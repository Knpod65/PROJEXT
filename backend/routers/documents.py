"""
Documents Router — สร้างเอกสาร 3 ประเภทหลัง optimize เสร็จ

POST /api/documents/generate/{schedule_id}
  → สร้างและ zip ทั้ง 3 ไฟล์พร้อมกัน
  → return: zip stream

GET  /api/documents/generate-all
  → สร้างทุก schedule ที่ status=published ใน session นั้น
  → return: zip รวมทุก section

Query params:
  type = cover_page | envelope | attendance | all (default: all)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import Optional
from database import get_db
import models
from auth_utils import get_current_user, require_staff_or_admin, log_action
from policies.document_policy import require_document_manager
from services.document_service import DocumentService

import io, zipfile, os, math

# นำเข้า generator functions
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
_GEN_DOCS_IMPORT_ERROR: Exception | None = None
try:
    from gen_docs import generate_cover_page, generate_envelope_cover, generate_attendance_sheet
except Exception as exc:  # pragma: no cover - local env dependent
    generate_cover_page = None
    generate_envelope_cover = None
    generate_attendance_sheet = None
    _GEN_DOCS_IMPORT_ERROR = exc

from exam_pickup import (
    activate_pickup_qr,
    build_pickup_assignments,
    create_pickup_qr,
    ensure_active_pickup_qr,
    ensure_schedule_ready_for_pickup,
    get_active_pickup_qr,
    get_confirmed_section_owner,
    get_latest_pickup_qr,
    serialize_pickup_qr,
)
from operational_documents import (
    build_bundle_filename,
    build_document_filename,
    generate_envelope_cover_pdf,
    generate_participant_code_announcement_pdf,
    generate_signature_sheet_pdf,
    iter_document_types,
    normalize_document_type,
)

router = APIRouter()


def _document_service(db: Session) -> DocumentService:
    return DocumentService(db)

# path ของ QR code image
QR_IMAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "qr_regulation.png")


def _ensure_doc_generators_available() -> None:
    if generate_cover_page and generate_envelope_cover and generate_attendance_sheet:
        return
    detail = "Document generation dependencies are unavailable in this local environment."
    if _GEN_DOCS_IMPORT_ERROR:
        detail = f"{detail} ({_GEN_DOCS_IMPORT_ERROR})"
    raise HTTPException(503, detail)


def _safe_filename(s: str) -> str:
    """ทำให้ชื่อไฟล์ปลอดภัย"""
    import re
    return re.sub(r'[^\w\-.]', '_', s)


def _load_schedule(db: Session, schedule_id: int) -> models.ExamSchedule:
    sch = db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.section)
            .joinedload(models.Section.course),
        joinedload(models.ExamSchedule.section)
            .joinedload(models.Section.teacher),
        joinedload(models.ExamSchedule.room),
        joinedload(models.ExamSchedule.supervisions)
            .joinedload(models.Supervision.user),
    ).filter(models.ExamSchedule.id == schedule_id).first()

    if not sch:
        raise HTTPException(404, f"ไม่พบ schedule id={schedule_id}")
    return sch


def _build_docs(sch: models.ExamSchedule, db: Session) -> dict:
    """
    สร้าง bytes ของเอกสารทั้ง 3 จาก ExamSchedule object
    return: {
      "cover_page": bytes,
      "envelope":   bytes,
      "attendance": bytes,
      "filename_prefix": str,
    }
    """
    _ensure_doc_generators_available()
    sec     = sch.section
    course  = sec.course if sec else None
    teacher = sec.teacher if sec else None
    room    = sch.room

    course_id   = course.course_id   if course  else "UNKNOWN"
    section_no  = sec.section_no     if sec     else "?"
    exam_date   = sch.exam_date      or "2026-01-01"
    exam_time   = sch.exam_time      or "00.00-00.00"
    room_name   = room.room_name     if room    else "?"
    teacher_name= teacher.full_name  if teacher else "-"
    num_students= sec.num_students   if sec     else 0
    exam_type   = sch.exam_type.value if sch.exam_type else "final"
    semester    = sec.semester       if sec     else "2"
    acad_year   = sec.academic_year  if sec     else "2568"

    # กรรมการคุมสอบ
    supervisors = []
    for sup in sorted(sch.supervisions or [], key=lambda s: s.slot_order):
        if sup.user:
            supervisors.append({
                "name":       sup.user.full_name or "",
                "slot_order": sup.slot_order,
            })

    # รายชื่อนักศึกษาจาก EnrollmentRecord
    enrollment_records = db.query(models.EnrollmentRecord).filter(
        models.EnrollmentRecord.section_id == sec.id
    ).order_by(models.EnrollmentRecord.student_name).all() if sec else []

    students = [
        {"student_id": r.student_id, "student_name": r.student_name}
        for r in enrollment_records
    ]
    # ถ้าไม่มี enrollment records ใช้จำนวนจาก num_students (placeholder)
    if not students:
        students = [
            {"student_id": f"xxxxxxx{i:04d}", "student_name": f"(นักศึกษาลำดับที่ {i})"}
            for i in range(1, num_students + 1)
        ]

    prefix = _safe_filename(f"{course_id}_ตอน{section_no}_{room_name}")

    qr_path = QR_IMAGE_PATH if os.path.exists(QR_IMAGE_PATH) else None

    common = dict(
        course_id=course_id,
        section_no=section_no,
        exam_date=exam_date,
        exam_time=exam_time,
        room_name=room_name,
        exam_type=exam_type,
        semester=semester,
        academic_year=acad_year,
    )

    return {
        "cover_page": generate_cover_page(
            **common,
            course_name_th=course.course_name_th if course else "",
        ),
        "envelope": generate_envelope_cover(
            **common,
            teacher_name=teacher_name,
            supervisors=supervisors,
            num_students=num_students,
            num_exam_sets=num_students,  # 1 ชุดต่อคน (ปรับได้)
            qr_image_path=qr_path,
        ),
        "attendance": generate_attendance_sheet(
            **common,
            teacher_name=teacher_name,
            students=students,
        ),
        "filename_prefix": prefix,
    }


# ══════════════════════════════════════════════════════════════
# POST /api/documents/generate/{schedule_id}
# ══════════════════════════════════════════════════════════════
@router.post("/generate/{schedule_id}")
def generate_documents(
    schedule_id: int,
    request: Request,
    doc_type: str = Query("all", description="cover_page | envelope | attendance | all"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_document_manager),
):
    """
    สร้างเอกสารสำหรับ 1 schedule
    - cover_page: ใบปะหน้าข้อสอบ (2 หน้า)
    - envelope:   ปกซองข้อสอบ
    - attendance: ใบลงลายมือชื่อ
    - all:        zip รวมทั้ง 3
    """
    return _document_service(db).generate_documents(schedule_id, request, current_user, doc_type)


# ══════════════════════════════════════════════════════════════
# POST /api/documents/generate-batch
# ══════════════════════════════════════════════════════════════
@router.post("/generate-batch")
def generate_batch_documents(
    request: Request,
    semester: str = Query("2"),
    academic_year: str = Query("2568"),
    exam_type: str = Query("final"),
    doc_type: str = Query("all", description="cover_page | envelope | attendance | all"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_document_manager),
):
    """
    สร้างเอกสารทุก section ที่ optimize แล้ว (status=published)
    ใน semester/year นั้น → ได้เป็น ZIP เดียว
    """
    return _document_service(db).generate_batch_documents(request, current_user, semester=semester, academic_year=academic_year, exam_type=exam_type, doc_type=doc_type)


# ══════════════════════════════════════════════════════════════
# GET /api/documents/preview/{schedule_id}
# ══════════════════════════════════════════════════════════════
@router.get("/preview/{schedule_id}")
def preview_document_info(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """ดูข้อมูลที่จะถูกใช้ generate เอกสาร (ไม่ generate จริง)"""
    return _document_service(db).preview_document_info(schedule_id)


# ══════════════════════════════════════════════════════════════
# PDF Processing endpoints (เชื่อมกับ ExamSubmission)
# ══════════════════════════════════════════════════════════════

import sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from exam_pdf_processor import (
    stamp_exam_header, merge_exam_with_cover,
    build_full_exam_set, split_students_by_room,
)
from routers.settings import get_setting


def _get_buffer_pct(db: Session) -> float:
    val = get_setting(db, "printshop_copies_buffer")
    try:
        return float(val) if val else 5.0
    except:
        return 5.0


def _get_exam_pdf(submission: models.ExamSubmission) -> bytes:
    """อ่าน PDF จาก path ที่ submission เก็บไว้"""
    path = submission.pdf_stripped_path or submission.pdf_original_path
    if not path or not os.path.exists(path):
        raise HTTPException(404, "ไม่พบไฟล์ PDF ข้อสอบ — อาจารย์ยังไม่ได้ upload หรือไฟล์หาย")
    with open(path, "rb") as f:
        return f.read()


def _get_students_sorted(section_id: int, db: Session) -> list:
    """ดึงรายชื่อนักศึกษาเรียงรหัสน้อย→มาก"""
    records = db.query(models.EnrollmentRecord).filter(
        models.EnrollmentRecord.section_id == section_id
    ).order_by(models.EnrollmentRecord.student_id).all()

    return [{"student_id": r.student_id, "student_name": r.student_name}
            for r in records]


def _get_room_capacities(schedule: models.ExamSchedule, db: Session) -> list:
    """
    ดึงความจุห้อง — ถ้า split ห้องจะมีหลาย schedule สำหรับ section เดียวกัน
    """
    sec = schedule.section
    if not sec:
        return []

    # หา schedules ทุกอันของ section นี้ (กรณี split)
    all_schedules = db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.room)
    ).filter(
        models.ExamSchedule.section_id == sec.id,
        models.ExamSchedule.exam_type  == schedule.exam_type,
    ).order_by(models.ExamSchedule.id).all()

    rooms = []
    for sch in all_schedules:
        if sch.room:
            rooms.append({
                "room_name": sch.room.room_name,
                "capacity":  sch.room.capacity,
                "schedule_id": sch.id,
            })
    # fallback ถ้าไม่ split
    if not rooms and schedule.room:
        rooms = [{"room_name": schedule.room.room_name,
                  "capacity": schedule.room.capacity,
                  "schedule_id": schedule.id}]
    return rooms


# ── GET /api/documents/exam-info/{submission_id} ──────────────
@router.get("/exam-info/{submission_id}")
def get_exam_print_info(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_document_manager),
):
    """
    ข้อมูลการพิมพ์ก่อน confirm
    - จำนวนหน้าต่อชุด
    - จำนวนชุดทั้งหมด (รวม buffer)
    - หน้ารวม
    - การแบ่งห้อง + ลำดับนักศึกษา
    """
    return _document_service(db).get_exam_print_info(submission_id)


# ── POST /api/documents/preview-pdf/{submission_id} ───────────
@router.post("/preview-pdf/{submission_id}")
def generate_preview_pdf(
    submission_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_document_manager),
):
    """
    สร้าง preview PDF 1 ชุด (ลำดับที่ 1):
      ใบปะหน้า 2 ใบ + ข้อสอบพร้อม header
    ส่งให้อาจารย์ตรวจสอบก่อน release ให้ร้านถ่าย
    """
    return _document_service(db).generate_preview_pdf(submission_id, request, current_user)


def _resolve_document_period(
    db: Session,
    *,
    academic_year: Optional[str] = None,
    semester: Optional[str] = None,
    exam_type: Optional[str] = None,
) -> models.ExamPeriod:
    if academic_year and semester and exam_type:
        period = db.query(models.ExamPeriod).filter(
            models.ExamPeriod.academic_year == str(academic_year),
            models.ExamPeriod.semester == str(semester),
            models.ExamPeriod.exam_type == str(exam_type),
        ).first()
    else:
        period = db.query(models.ExamPeriod).filter(
            models.ExamPeriod.is_active == True
        ).first()

    if not period:
        raise HTTPException(404, "ไม่พบภาคสอบที่ต้องการสำหรับการสร้างเอกสาร")
    return period


def _load_export_schedules(
    db: Session,
    *,
    schedule_id: Optional[int] = None,
    course_id: Optional[str] = None,
    section_no: Optional[str] = None,
    room_id: Optional[int] = None,
    academic_year: Optional[str] = None,
    semester: Optional[str] = None,
    exam_type: Optional[str] = None,
) -> list[models.ExamSchedule]:
    if schedule_id is not None:
        return [_load_schedule(db, schedule_id)]

    period = _resolve_document_period(
        db,
        academic_year=academic_year,
        semester=semester,
        exam_type=exam_type,
    )
    exam_type_enum = models.ExamType(period.exam_type)

    query = db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
        joinedload(models.ExamSchedule.section).joinedload(models.Section.teacher),
        joinedload(models.ExamSchedule.room),
        joinedload(models.ExamSchedule.supervisions).joinedload(models.Supervision.user),
    ).join(models.Section).join(models.Course).filter(
        models.Section.academic_year == period.academic_year,
        models.Section.semester == period.semester,
        models.ExamSchedule.exam_type == exam_type_enum,
    )

    if course_id:
        query = query.filter(models.Course.course_id == course_id.strip())
    if section_no:
        query = query.filter(models.Section.section_no == section_no.strip())
    if room_id is not None:
        query = query.filter(models.ExamSchedule.room_id == room_id)

    return query.order_by(
        models.ExamSchedule.exam_date,
        models.ExamSchedule.exam_time,
        models.Course.course_id,
        models.Section.section_no,
    ).all()


def _serialize_schedule_summary(schedule: models.ExamSchedule, db: Session) -> dict[str, object]:
    section = schedule.section
    course = section.course if section else None
    teacher = get_confirmed_section_owner(db, schedule)
    return {
        "id": schedule.id,
        "course_code": course.course_id if course else None,
        "course_name": course.course_name_th or course.course_name_en if course else None,
        "section_no": section.section_no if section else None,
        "exam_date": schedule.exam_date.isoformat() if hasattr(schedule.exam_date, "isoformat") else str(schedule.exam_date),
        "exam_time": schedule.exam_time,
        "room_name": schedule.room.room_name if schedule.room else None,
        "teacher_name": teacher.full_name if teacher else None,
        "status": schedule.status.value if hasattr(schedule.status, "value") else str(schedule.status),
    }


def _load_students_for_schedule(schedule: models.ExamSchedule, db: Session) -> list[dict[str, str]]:
    section = schedule.section
    if not section:
        return []

    rows = db.query(models.EnrollmentRecord).filter(
        models.EnrollmentRecord.section_id == section.id
    ).order_by(
        models.EnrollmentRecord.student_id,
        models.EnrollmentRecord.student_name,
    ).all()
    if rows:
        return [
            {
                "student_id": row.student_id,
                "student_name": row.student_name or "",
            }
            for row in rows
        ]

    legacy_rows = db.query(models.Enrollment).join(
        models.Student,
        models.Student.student_id == models.Enrollment.student_id,
    ).filter(
        models.Enrollment.section_id == section.id
    ).order_by(
        models.Enrollment.student_id
    ).all()
    return [
        {
            "student_id": row.student_id,
            "student_name": row.student.full_name if row.student else "",
        }
        for row in legacy_rows
    ]


def _build_operational_document_payload(
    db: Session,
    schedule: models.ExamSchedule,
    *,
    actor_id: int,
    include_qr: bool,
) -> dict[str, object]:
    ensure_schedule_ready_for_pickup(db, schedule)

    section = schedule.section
    course = section.course if section and section.course else None
    room = schedule.room
    teacher = get_confirmed_section_owner(db, schedule)
    students = _load_students_for_schedule(schedule, db)
    invigilators = [
        {
            "name": supervision.user.full_name or supervision.user.username,
            "role": supervision.role_in_exam or "invigilator",
        }
        for supervision in sorted(schedule.supervisions or [], key=lambda item: item.slot_order or 0)
        if supervision.user
    ]

    if include_qr and not invigilators:
        raise HTTPException(400, "ยังไม่ได้ยืนยันผู้คุมสอบหรือผู้รับข้อสอบสำหรับการพิมพ์ปกซองข้อสอบ")

    active_qr = ensure_active_pickup_qr(db, schedule, actor_id=actor_id) if include_qr else None
    return {
        "schedule_id": schedule.id,
        "course_code": course.course_id if course else "-",
        "course_name": course.course_name_th or course.course_name_en if course else "-",
        "section_no": section.section_no if section else "-",
        "exam_date": schedule.exam_date,
        "exam_time": schedule.exam_time,
        "exam_type": schedule.exam_type.value if hasattr(schedule.exam_type, "value") else str(schedule.exam_type),
        "semester": section.semester if section else "-",
        "academic_year": section.academic_year if section else "-",
        "room_name": room.room_name if room else "-",
        "total_students": section.num_students if section else len(students),
        "instructor_name": teacher.full_name if teacher else (section.teacher.full_name if section and section.teacher else "-"),
        "invigilators": invigilators,
        "student_rows": students,
        "qr_x_value": active_qr and serialize_pickup_qr(active_qr)["qr_value"],
    }


def _generate_operational_document_bytes(document_type: str, payload: dict[str, object]) -> bytes:
    if document_type == "participant_codes":
        return generate_participant_code_announcement_pdf(payload)
    if document_type == "signature_sheet":
        return generate_signature_sheet_pdf(payload)
    if document_type == "envelope_cover":
        return generate_envelope_cover_pdf(payload)
    raise HTTPException(400, f"Unsupported document type: {document_type}")


@router.get("/pickup-qr/{schedule_id}")
def get_pickup_qr_status(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_document_manager),
):
    return _document_service(db).get_pickup_qr_status(schedule_id)


@router.post("/pickup-qr/{schedule_id}/regenerate")
def regenerate_pickup_qr(
    schedule_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_document_manager),
):
    return _document_service(db).regenerate_pickup_qr(schedule_id, request, current_user)


@router.post("/pickup-qr/{schedule_id}/confirm")
def confirm_pickup_qr(
    schedule_id: int,
    request: Request,
    qr_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_document_manager),
):
    return _document_service(db).confirm_pickup_qr(schedule_id, request, current_user, qr_id=qr_id)


@router.get("/export-pdf")
def export_operational_documents(
    request: Request,
    schedule_id: Optional[int] = None,
    course_id: Optional[str] = None,
    section_no: Optional[str] = None,
    room_id: Optional[int] = None,
    academic_year: Optional[str] = None,
    semester: Optional[str] = None,
    exam_type: Optional[str] = None,
    document_type: str = Query("all"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_document_manager),
):
    return _document_service(db).export_operational_documents(request, current_user, schedule_id=schedule_id, course_id=course_id, section_no=section_no, room_id=room_id, academic_year=academic_year, semester=semester, exam_type=exam_type, document_type=document_type)
