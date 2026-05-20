"""
Exam Manager Router — จัดการผู้รับผิดชอบสอบ + สิ่งเพิ่มเติม

POST /api/exam-manager/propose          อาจารย์เสนอตัว / เสนอคนอื่นเป็น manager
POST /api/exam-manager/{id}/confirm     อาจารย์อีกคน confirm หรือ admin assign
POST /api/exam-manager/{id}/reassign    เปลี่ยนผู้รับผิดชอบ (admin)
GET  /api/exam-manager/pending          รายการรอ confirm ของฉัน
GET  /api/exam-manager/section/{sid}    ดู managers ของ section นี้
GET  /api/exam-manager/overview         ภาพรวมทุก section (admin)

POST /api/exam-manager/materials/{sub_id}  กรอกสิ่งที่ต้องการเพิ่มเติม
GET  /api/exam-manager/materials/{sub_id}  ดูรายการที่กรอกไว้
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from database import get_db
import models
from academic_groups import build_course_group_clause, can_access_academic_group, normalize_academic_group_code
from auth_utils import (
    require_admin,
    require_dept_or_admin,
    get_current_user,
    log_action,
    get_effective_role,
    get_dept_filter,
    is_view_all_role,
    assert_dept_access,
)
from services.permission_service import can_manage_schedule, can_impersonate_admin
from exam_ownership import (
    OWNER_SOURCE_AUTO,
    OWNER_SOURCE_MANUAL,
    build_owner_map,
    get_assignment_status,
    get_teacher_owned_section_ids,
    normalize_owner_exam_type,
    upsert_section_owner,
)

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────
class ProposeManagerRequest(BaseModel):
    section_id:  int
    exam_type:   str          # "midterm" | "final"
    manager_id:  Optional[int] = None   # None = เสนอตัวเอง
    note:        Optional[str] = None


class SectionOwnershipUpdateRequest(BaseModel):
    midterm_manager_id: Optional[int] = None
    final_manager_id: Optional[int] = None
    note: Optional[str] = None


class MaterialRequest(BaseModel):
    answer_paper_sheets:  int  = 0
    answer_paper_staple:  bool = False
    answer_booklet_count: int  = 0
    omr_sheet_count:      int  = 0
    omr_form_code:        Optional[str] = None
    scratch_paper_sheets: int  = 0
    special_note:         Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────
def _can_manage_section(db, user: models.User, section: models.Section) -> bool:
    """
    ตรวจว่า user มีสิทธิ์จัดการ exam ของ section นี้:
    - admin                → ทุก section
    - esq_head / secretary → ❌ read-only (ห้าม manage)
    - dept_supervisor      → เฉพาะ sections ที่ teacher.dept_code == ตัวเอง
    - teacher              → เฉพาะ section ที่ตัวเองเป็น main teacher หรือ co-teacher (dept เดียวกัน)
    """
    if user.role == models.UserRole.admin:
        return True
    # esq_head + secretary — read-only
    if is_view_all_role(user):
        return False
    # dept_supervisor — จัดการได้เฉพาะแผนกตัวเอง
    if user.role == models.UserRole.dept_supervisor:
        return can_access_academic_group(user.dept_code, _section_department_code(section))
    # teacher — main teacher หรือ co-teacher (dept เดียวกัน)
    if section.teacher_id == user.id:
        return True
    main_teacher = db.query(models.User).filter(
        models.User.id == section.teacher_id
    ).first() if section.teacher_id else None
    if (
        main_teacher
        and normalize_academic_group_code(user.dept_code)
        and can_access_academic_group(user.dept_code, main_teacher.dept_code)
    ):
        return True
    return False


def _manager_dict(em: models.SectionExamManager) -> dict:
    return {
        "id":           em.id,
        "section_id":   em.section_id,
        "exam_type":    normalize_owner_exam_type(em.exam_type),
        "manager_id":   em.manager_id,
        "manager_name": em.manager.full_name if em.manager else None,
        "proposed_by":  em.proposed_by,
        "proposer_name":em.proposer.full_name if em.proposer else None,
        "confirmed":    em.confirmed,
        "confirmed_by": em.confirmed_by,
        "confirmer_name":em.confirmer.full_name if em.confirmer else None,
        "confirmed_at": em.confirmed_at.isoformat() if em.confirmed_at else None,
        "assignment_source": em.assignment_source or OWNER_SOURCE_MANUAL,
        "assignment_status": get_assignment_status(em),
        "note":         em.note,
    }


def _teacher_dict(user: models.User | None) -> dict | None:
    if not user:
        return None
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "dept_code": normalize_academic_group_code(user.dept_code),
    }


def _material_dict(mat: models.ExamMaterialRequest) -> dict:
    return {
        "id":                   mat.id,
        "submission_id":        mat.submission_id,
        "answer_paper_sheets":  mat.answer_paper_sheets,
        "answer_paper_staple":  mat.answer_paper_staple,
        "answer_booklet_count": mat.answer_booklet_count,
        "omr_sheet_count":      mat.omr_sheet_count,
        "omr_form_code":        mat.omr_form_code,
        "scratch_paper_sheets": mat.scratch_paper_sheets,
        "special_note":         mat.special_note,
        "confirmed":            mat.confirmed,
        "confirmed_at":         mat.confirmed_at.isoformat() if mat.confirmed_at else None,
        # คำนวณรวมต่อคน
        "items_per_student": {
            "answer_paper":  mat.answer_paper_sheets,
            "booklet":       mat.answer_booklet_count,
            "omr":           mat.omr_sheet_count,
            "scratch":       mat.scratch_paper_sheets,
        }
    }


def _section_department_code(section: models.Section) -> str | None:
    if section.course and section.course.academic_group:
        return section.course.academic_group
    if section.teacher and section.teacher.dept_code:
        return normalize_academic_group_code(section.teacher.dept_code)
    if section.course and section.course.department:
        return normalize_academic_group_code(section.course.department)
    return None


def _validate_teacher_candidate(
    db: Session,
    teacher_id: int | None,
    *,
    dept_code: str | None = None,
    section_group: str | None = None,
) -> models.User | None:
    if teacher_id is None:
        return None

    teacher = db.query(models.User).filter(
        models.User.id == teacher_id,
        models.User.role == models.UserRole.teacher,
        models.User.is_active == True,
    ).first()
    if not teacher:
        raise HTTPException(400, "Responsible teacher must be an active teacher account.")
    normalized_dept_code = normalize_academic_group_code(dept_code)
    normalized_teacher_group = normalize_academic_group_code(teacher.dept_code)
    normalized_section_group = normalize_academic_group_code(section_group)
    if (
        normalized_dept_code
        and normalized_section_group != "ALL"
        and normalized_teacher_group != normalized_dept_code
    ):
        raise HTTPException(400, "Department supervisors can assign teachers only within their own department.")
    return teacher


# ══════════════════════════════════════════════════════════════
# EXAM MANAGER — co-teacher designation
# ══════════════════════════════════════════════════════════════

@router.put("/section/{section_id}/ownership")
def update_section_ownership(
    section_id: int,
    data: SectionOwnershipUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_dept_or_admin),
):
    section = db.query(models.Section).options(
        joinedload(models.Section.course),
        joinedload(models.Section.teacher),
    ).filter(models.Section.id == section_id).first()
    if not section:
        raise HTTPException(404, "ไม่พบ section")

    dept_scope = normalize_academic_group_code(current_user.dept_code) if current_user.role == models.UserRole.dept_supervisor else None
    section_dept = _section_department_code(section)
    if dept_scope:
        if not section_dept:
            raise HTTPException(400, "This section has no department scope for supervisor assignment.")
        assert_dept_access(current_user, section_dept)

    midterm_teacher = _validate_teacher_candidate(
        db,
        data.midterm_manager_id,
        dept_code=dept_scope,
        section_group=section_dept,
    )
    final_teacher = _validate_teacher_candidate(
        db,
        data.final_manager_id,
        dept_code=dept_scope,
        section_group=section_dept,
    )

    old_rows = db.query(models.SectionExamManager).options(
        joinedload(models.SectionExamManager.manager),
        joinedload(models.SectionExamManager.proposer),
        joinedload(models.SectionExamManager.confirmer),
    ).filter(
        models.SectionExamManager.section_id == section_id,
        models.SectionExamManager.exam_type.in_(["midterm", "final"]),
    ).all()
    old_values = {row.exam_type: _manager_dict(row) for row in old_rows}

    upsert_section_owner(
        db,
        section=section,
        exam_type="midterm",
        manager_id=midterm_teacher.id if midterm_teacher else None,
        actor_id=current_user.id,
        note=data.note,
        assignment_source=OWNER_SOURCE_MANUAL,
    )
    upsert_section_owner(
        db,
        section=section,
        exam_type="final",
        manager_id=final_teacher.id if final_teacher else None,
        actor_id=current_user.id,
        note=data.note,
        assignment_source=OWNER_SOURCE_MANUAL,
    )
    db.commit()

    updated_rows = db.query(models.SectionExamManager).options(
        joinedload(models.SectionExamManager.manager),
        joinedload(models.SectionExamManager.proposer),
        joinedload(models.SectionExamManager.confirmer),
    ).filter(
        models.SectionExamManager.section_id == section_id,
        models.SectionExamManager.exam_type.in_(["midterm", "final"]),
    ).all()
    new_values = {row.exam_type: _manager_dict(row) for row in updated_rows}

    log_action(
        db,
        current_user,
        "UPDATE_SECTION_OWNERSHIP",
        "section_exam_managers",
        record_id=section_id,
        old_values=old_values,
        new_values=new_values,
        request=request,
    )

    return {
        "section_id": section_id,
        "midterm": next((_manager_dict(row) for row in updated_rows if row.exam_type == "midterm"), None),
        "final": next((_manager_dict(row) for row in updated_rows if row.exam_type == "final"), None),
        "complete": len(updated_rows) == 2 and all(row.confirmed for row in updated_rows),
        "message": "Ownership assignments updated.",
    }

@router.post("/propose")
def propose_manager(
    data: ProposeManagerRequest,
    request: Request,
    db:   Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    เสนอผู้รับผิดชอบสอบ:
    - อาจารย์เสนอตัวเอง → รอ admin confirm (หรือ auto-confirm ถ้าไม่มีคนอื่น)
    - อาจารย์เสนอคนอื่น → คนนั้นต้อง confirm
    - Admin เสนอใครก็ได้ → auto-confirmed
    """
    section = db.query(models.Section).options(
        joinedload(models.Section.course)
    ).filter(models.Section.id == data.section_id).first()
    if not section:
        raise HTTPException(404, "ไม่พบ section")

    eff = get_effective_role(current_user)
    is_admin = can_impersonate_admin(current_user)

    # esq_head + secretary = read-only
    if is_view_all_role(current_user):
        raise HTTPException(403, "บัญชีนี้มีสิทธิ์อ่านอย่างเดียว")

    # ตรวจสิทธิ์: main teacher, co-teacher (แผนกเดียวกัน), หรือ admin
    if not _can_manage_section(db, current_user, section):
        raise HTTPException(403, "คุณไม่ใช่อาจารย์ผู้รับผิดชอบ section นี้")

    if data.exam_type not in ("midterm", "final"):
        raise HTTPException(400, "exam_type ต้องเป็น midterm หรือ final")

    manager_id = data.manager_id or current_user.id

    # ตรวจว่า manager_id เป็น teacher
    manager = db.query(models.User).filter(
        models.User.id == manager_id,
        models.User.role == models.UserRole.teacher,
        models.User.is_active == True,
    ).first()
    if not manager:
        raise HTTPException(400, "ผู้รับผิดชอบต้องเป็นอาจารย์ที่ active")

    # ตรวจ duplicate
    existing = db.query(models.SectionExamManager).filter(
        and_(
            models.SectionExamManager.section_id == data.section_id,
            models.SectionExamManager.exam_type  == data.exam_type,
        )
    ).first()
    if existing:
        raise HTTPException(400,
            f"มีผู้รับผิดชอบ {data.exam_type} อยู่แล้ว ({existing.manager.full_name if existing.manager else '?'})"
            " — ใช้ PUT reassign ถ้าต้องการเปลี่ยน")

    # auto-confirm เฉพาะ admin
    # อาจารย์เสนอใครก็ต้องรอ confirm จาก:
    #   - main teacher (ถ้าไม่ใช่ผู้เสนอ)
    #   - หรือ admin
    auto_confirm = is_admin

    em = models.SectionExamManager(
        section_id  = data.section_id,
        exam_type   = data.exam_type,
        manager_id  = manager_id,
        proposed_by = current_user.id,
        confirmed   = auto_confirm,
        confirmed_by= current_user.id if auto_confirm else None,
        confirmed_at= datetime.now(timezone.utc) if auto_confirm else None,
        assignment_source=OWNER_SOURCE_AUTO if auto_confirm and manager_id == section.teacher_id else OWNER_SOURCE_MANUAL,
        note        = data.note,
    )
    db.add(em)
    db.commit()
    db.refresh(em)

    log_action(db, current_user, "PROPOSE_EXAM_MANAGER", "section_exam_managers",
               record_id=em.id,
               new_values={"section": data.section_id, "exam_type": data.exam_type,
                           "manager": manager.full_name, "auto_confirm": auto_confirm},
               request=request)

    # ถ้า auto-confirm → สร้าง/เชื่อม submission ทันที
    if auto_confirm:
        _ensure_submission(db, data.section_id, manager_id)

    result_em = db.query(models.SectionExamManager).options(
        joinedload(models.SectionExamManager.manager),
        joinedload(models.SectionExamManager.proposer),
    ).filter(models.SectionExamManager.id == em.id).first()

    # Email notification (no-op ถ้าไม่มี SMTP)
    if not auto_confirm and manager.email:
        try:
            from email_notifications import notify_confirm_manager
            course_id_str = section.course.course_id if section.course else "?"
            notify_confirm_manager(manager.email, manager.full_name or "",
                                   current_user.full_name or "",
                                   course_id_str, section.section_no,
                                   data.exam_type)
        except Exception:
            pass

    return {
        **_manager_dict(result_em),
        "message": "กำหนดผู้รับผิดชอบแล้ว ✅" if auto_confirm
                   else f"ส่งคำขอให้ {manager.full_name} confirm แล้ว",
    }


@router.post("/{manager_id}/confirm")
def confirm_manager(
    manager_id: int,
    request: Request,
    db:   Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    ยืนยันการรับผิดชอบ — เฉพาะคนที่ถูกเสนอชื่อ หรือ admin
    """
    em = db.query(models.SectionExamManager).options(
        joinedload(models.SectionExamManager.manager),
    ).filter(models.SectionExamManager.id == manager_id).first()
    if not em:
        raise HTTPException(404, "ไม่พบรายการ")
    if em.confirmed:
        raise HTTPException(400, "confirm แล้ว")

    is_admin  = current_user.role == models.UserRole.admin
    is_target = em.manager_id == current_user.id

    if not is_admin and not is_target:
        raise HTTPException(403, "เฉพาะผู้รับผิดชอบหรือ admin เท่านั้น")

    em.confirmed    = True
    em.confirmed_by = current_user.id
    em.confirmed_at = datetime.now(timezone.utc)
    db.commit()

    # สร้าง submission สำหรับ manager คนนี้
    _ensure_submission(db, em.section_id, em.manager_id)

    log_action(db, current_user, "CONFIRM_EXAM_MANAGER", "section_exam_managers",
               record_id=em.id, request=request)

    return {**_manager_dict(em), "message": "ยืนยันแล้ว ✅"}


@router.put("/{manager_id}/reassign")
def reassign_manager(
    manager_id: int,
    data: ProposeManagerRequest,
    request: Request,
    db:   Session = Depends(get_db),
    current_user: models.User = Depends(require_dept_or_admin),
):
    """Admin เปลี่ยนผู้รับผิดชอบ"""
    em = db.query(models.SectionExamManager).filter(
        models.SectionExamManager.id == manager_id
    ).first()
    if not em:
        raise HTTPException(404, "ไม่พบ")

    new_manager = db.query(models.User).filter(
        models.User.id == data.manager_id,
        models.User.role == models.UserRole.teacher,
    ).first()
    if not new_manager:
        raise HTTPException(400, "ไม่พบอาจารย์")

    old_manager_id = em.manager_id
    em.manager_id   = data.manager_id
    em.proposed_by  = current_user.id
    em.confirmed    = True
    em.confirmed_by = current_user.id
    em.confirmed_at = datetime.now(timezone.utc)
    em.note         = data.note or em.note
    em.assignment_source = OWNER_SOURCE_MANUAL
    db.commit()

    _ensure_submission(db, em.section_id, data.manager_id)

    log_action(db, current_user, "REASSIGN_EXAM_MANAGER", "section_exam_managers",
               record_id=em.id,
               old_values={"manager_id": old_manager_id},
               new_values={"manager_id": data.manager_id, "manager": new_manager.full_name},
               request=request)

    return {**_manager_dict(em), "message": f"เปลี่ยนเป็น {new_manager.full_name} แล้ว"}


@router.get("/pending")
def get_pending_confirmations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """รายการที่รอ confirm ของฉัน"""
    pending = db.query(models.SectionExamManager).options(
        joinedload(models.SectionExamManager.section)
            .joinedload(models.Section.course),
        joinedload(models.SectionExamManager.proposer),
    ).filter(
        models.SectionExamManager.manager_id == current_user.id,
        models.SectionExamManager.confirmed  == False,
    ).all()

    return [_manager_dict(em) for em in pending]


@router.get("/section/{section_id}")
def get_section_managers(
    section_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """ดู managers ทั้ง midterm + final ของ section นี้"""
    managers = db.query(models.SectionExamManager).options(
        joinedload(models.SectionExamManager.manager),
        joinedload(models.SectionExamManager.proposer),
        joinedload(models.SectionExamManager.confirmer),
    ).filter(
        models.SectionExamManager.section_id == section_id
    ).all()

    return {
        "section_id": section_id,
        "midterm":    next((_manager_dict(m) for m in managers if m.exam_type == "midterm"), None),
        "final":      next((_manager_dict(m) for m in managers if m.exam_type == "final"),   None),
        "complete":   len([m for m in managers if m.confirmed]) == 2,
    }


@router.get("/overview")
def get_overview(
    semester:      Optional[str] = None,
    academic_year: Optional[str] = None,
    unassigned_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_dept_or_admin),
):
    """
    ภาพรวมทุก section — ใครได้รับมอบหมายแล้ว ใครยังไม่ได้
    Admin ใช้ตรวจก่อน optimize
    """
    # active period ถ้าไม่ระบุ
    if not semester or not academic_year:
        p = db.query(models.ExamPeriod).filter(
            models.ExamPeriod.is_active == True
        ).first()
        if p:
            semester      = semester      or p.semester
            academic_year = academic_year or p.academic_year

    dept_filter = get_dept_filter(current_user)

    q = db.query(models.Section).options(
        joinedload(models.Section.course),
        joinedload(models.Section.teacher),
        joinedload(models.Section.teaching_room),
    ).filter(
        and_(
            models.Section.semester      == semester,
            models.Section.academic_year == academic_year,
        )
    )
    # dept_supervisor เห็นแค่แผนกตัวเอง
    if dept_filter:
        group_clause = build_course_group_clause(models.Course.course_id, dept_filter)
        if group_clause is None:
            sections = []
        else:
            q = q.join(
                models.Course, models.Section.course_id == models.Course.id
            ).filter(group_clause)
            sections = q.order_by(models.Section.id.asc()).all()
    else:
        sections = q.order_by(models.Section.id.asc()).all()
    owner_map, created = build_owner_map(
        db,
        sections,
        ["midterm", "final"],
        auto_create=True,
        actor_id=current_user.id,
    )
    if created:
        db.commit()

    result = []
    ready_count = 0
    needs_attention_count = 0
    auto_assigned_count = 0
    manual_assigned_count = 0
    for sec in sections:
        mid = owner_map.get((sec.id, "midterm"))
        fin = owner_map.get((sec.id, "final"))
        mid_status = get_assignment_status(mid)
        fin_status = get_assignment_status(fin)
        both_ok = bool(mid and mid.confirmed and fin and fin.confirmed)
        needs_attention = any(status_name in {"needs_attention", "pending"} for status_name in (mid_status, fin_status))

        if both_ok:
            ready_count += 1
        if needs_attention:
            needs_attention_count += 1
        if any(status_name == "manual_assigned" for status_name in (mid_status, fin_status)):
            manual_assigned_count += 1
        if all(status_name == "auto_assigned" for status_name in (mid_status, fin_status)):
            auto_assigned_count += 1

        row = {
            "section_id":    sec.id,
            "course_id":     sec.course.course_id   if sec.course else None,
            "course_name":   sec.course.course_name_th if sec.course else None,
            "section_no":    sec.section_no,
            "department":    _section_department_code(sec),
            "academic_group": _section_department_code(sec),
            "imported_teachers": [_teacher_dict(sec.teacher)] if sec.teacher else [],
            "main_teacher":  sec.teacher.full_name  if sec.teacher else None,
            "num_students":  sec.num_students,
            "teaching_room": sec.teaching_room.room_name if sec.teaching_room else None,
            "midterm": _manager_dict(mid) if mid else None,
            "final":   _manager_dict(fin) if fin else None,
            "midterm_ok": mid.confirmed if mid else False,
            "final_ok":   fin.confirmed if fin else False,
            "both_ok":    both_ok,
            "needs_attention": needs_attention,
        }
        if unassigned_only and row["both_ok"]:
            continue
        result.append(row)

    total = len(sections)

    return {
        "semester":     semester,
        "academic_year":academic_year,
        "total":        total,
        "assigned":     ready_count,
        "unassigned":   total - ready_count,
        "ready_count":  ready_count,
        "needs_attention_count": needs_attention_count,
        "auto_assigned_count": auto_assigned_count,
        "manual_assigned_count": manual_assigned_count,
        "pct_complete": round(ready_count / total * 100, 1) if total else 0,
        "sections":     result,
    }


# ══════════════════════════════════════════════════════════════
# EXAM MATERIALS
# ══════════════════════════════════════════════════════════════



@router.get("/my-sections")
def get_my_sections(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    อาจารย์ดูว่าตัวเองเป็น main teacher ของ sections ไหนบ้าง
    และมีใคร propose มาให้ confirm ไหม
    ใช้ใน "ขั้น 0" ที่อาจารย์ต้องเข้ามาจัดการ
    """
    p = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.is_active == True
    ).first()
    if not p:
        return {"sections": [], "pending_confirm": []}

    try:
        active_exam_type = normalize_owner_exam_type(p.exam_type)
    except ValueError:
        active_exam_type = None

    # sections ที่รับผิดชอบ:
    # - teacher: เฉพาะ section ที่ถูก assign ให้ใน active exam cycle
    # - dept_supervisor: ทุก section ในแผนกตัวเอง
    if current_user.role == models.UserRole.dept_supervisor and current_user.dept_code:
        group_clause = build_course_group_clause(models.Course.course_id, current_user.dept_code)
        base_query = db.query(models.Section).options(
            joinedload(models.Section.course),
        ).filter(
            and_(
                models.Section.semester == p.semester,
                models.Section.academic_year == p.academic_year,
            )
        )
        if group_clause is None:
            my_sections = []
        else:
            my_sections = base_query.join(
                models.Course, models.Section.course_id == models.Course.id
            ).filter(group_clause).all()
    elif current_user.role == models.UserRole.teacher:
        owned_section_ids, _ = get_teacher_owned_section_ids(
            db,
            current_user.id,
            p.semester,
            p.academic_year,
        )
        if owned_section_ids is None:
            my_sections = db.query(models.Section).options(
                joinedload(models.Section.course),
            ).filter(
                and_(
                    models.Section.teacher_id == current_user.id,
                    models.Section.semester == p.semester,
                    models.Section.academic_year == p.academic_year,
                )
            ).all()
        elif owned_section_ids:
            my_sections = db.query(models.Section).options(
                joinedload(models.Section.course),
            ).filter(
                models.Section.id.in_(owned_section_ids)
            ).all()
        else:
            my_sections = []
    else:
        my_sections = db.query(models.Section).options(
            joinedload(models.Section.course),
        ).filter(
            and_(
                models.Section.teacher_id    == current_user.id,
                models.Section.semester      == p.semester,
                models.Section.academic_year == p.academic_year,
            )
        ).all()

    # sections ที่มีคนเสนอให้เป็น manager แต่ยังไม่ confirm
    pending = db.query(models.SectionExamManager).options(
        joinedload(models.SectionExamManager.section)
            .joinedload(models.Section.course),
        joinedload(models.SectionExamManager.proposer),
    ).filter(
        and_(
            models.SectionExamManager.manager_id == current_user.id,
            models.SectionExamManager.confirmed  == False,
        )
    ).all()

    owner_map, created = build_owner_map(
        db,
        my_sections,
        ["midterm", "final"],
        auto_create=True,
        actor_id=current_user.id,
    )
    if created:
        db.commit()

    result = []
    for sec in my_sections:
        mid_owner = owner_map.get((sec.id, "midterm"))
        final_owner = owner_map.get((sec.id, "final"))
        needs_action = (
            not (
                (
                    active_exam_type == "midterm"
                    and mid_owner is not None
                    and mid_owner.confirmed
                )
                or (
                    active_exam_type == "final"
                    and final_owner is not None
                    and final_owner.confirmed
                )
            )
            if active_exam_type
            else not (
                (mid_owner is not None and mid_owner.confirmed)
                and (final_owner is not None and final_owner.confirmed)
            )
        )
        result.append({
            "section_id":  sec.id,
            "course_id":   sec.course.course_id    if sec.course else None,
            "course_name": sec.course.course_name_th if sec.course else None,
            "section_no":  sec.section_no,
            "num_students":sec.num_students,
            "midterm":     _manager_dict(mid_owner) if mid_owner else None,
            "final":       _manager_dict(final_owner) if final_owner else None,
            "needs_action": needs_action,
        })

    return {
        "my_sections":    result,
        "pending_confirm": [_manager_dict(em) for em in pending],
        "needs_action_count": len([r for r in result if r["needs_action"]]) + len(pending),
    }

@router.get("/materials/{submission_id}")
def get_materials(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    mat = db.query(models.ExamMaterialRequest).filter(
        models.ExamMaterialRequest.submission_id == submission_id
    ).first()
    if not mat:
        return {"submission_id": submission_id, "materials": None, "exists": False}
    return {"submission_id": submission_id, "materials": _material_dict(mat), "exists": True}


@router.post("/materials/{submission_id}")
def save_materials(
    submission_id: int,
    data: MaterialRequest,
    request: Request,
    db:   Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    บันทึกสิ่งที่ต้องการเพิ่มเติม (กรอกได้ตั้งแต่ step 0 ก่อนมีวันสอบ)
    upsert — กรอกซ้ำได้ ข้อมูลจะ update
    """
    sub = db.query(models.ExamSubmission).filter(
        models.ExamSubmission.id == submission_id
    ).first()
    if not sub:
        raise HTTPException(404, "ไม่พบ submission")

    # ตรวจสิทธิ์ — เฉพาะ exam manager หรือ admin
    is_admin = current_user.role == models.UserRole.admin
    if not is_admin and sub.submitted_by != current_user.id:
        # ตรวจว่าเป็น exam manager ของ section นี้
        em = db.query(models.SectionExamManager).filter(
            and_(
                models.SectionExamManager.section_id == sub.section_id,
                models.SectionExamManager.manager_id == current_user.id,
                models.SectionExamManager.confirmed  == True,
            )
        ).first()
        if not em:
            raise HTTPException(403, "เฉพาะผู้รับผิดชอบ exam หรือ admin เท่านั้น")

    if sub.status in (models.SubmissionStatus.approved, models.SubmissionStatus.released):
        raise HTTPException(400, "ไม่สามารถแก้ไขได้ — submission ถูก approve แล้ว")

    mat = db.query(models.ExamMaterialRequest).filter(
        models.ExamMaterialRequest.submission_id == submission_id
    ).first()

    if mat:
        # update
        for k, v in data.dict().items():
            setattr(mat, k, v)
    else:
        mat = models.ExamMaterialRequest(
            submission_id = submission_id,
            **data.dict()
        )
        db.add(mat)

    mat.confirmed    = True
    mat.confirmed_at = datetime.now(timezone.utc)
    db.commit()

    # อัปเดต exam_format_confirmed ใน submission
    sub.exam_format_confirmed    = True
    sub.exam_format_confirmed_at = datetime.now(timezone.utc)
    db.commit()

    log_action(db, current_user, "SAVE_EXAM_MATERIALS", "exam_material_requests",
               record_id=mat.id, new_values=data.dict(), request=request)

    return {
        "status":    "saved",
        "materials": _material_dict(mat),
    }


# ── Internal helper ───────────────────────────────────────────
def _ensure_submission(db: Session, section_id: int, user_id: int):
    """
    สร้าง ExamSubmission ถ้ายังไม่มี
    เรียกหลัง confirm manager เพื่อให้ระบบพร้อมรับข้อมูลจากอาจารย์
    """
    existing = db.query(models.ExamSubmission).filter(
        models.ExamSubmission.section_id == section_id
    ).first()
    if not existing:
        sub = models.ExamSubmission(
            section_id   = section_id,
            submitted_by = user_id,
            status       = models.SubmissionStatus.draft,
        )
        db.add(sub)
        db.commit()


@router.delete("/{manager_id}")
def delete_manager(
    manager_id: int,
    request: Request,
    db:   Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """ลบ/ปฏิเสธการมอบหมาย — เฉพาะตัวเองหรือ admin"""
    em = db.query(models.SectionExamManager).filter(
        models.SectionExamManager.id == manager_id
    ).first()
    if not em:
        raise HTTPException(404, "ไม่พบ")
    is_admin = current_user.role == models.UserRole.admin
    if not is_admin and em.manager_id != current_user.id:
        raise HTTPException(403, "ไม่มีสิทธิ์")
    db.delete(em)
    db.commit()
    log_action(db, current_user, "DELETE_EXAM_MANAGER", "section_exam_managers",
               record_id=manager_id, request=request)
    return {"status": "deleted"}
