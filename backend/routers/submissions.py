import os
"""
Exam Submission Router — Teacher workflow (M1 complete)
Steps: confirm date → exam type → upload/create → submit → admin approve → release
"""
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
import models
from academic_groups import build_course_group_clause
from auth_utils import (get_current_user, require_admin, get_effective_role,
                        log_action, is_view_all_role, get_dept_filter)
from exam_ownership import (
    get_active_exam_period,
    get_teacher_owned_section_ids,
    teacher_has_section_access,
)
from routers.settings import get_setting, is_past_deadline
from services.submission_service import (
    snapshot_submission as _snapshot_submission_svc,
    save_version as _save_version_svc,
    get_print_priority as _get_print_priority_svc,
    upsert_print_queue_job as _upsert_print_queue_job_svc,
)
from datetime import datetime, timedelta, timezone
import secrets, hashlib, os, json

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads", "exam_files")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── Schemas ───────────────────────────────────────────────────
class Step1Confirm(BaseModel):
    section_id: int

class Step2ExamType(BaseModel):
    section_id: int
    exam_type_choice: models.ExamTypeChoice
    answer_formats: Optional[List[models.AnswerFormat]] = None
    a4_pages_count: Optional[int] = 0

class Step3Metadata(BaseModel):
    section_id: int
    no_cover_page_confirmed: bool = False
    is_shared_exam: bool = False
    shared_with_sections: Optional[List[int]] = None

class SubmitRequest(BaseModel):
    section_id: int

class ApproveRequest(BaseModel):
    submission_id: int
    approve: bool
    reason: Optional[str] = None

class MessageCreate(BaseModel):
    message: str


# ── Helpers ───────────────────────────────────────────────────
def _get_submission(db, section_id, user, create_if_missing=True):
    effective = get_effective_role(user)
    sub = db.query(models.ExamSubmission).filter(
        models.ExamSubmission.section_id == section_id
    ).first()

    if not sub and create_if_missing:
        # Verify ownership
        section = db.query(models.Section).filter(
            models.Section.id == section_id
        ).first()
        if not section:
            raise HTTPException(404, "ไม่พบ section")
        if effective == models.UserRole.teacher and not teacher_has_section_access(db, user, section):
            raise HTTPException(403, "คุณไม่มีสิทธิ์จัดการ section นี้")

        sub = models.ExamSubmission(
            section_id=section_id,
            submitted_by=user.id,
            status=models.SubmissionStatus.draft,
        )
        db.add(sub)
        db.flush()

    return sub


def _snapshot_submission(sub: models.ExamSubmission) -> dict:
    return _snapshot_submission_svc(sub)


def _save_version(db, sub, user, reason=""):
    _save_version_svc(db, sub, user, reason)


def _get_print_priority(submission: models.ExamSubmission) -> str:
    return _get_print_priority_svc(submission)


def _upsert_print_queue_job(
    db: Session,
    submission: models.ExamSubmission,
    created_by: models.User,
    release_token: str,
):
    return _upsert_print_queue_job_svc(db, submission, created_by, release_token)


def _resolve_submission_pdf_path(submission: models.ExamSubmission) -> str:
    for candidate in (submission.pdf_stripped_path, submission.pdf_original_path):
        if candidate and os.path.exists(candidate):
            return candidate
    raise HTTPException(404, "เนเธกเนเธเธเนเธเธฅเน")


def _build_submission_filename(submission: models.ExamSubmission) -> str:
    section = submission.section
    course = section.course if section else None
    course_code = (course.course_id if course and course.course_id else f"submission-{submission.id}").replace("/", "-")
    section_no = (section.section_no if section and section.section_no else "unknown").replace("/", "-")
    return f"{course_code}_section-{section_no}.pdf"


def _load_valid_access_token(
    db: Session,
    token: str,
    current_user: models.User,
) -> models.ExamAccessToken:
    access_token = db.query(models.ExamAccessToken).options(
        joinedload(models.ExamAccessToken.submission)
            .joinedload(models.ExamSubmission.section)
            .joinedload(models.Section.course)
    ).filter(
        models.ExamAccessToken.token == token,
        models.ExamAccessToken.revoked == False,
    ).first()

    if not access_token:
        raise HTTPException(403, "Token เนเธกเนเธ–เธนเธเธ•เนเธญเธ")
    if access_token.issued_to != current_user.id:
        raise HTTPException(403, "Token เธเธตเนเนเธกเนเนเธเนเธเธญเธเธเธธเธ“")
    if datetime.now(timezone.utc) > access_token.expires_at:
        raise HTTPException(403, "Token เธซเธกเธ”เธญเธฒเธขเธธ")
    if access_token.use_count >= access_token.max_uses:
        raise HTTPException(403, "Token เนเธเนเธเธฃเธเนเธฅเนเธง")
    return access_token


# ── Get submission status ──────────────────────────────────────
@router.get("/section/{section_id}")
def get_submission(
    section_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    effective = get_effective_role(current_user)
    sub = db.query(models.ExamSubmission).options(
        joinedload(models.ExamSubmission.section)
            .joinedload(models.Section.course),
        joinedload(models.ExamSubmission.submitter),
        joinedload(models.ExamSubmission.versions),
    ).filter(models.ExamSubmission.section_id == section_id).first()

    if not sub:
        return {"exists": False, "section_id": section_id}

    # Teachers only see their own
    if effective == models.UserRole.teacher:
        section = db.query(models.Section).filter(
            models.Section.id == section_id
        ).first()
        if section and not teacher_has_section_access(db, current_user, section):
            raise HTTPException(403, "ไม่มีสิทธิ์ดู submission นี้")

    return {
        "exists": True,
        "id": sub.id,
        "section_id": sub.section_id,
        "status": sub.status,
        "version": sub.version,
        "date_confirmed": sub.date_confirmed,
        "exam_type_choice": sub.exam_type_choice,
        "answer_formats": sub.answer_formats,
        "a4_pages_count": sub.a4_pages_count,
        "has_uploaded_pdf": sub.has_uploaded_pdf,
        "no_cover_page_confirmed": sub.no_cover_page_confirmed,
        "is_shared_exam": sub.is_shared_exam,
        "shared_with_sections": sub.shared_with_sections,
        "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None,
        "approved_at": sub.approved_at.isoformat() if sub.approved_at else None,
        "rejected_reason": sub.rejected_reason,
        "admin_note": sub.admin_note,
        "course_name": sub.section.course.course_name_th if sub.section and sub.section.course else None,
        "versions": [
            {"version": v.version, "created_at": v.created_at.isoformat(),
             "reason": v.change_reason}
            for v in (sub.versions or [])
        ],
    }


@router.get("/")
def list_submissions(
    status:  Optional[str] = None,
    page:    int = 1,
    limit:   int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if limit > 200:
        limit = 200
    if page < 1:
        page = 1
    effective   = get_effective_role(current_user)
    dept_filter = get_dept_filter(current_user)
    q = db.query(models.ExamSubmission).join(
        models.Section,
        models.ExamSubmission.section_id == models.Section.id
    ).options(
        joinedload(models.ExamSubmission.section)
            .joinedload(models.Section.course),
        joinedload(models.ExamSubmission.submitter),
    )

    if effective == models.UserRole.teacher:
        active_period = get_active_exam_period(db)
        if active_period:
            owned_section_ids, _ = get_teacher_owned_section_ids(
                db,
                current_user.id,
                active_period.semester,
                active_period.academic_year,
            )
            if owned_section_ids is None:
                q = q.filter(models.Section.teacher_id == current_user.id)
            elif not owned_section_ids:
                return []
            else:
                q = q.filter(models.Section.id.in_(owned_section_ids))
        else:
            q = q.filter(models.Section.teacher_id == current_user.id)
    elif effective == models.UserRole.dept_supervisor:
        group_clause = build_course_group_clause(models.Course.course_id, dept_filter)
        if group_clause is None:
            return []
        q = q.join(models.Course, models.Section.course_id == models.Course.id).filter(group_clause)

    if status:
        q = q.filter(models.ExamSubmission.status == status)

    subs = q.order_by(models.ExamSubmission.updated_at.desc()).all()
    return [
        {
            "id": s.id,
            "section_id": s.section_id,
            "course_id": s.section.course.course_id if s.section and s.section.course else None,
            "course_name": s.section.course.course_name_th if s.section and s.section.course else None,
            "section_no": s.section.section_no if s.section else None,
            "status": s.status,
            "version": s.version,
            "exam_type_choice": s.exam_type_choice,
            "has_uploaded_pdf": s.has_uploaded_pdf,
            "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
            "submitter": s.submitter.full_name if s.submitter else None,
        }
        for s in subs
    ]


# ── Step 1: Confirm date ───────────────────────────────────────
def _require_not_readonly(user):
    """Block esq_head + secretary จาก write operations"""
    if is_view_all_role(user):
        raise HTTPException(403,
            "บัญชีนี้มีสิทธิ์ดูอย่างเดียว — ไม่สามารถแก้ไขได้")

@router.post("/step1-confirm")
def step1_confirm_date(
    data: Step1Confirm,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    _require_not_readonly(current_user)
    if is_past_deadline(db, "exam_submission_deadline"):
        raise HTTPException(400, "เลยกำหนดส่งข้อสอบแล้ว")

    sub = _get_submission(db, data.section_id, current_user)
    if sub.status in (models.SubmissionStatus.approved, models.SubmissionStatus.released):
        raise HTTPException(400, "ข้อสอบ approved แล้ว — ติดต่อ admin")

    sub.date_confirmed = True
    sub.date_confirmed_at = datetime.now(timezone.utc)
    _save_version(db, sub, current_user, "ยืนยันวันสอบ")
    db.commit()
    log_action(db, current_user, "EXAM_CONFIRM_DATE", "exam_submissions",
               sub.id, request=request)
    return {"success": True, "step": 1, "next": "step2-exam-type"}


# ── Step 2: Exam type ──────────────────────────────────────────
@router.post("/step2-exam-type")
def step2_exam_type(
    data: Step2ExamType,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    _require_not_readonly(current_user)
    if is_view_all_role(current_user):
        raise HTTPException(403, "บัญชีนี้มีสิทธิ์อ่านอย่างเดียว")
    if is_past_deadline(db, "exam_submission_deadline"):
        raise HTTPException(400, "เลยกำหนดส่งข้อสอบแล้ว")

    sub = _get_submission(db, data.section_id, current_user, create_if_missing=False)
    if not sub:
        raise HTTPException(400, "กรุณายืนยันวันสอบก่อน (Step 1)")
    if not sub.date_confirmed:
        raise HTTPException(400, "กรุณายืนยันวันสอบก่อน (Step 1)")

    sub.exam_type_choice = data.exam_type_choice
    sub.answer_formats   = [f for f in (data.answer_formats or [])]
    sub.a4_pages_count   = data.a4_pages_count or 0
    _save_version(db, sub, current_user, f"เลือกประเภท {data.exam_type_choice}")
    db.commit()
    log_action(db, current_user, "EXAM_SET_TYPE", "exam_submissions",
               sub.id, request=request)

    # no_exam / online / outside / in_class → ไม่ต้องส่งไฟล์
    needs_file = data.exam_type_choice == models.ExamTypeChoice.onsite
    return {
        "success": True,
        "step": 2,
        "needs_file": needs_file,
        "next": "step3-upload" if needs_file else "submit",
    }


# ── Step 3a: Upload PDF ────────────────────────────────────────
@router.post("/step3-upload/{section_id}")
async def step3_upload_pdf(
    section_id: int,
    no_cover_page_confirmed: bool,
    is_shared_exam: bool = False,
    file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    _require_not_readonly(current_user)
    if is_view_all_role(current_user):
        raise HTTPException(403, "บัญชีนี้มีสิทธิ์อ่านอย่างเดียว")
    if is_past_deadline(db, "exam_submission_deadline"):
        raise HTTPException(400, "เลยกำหนดส่งข้อสอบแล้ว")

    sub = _get_submission(db, section_id, current_user, create_if_missing=False)
    if not sub or not sub.exam_type_choice:
        raise HTTPException(400, "กรุณาเลือกประเภทข้อสอบก่อน (Step 2)")

    # ── Validate file ──
    filename = (file.filename or "").strip().lower()
    allowed_content_types = {"application/pdf", "application/x-pdf"}
    if not filename.endswith(".pdf"):
        raise HTTPException(400, "รองรับเฉพาะไฟล์ .pdf เท่านั้น")
    if file.content_type and file.content_type.lower() not in allowed_content_types:
        raise HTTPException(400, "ชนิดไฟล์ไม่ถูกต้อง ต้องเป็น PDF เท่านั้น")
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(400, "ไฟล์ใหญ่เกิน 20MB")

    # Magic bytes check
    if not content.startswith(b"%PDF-"):
        raise HTTPException(400, "ไฟล์ไม่ใช่ PDF จริง (magic bytes ไม่ตรง)")

    # ── Save file (outside webroot) ──
    file_id = secrets.token_hex(16)
    raw_path = os.path.join(UPLOAD_DIR, f"{file_id}_raw.pdf")
    with open(raw_path, "wb") as f:
        f.write(content)

    # ── Strip PDF metadata ──
    stripped_path = os.path.join(UPLOAD_DIR, f"{file_id}_clean.pdf")
    try:
        import pikepdf
        with pikepdf.open(raw_path) as pdf:
            pdf.docinfo.clear()
            pdf.save(stripped_path)
    except ImportError:
        # pikepdf ไม่ได้ติดตั้ง — ใช้ raw file แทน
        stripped_path = raw_path

    sub.has_uploaded_pdf         = True
    sub.pdf_original_path        = raw_path
    sub.pdf_stripped_path        = stripped_path
    sub.no_cover_page_confirmed  = no_cover_page_confirmed
    sub.is_shared_exam           = is_shared_exam
    _save_version(db, sub, current_user, "อัปโหลด PDF")
    db.commit()
    log_action(db, current_user, "EXAM_UPLOAD_PDF", "exam_submissions",
               sub.id, request=request)
    return {"success": True, "step": 3, "next": "submit"}


# ── Submit for review ──────────────────────────────────────────
@router.post("/submit")
def submit_for_review(
    data: SubmitRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    _require_not_readonly(current_user)
    if is_past_deadline(db, "exam_submission_deadline"):
        raise HTTPException(400, "เลยกำหนดส่งข้อสอบแล้ว")

    sub = _get_submission(db, data.section_id, current_user, create_if_missing=False)
    if not sub:
        raise HTTPException(400, "ไม่พบ submission")
    if not sub.date_confirmed:
        raise HTTPException(400, "กรุณายืนยันวันสอบก่อน")
    if not sub.exam_type_choice:
        raise HTTPException(400, "กรุณาเลือกประเภทข้อสอบก่อน")

    # Onsite ต้องมีไฟล์
    if (sub.exam_type_choice == models.ExamTypeChoice.onsite
            and not sub.has_uploaded_pdf
            and not sub.questions):
        raise HTTPException(400, "ข้อสอบ Onsite ต้องอัปโหลดไฟล์หรือสร้างข้อสอบในระบบ")

    # ต้องมี print spec (step 4) สำหรับ onsite เท่านั้น
    if (sub.exam_type_choice == models.ExamTypeChoice.onsite
            and not sub.print_spec_confirmed):
        raise HTTPException(400, "กรุณากำหนดสเปคการพิมพ์ก่อนส่ง (ขั้น 4)")

    sub.status = models.SubmissionStatus.submitted
    sub.submitted_at = datetime.now(timezone.utc)
    _save_version(db, sub, current_user, "ส่งข้อสอบ")
    db.commit()
    log_action(db, current_user, "EXAM_SUBMIT", "exam_submissions",
               sub.id, request=request)
    return {"success": True, "status": "submitted"}


# ── Admin: approve / reject ────────────────────────────────────
@router.post("/approve")
def approve_submission(
    data: ApproveRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    sub = db.query(models.ExamSubmission).filter(
        models.ExamSubmission.id == data.submission_id
    ).first()
    if not sub:
        raise HTTPException(404, "ไม่พบ submission")
    if sub.status != models.SubmissionStatus.submitted:
        raise HTTPException(400, "ต้อง status=submitted ก่อน approve")

    if data.approve:
        sub.status      = models.SubmissionStatus.approved
        sub.approved_by = current_user.id
        sub.approved_at = datetime.now(timezone.utc)
        action = "EXAM_APPROVE"
    else:
        sub.status          = models.SubmissionStatus.rejected
        sub.rejected_reason = data.reason
        action = "EXAM_REJECT"

    _save_version(db, sub, current_user,
                  "อนุมัติ" if data.approve else f"ปฏิเสธ: {data.reason}")
    db.commit()
    log_action(db, current_user, action, "exam_submissions",
               sub.id, request=request)

    # Email notification (no-op ถ้าไม่มี SMTP config)
    try:
        from email_notifications import notify_submission_approved, notify_submission_rejected
        teacher = sub.submitter
        sec     = sub.section
        course_id_str = sec.course.course_id if sec and sec.course else "?"
        section_no    = sec.section_no if sec else "?"
        if teacher and teacher.email:
            if data.approve:
                notify_submission_approved(teacher.email, teacher.full_name or "",
                                           course_id_str, section_no, "final")
            else:
                notify_submission_rejected(teacher.email, teacher.full_name or "",
                                           course_id_str, section_no, "final",
                                           data.reason or "")
    except Exception:
        pass  # email fail ไม่กระทบ main flow

    return {"success": True, "status": sub.status}


# ── Admin: release to printshop ───────────────────────────────
@router.post("/{submission_id}/release")
def release_to_printshop(
    submission_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    sub = db.query(models.ExamSubmission).filter(
        models.ExamSubmission.id == submission_id
    ).first()
    if not sub:
        raise HTTPException(404, "ไม่พบ submission")
    if sub.status != models.SubmissionStatus.approved:
        raise HTTPException(400, "ต้อง approve ก่อน release")
    if not sub.pdf_stripped_path or not os.path.exists(sub.pdf_stripped_path):
        raise HTTPException(400, "ไม่พบไฟล์ PDF")

    # สร้าง token สำหรับ printshop
    token_str = secrets.token_hex(32)
    token = models.ExamAccessToken(
        token         = token_str,
        submission_id = sub.id,
        issued_to     = current_user.id,
        purpose       = models.TokenPurpose.print,
        max_uses      = 1,
        expires_at    = datetime.now(timezone.utc) + timedelta(
            hours=int(os.getenv("PRINTSHOP_TOKEN_HOURS", "72"))  # default 3 วัน
        ),
    )
    db.add(token)
    _upsert_print_queue_job(db, sub, current_user, token_str)
    sub.status = models.SubmissionStatus.released
    _save_version(db, sub, current_user, "release ให้ printshop")
    db.commit()
    log_action(db, current_user, "EXAM_RELEASE", "exam_submissions",
               sub.id, request=request)
    return {
        "success": True,
        "printshop_token": token_str,
        "expires_in": "72 hours",
        "max_uses": 1,
    }


# ── Version history ────────────────────────────────────────────
@router.get("/{submission_id}/versions")
def get_versions(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    versions = db.query(models.ExamSubmissionVersion).filter(
        models.ExamSubmissionVersion.submission_id == submission_id
    ).order_by(models.ExamSubmissionVersion.version.desc()).all()

    return [
        {
            "version": v.version,
            "snapshot": v.snapshot,
            "changed_by": v.changer.full_name if v.changer else None,
            "change_reason": v.change_reason,
            "created_at": v.created_at.isoformat(),
        }
        for v in versions
    ]


@router.post("/{submission_id}/rollback/{version}")
def rollback_version(
    submission_id: int,
    version: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    ver = db.query(models.ExamSubmissionVersion).filter(
        models.ExamSubmissionVersion.submission_id == submission_id,
        models.ExamSubmissionVersion.version == version,
    ).first()
    if not ver:
        raise HTTPException(404, "ไม่พบ version")

    sub = db.query(models.ExamSubmission).filter(
        models.ExamSubmission.id == submission_id
    ).first()

    snap = ver.snapshot
    sub.date_confirmed           = snap.get("date_confirmed", False)
    sub.exam_type_choice         = snap.get("exam_type_choice")
    sub.answer_formats           = snap.get("answer_formats")
    sub.a4_pages_count           = snap.get("a4_pages_count", 0)
    sub.no_cover_page_confirmed  = snap.get("no_cover_page_confirmed", False)
    sub.is_shared_exam           = snap.get("is_shared_exam", False)
    sub.status                   = models.SubmissionStatus.draft  # reset to draft
    _save_version(db, sub, current_user, f"rollback to version {version}")
    db.commit()
    log_action(db, current_user, "EXAM_ROLLBACK", "exam_submissions",
               sub.id, new_values={"rollback_to": version}, request=request)
    return {"success": True, "rolled_back_to": version}


# ── Secure file access (view/download) ────────────────────────
@router.post("/{submission_id}/request-access")
def request_file_access(
    submission_id: int,
    purpose: models.TokenPurpose,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    effective = get_effective_role(current_user)
    sub = db.query(models.ExamSubmission).options(
        joinedload(models.ExamSubmission.section)
    ).filter(models.ExamSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(404, "ไม่พบ submission")

    # Permission check
    can_download = effective in (models.UserRole.admin, models.UserRole.teacher)
    can_view     = can_download  # + edu-sq handled via role check

    # Teacher: only their own
    if effective == models.UserRole.teacher:
        if not teacher_has_section_access(db, current_user, sub.section):
            raise HTTPException(403, "ไม่มีสิทธิ์เข้าถึงไฟล์นี้")

    if purpose == models.TokenPurpose.download and not can_download:
        raise HTTPException(403, "role นี้ไม่สามารถ download ได้")

    if sub.status not in (
        models.SubmissionStatus.approved,
        models.SubmissionStatus.released
    ):
        raise HTTPException(400, "ไฟล์ยังไม่ได้รับการอนุมัติ")

    # สร้าง token
    max_uses = 5 if purpose == models.TokenPurpose.view else 1
    token_str = secrets.token_hex(32)
    ip = request.client.host if request.client else "unknown"
    token = models.ExamAccessToken(
        token         = token_str,
        submission_id = sub.id,
        issued_to     = current_user.id,
        purpose       = purpose,
        max_uses      = max_uses,
        ip_hash       = hashlib.sha256(ip.encode()).hexdigest()[:16],
        expires_at    = datetime.now(timezone.utc) + timedelta(hours=2),
    )
    db.add(token)
    db.commit()
    log_action(db, current_user, "EXAM_REQUEST_ACCESS", "exam_submissions",
               sub.id, new_values={"purpose": purpose}, request=request)
    return {
        "token": token_str,
        "purpose": purpose,
        "expires_in": "2 hours",
        "max_uses": max_uses,
        "access_url": f"/api/submissions/access/{token_str}",
        "content_url": f"/api/submissions/access/{token_str}/content",
    }


@router.get("/access/{token}")
def access_exam_file(
    token: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    access_token = _load_valid_access_token(db, token, current_user)
    submission = access_token.submission
    _resolve_submission_pdf_path(submission)

    watermark = (
        f"{current_user.full_name or current_user.username} | "
        f"{current_user.email} | "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}"
    )

    response = JSONResponse(
        {
            "purpose": access_token.purpose.value,
            "can_download": access_token.purpose in (models.TokenPurpose.download, models.TokenPurpose.print),
            "submission_id": submission.id,
            "watermark": watermark,
            "remaining_uses": max(access_token.max_uses - access_token.use_count, 0),
            "expires_at": access_token.expires_at.isoformat() if access_token.expires_at else None,
            "content_url": f"/api/submissions/access/{token}/content",
        }
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@router.get("/access/{token}/content")
def stream_exam_file(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    access_token = _load_valid_access_token(db, token, current_user)
    submission = access_token.submission
    file_path = _resolve_submission_pdf_path(submission)

    ip = request.client.host if request.client else "unknown"
    watermark = (
        f"{current_user.full_name or current_user.username} | "
        f"{current_user.email} | "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}"
    )
    action = {
        models.TokenPurpose.view: "viewed",
        models.TokenPurpose.download: "downloaded",
        models.TokenPurpose.print: "printed",
    }.get(access_token.purpose, "viewed")
    log = models.ExamAccessLog(
        token_id=access_token.id,
        user_id=current_user.id,
        action=action,
        ip_hash=hashlib.sha256(ip.encode()).hexdigest()[:16],
        watermark_text=watermark,
    )
    db.add(log)
    access_token.use_count += 1
    db.commit()

    filename = _build_submission_filename(submission)
    response = FileResponse(file_path, media_type="application/pdf", filename=filename)
    if access_token.purpose == models.TokenPurpose.view:
        response.headers["Content-Disposition"] = f'inline; filename="{filename}"'
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-EMS-Watermark"] = watermark
    return response


# ── Messages: Teacher ↔ Admin ──────────────────────────────────

def _assert_message_access(db: Session, submission_id: int, user: models.User):
    """Raise 403/404 if user cannot access messages for this submission.
    Teachers: only their own. Admin/esq_head/secretary/dept_supervisor: all."""
    effective = get_effective_role(user)
    sub = db.query(models.ExamSubmission).options(
        joinedload(models.ExamSubmission.section)
    ).filter(models.ExamSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(404, "ไม่พบ submission")
    if effective == models.UserRole.teacher:
        section = sub.section
        if not section or not teacher_has_section_access(db, user, section):
            raise HTTPException(403, "ไม่มีสิทธิ์เข้าถึง submission นี้")
    elif effective == models.UserRole.staff:
        # staff ไม่มีสิทธิ์อ่าน/เขียน messages
        raise HTTPException(403, "role นี้ไม่มีสิทธิ์ดู messages")
    return sub


@router.get("/{submission_id}/messages")
def get_messages(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    _assert_message_access(db, submission_id, current_user)
    msgs = db.query(models.ExamMessage).options(
        joinedload(models.ExamMessage.sender)
    ).filter(
        models.ExamMessage.submission_id == submission_id
    ).order_by(models.ExamMessage.created_at).all()
    return [
        {
            "id": m.id,
            "sender": m.sender.full_name if m.sender else "—",
            "sender_role": m.sender.role if m.sender else None,
            "message": m.message,
            "is_read": m.is_read,
            "created_at": m.created_at.isoformat(),
        }
        for m in msgs
    ]


@router.post("/{submission_id}/messages")
def send_message(
    submission_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    _assert_message_access(db, submission_id, current_user)
    if not data.message or not data.message.strip():
        raise HTTPException(400, "ข้อความไม่ควรว่าง")
    if len(data.message) > 2000:
        raise HTTPException(400, "ข้อความยาวเกิน 2000 ตัวอักษร")
    msg = models.ExamMessage(
        submission_id=submission_id,
        sender_id=current_user.id,
        message=data.message.strip(),
    )
    db.add(msg)
    db.commit()
    return {"success": True}


# ── Step 4 — Print Specifications ────────────────────────────
class Step4PrintSpec(BaseModel):
    section_id:          int
    print_duplex:        bool = False          # หน้า-หลัง
    print_staple:        str  = "none"         # none | corner_left | side_left | custom
    print_staple_page:   Optional[int] = None  # เย็บแยกที่หน้าที่ X
    print_note:          Optional[str] = None  # หมายเหตุร้านถ่าย


@router.post("/step4-print-spec")
def step4_print_spec(
    data: Step4PrintSpec,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """อาจารย์กำหนดสเปคการพิมพ์ (ทำหลัง upload PDF)"""
    effective = get_effective_role(current_user)
    if is_view_all_role(current_user):
        raise HTTPException(403, "บัญชีนี้มีสิทธิ์อ่านอย่างเดียว")
    sub = _get_submission(db, data.section_id, current_user, create_if_missing=False)
    if not sub:
        raise HTTPException(404, "ไม่พบ submission")
    if sub.status in (models.SubmissionStatus.approved, models.SubmissionStatus.released):
        raise HTTPException(400, "ไม่สามารถแก้ไขได้ — submission ถูก approve แล้ว")
    if effective == models.UserRole.teacher and not teacher_has_section_access(db, current_user, sub.section):
        raise HTTPException(403, "ไม่มีสิทธิ์")

    valid_staple = {"none", "corner_left", "side_left", "custom"}
    if data.print_staple not in valid_staple:
        raise HTTPException(400, f"print_staple ต้องเป็น {valid_staple}")

    sub.print_duplex         = data.print_duplex
    sub.print_staple         = data.print_staple
    sub.print_staple_page    = data.print_staple_page
    sub.print_note           = data.print_note
    sub.print_spec_confirmed = True

    db.commit()
    log_action(db, current_user, "STEP4_PRINT_SPEC", "exam_submissions",
               record_id=sub.id,
               new_values={"duplex": data.print_duplex, "staple": data.print_staple,
                           "staple_page": data.print_staple_page, "note": data.print_note},
               request=request)

    return {
        "status":       "ok",
        "print_duplex": sub.print_duplex,
        "print_staple": sub.print_staple,
        "print_staple_page": sub.print_staple_page,
        "print_note":   sub.print_note,
        "print_spec_confirmed": True,
    }
