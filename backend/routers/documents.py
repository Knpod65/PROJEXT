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
    current_user: models.User = Depends(require_staff_or_admin),
):
    """
    สร้างเอกสารสำหรับ 1 schedule
    - cover_page: ใบปะหน้าข้อสอบ (2 หน้า)
    - envelope:   ปกซองข้อสอบ
    - attendance: ใบลงลายมือชื่อ
    - all:        zip รวมทั้ง 3
    """
    sch  = _load_schedule(db, schedule_id)
    docs = _build_docs(sch, db)
    pfx  = docs["filename_prefix"]

    log_action(db, current_user, "GENERATE_DOCUMENTS", "exam_schedules",
               record_id=schedule_id, new_values={"doc_type": doc_type}, request=request)

    if doc_type == "cover_page":
        filename = f"ใบปะหน้า_{pfx}.docx"
        return StreamingResponse(
            io.BytesIO(docs["cover_page"]),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    elif doc_type == "envelope":
        filename = f"ปกซอง_{pfx}.docx"
        return StreamingResponse(
            io.BytesIO(docs["envelope"]),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    elif doc_type == "attendance":
        filename = f"ใบลงมือชื่อ_{pfx}.docx"
        return StreamingResponse(
            io.BytesIO(docs["attendance"]),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    else:
        # zip ทั้ง 3
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"ใบปะหน้า_{pfx}.docx",   docs["cover_page"])
            zf.writestr(f"ปกซอง_{pfx}.docx",       docs["envelope"])
            zf.writestr(f"ใบลงมือชื่อ_{pfx}.docx", docs["attendance"])
        zip_buf.seek(0)
        return StreamingResponse(
            zip_buf,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="เอกสารสอบ_{pfx}.zip"'},
        )


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
    current_user: models.User = Depends(require_staff_or_admin),
):
    """
    สร้างเอกสารทุก section ที่ optimize แล้ว (status=published)
    ใน semester/year นั้น → ได้เป็น ZIP เดียว
    """
    exam_type_enum = models.ExamType.final if exam_type == "final" else models.ExamType.midterm

    schedules = db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.section)
            .joinedload(models.Section.course),
        joinedload(models.ExamSchedule.section)
            .joinedload(models.Section.teacher),
        joinedload(models.ExamSchedule.room),
        joinedload(models.ExamSchedule.supervisions)
            .joinedload(models.Supervision.user),
    ).join(models.Section).filter(
        and_(
            models.Section.semester      == semester,
            models.Section.academic_year == academic_year,
            models.ExamSchedule.exam_type == exam_type_enum,
            models.ExamSchedule.status   == models.ScheduleStatus.published,
        )
    ).order_by(models.ExamSchedule.exam_date, models.ExamSchedule.exam_time).all()

    if not schedules:
        raise HTTPException(404, "ไม่พบ schedule ที่ publish แล้วในช่วงเวลาที่เลือก")

    log_action(db, current_user, "GENERATE_BATCH_DOCUMENTS", "exam_schedules",
               new_values={"semester": semester, "academic_year": academic_year,
                           "exam_type": exam_type, "doc_type": doc_type,
                           "count": len(schedules)},
               request=request)

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for sch in schedules:
            try:
                docs = _build_docs(sch, db)
                pfx  = docs["filename_prefix"]
                date = sch.exam_date or "nodate"

                folder = f"{date}/"

                if doc_type in ("cover_page", "all"):
                    zf.writestr(f"{folder}ใบปะหน้า_{pfx}.docx",   docs["cover_page"])
                if doc_type in ("envelope", "all"):
                    zf.writestr(f"{folder}ปกซอง_{pfx}.docx",       docs["envelope"])
                if doc_type in ("attendance", "all"):
                    zf.writestr(f"{folder}ใบลงมือชื่อ_{pfx}.docx", docs["attendance"])
            except Exception as e:
                # ข้าม section ที่มีปัญหา ไม่หยุด batch
                zf.writestr(f"ERROR_{sch.id}.txt", str(e))

    zip_buf.seek(0)
    exam_type_th = "ปลายภาค" if exam_type == "final" else "กลางภาค"
    fname = f"เอกสารสอบ_{exam_type_th}_{academic_year}_ภาค{semester}.zip"
    return StreamingResponse(
        zip_buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


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
    sch = _load_schedule(db, schedule_id)
    sec = sch.section
    course = sec.course if sec else None

    enrollment_count = db.query(models.EnrollmentRecord).filter(
        models.EnrollmentRecord.section_id == sec.id
    ).count() if sec else 0

    return {
        "schedule_id":    sch.id,
        "course_id":      course.course_id if course else None,
        "course_name_th": course.course_name_th if course else None,
        "section_no":     sec.section_no if sec else None,
        "exam_date":      sch.exam_date,
        "exam_time":      sch.exam_time,
        "room":           sch.room.room_name if sch.room else None,
        "teacher":        sec.teacher.full_name if sec and sec.teacher else None,
        "num_students":   sec.num_students if sec else 0,
        "enrollment_records": enrollment_count,
        "supervisors": [
            {"name": s.user.full_name, "slot": s.slot_order}
            for s in sorted(sch.supervisions or [], key=lambda x: x.slot_order)
            if s.user
        ],
        "status":      sch.status.value if sch.status else None,
        "ready":       enrollment_count > 0,
        "note":        None if enrollment_count > 0
                       else f"⚠ ยังไม่มี enrollment records — ใบลงมือชื่อจะใช้ placeholder {sec.num_students if sec else 0} คน",
    }


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
    current_user: models.User = Depends(require_staff_or_admin),
):
    """
    ข้อมูลการพิมพ์ก่อน confirm
    - จำนวนหน้าต่อชุด
    - จำนวนชุดทั้งหมด (รวม buffer)
    - หน้ารวม
    - การแบ่งห้อง + ลำดับนักศึกษา
    """
    sub = db.query(models.ExamSubmission).options(
        joinedload(models.ExamSubmission.section)
            .joinedload(models.Section.course),
        joinedload(models.ExamSubmission.section)
            .joinedload(models.Section.teacher),
        joinedload(models.ExamSubmission.material_request),
    ).filter(models.ExamSubmission.id == submission_id).first()

    if not sub:
        raise HTTPException(404, "ไม่พบ submission")
    if sub.status not in (models.SubmissionStatus.approved, models.SubmissionStatus.released):
        raise HTTPException(400, f"submission ยังไม่ได้ approve (status={sub.status.value})")

    sec = sub.section
    schedule = db.query(models.ExamSchedule).filter(
        models.ExamSchedule.section_id == sec.id
    ).first() if sec else None

    # หน้าข้อสอบ
    exam_pages = 0
    if sub.pdf_stripped_path and os.path.exists(sub.pdf_stripped_path):
        from pypdf import PdfReader as _R
        exam_pages = len(_R(sub.pdf_stripped_path).pages)
    elif sub.pdf_original_path and os.path.exists(sub.pdf_original_path):
        from pypdf import PdfReader as _R
        exam_pages = len(_R(sub.pdf_original_path).pages)
    elif sub.a4_pages_count:
        exam_pages = sub.a4_pages_count

    cover_pages  = 2
    total_pages  = exam_pages + cover_pages
    num_students = sec.num_students if sec else 0
    buffer_pct   = _get_buffer_pct(db)
    buffer_sets  = math.ceil(num_students * buffer_pct / 100)
    print_sets   = num_students + buffer_sets
    print_sheets = print_sets * total_pages

    # ห้อง + นักศึกษา
    students  = _get_students_sorted(sec.id, db) if sec else []
    room_caps = _get_room_capacities(schedule, db) if schedule else []
    splits    = split_students_by_room(students, room_caps) if (students and room_caps) else []

    # print spec จากอาจารย์
    staple_labels = {
        "none":        "ไม่เย็บ",
        "corner_left": "เย็บมุมบนซ้าย",
        "side_left":   "เย็บกลางซ้าย (2 จุด)",
        "custom":      f"เย็บแยกที่หน้า {sub.print_staple_page}",
    }
    # คำนวณหน้าจริงสำหรับร้านถ่าย (duplex ÷ 2 ปัดขึ้น)
    physical_sheets = (math.ceil(total_pages / 2) if sub.print_duplex else total_pages)
    physical_total  = print_sets * physical_sheets

    # ดึง material_request
    mat = None
    if hasattr(sub, 'material_request') and sub.material_request:
        mr = sub.material_request
        mat = {
            "answer_paper_sheets":  mr.answer_paper_sheets,
            "answer_paper_staple":  mr.answer_paper_staple,
            "answer_booklet_count": mr.answer_booklet_count,
            "omr_sheet_count":      mr.omr_sheet_count,
            "omr_form_code":        mr.omr_form_code,
            "scratch_paper_sheets": mr.scratch_paper_sheets,
            "special_note":         mr.special_note,
            # คำนวณรวมต่อ print_sets
            "answer_paper_total":   mr.answer_paper_sheets  * print_sets if mr.answer_paper_sheets  else 0,
            "booklet_total":        mr.answer_booklet_count * print_sets if mr.answer_booklet_count else 0,
            "omr_total":            mr.omr_sheet_count      * print_sets if mr.omr_sheet_count      else 0,
            "scratch_total":        mr.scratch_paper_sheets * print_sets if mr.scratch_paper_sheets else 0,
        }

    return {
        "submission_id":  submission_id,
        "course_id":      sec.course.course_id if sec and sec.course else None,
        "section_no":     sec.section_no if sec else None,
        "exam_pages":     exam_pages,
        "cover_pages":    cover_pages,
        "total_pages":    total_pages,
        "num_students":   num_students,
        "buffer_pct":     buffer_pct,
        "buffer_sets":    buffer_sets,
        "print_sets":     print_sets,
        "print_sheets":   print_sheets,
        # สิ่งที่ต้องการเพิ่มเติม (จากอาจารย์ step 0)
        "material_request": mat,
        # สเปคพิมพ์จากอาจารย์
        "print_spec": {
            "duplex":          sub.print_duplex or False,
            "staple":          sub.print_staple or "none",
            "staple_label":    staple_labels.get(sub.print_staple or "none", "ไม่เย็บ"),
            "staple_page":     sub.print_staple_page,
            "note":            sub.print_note or "",
            "spec_confirmed":  sub.print_spec_confirmed or False,
            # หน้า/แผ่นจริงที่ร้านถ่ายต้องรับ
            "physical_sheets_per_set": physical_sheets,
            "physical_sheets_total":   physical_total,
            "duplex_label": "พิมพ์หน้า-หลัง (Duplex)" if sub.print_duplex else "พิมพ์หน้าเดียว (Simplex)",
        },
        "enrollment_ready": len(students) > 0,
        "room_splits": [
            {
                "room_name":   r["room_name"],
                "count":       r["count"],
                "start_order": r["start_order"],
                "end_order":   r["end_order"],
            }
            for r in splits
        ],
    }


# ── POST /api/documents/preview-pdf/{submission_id} ───────────
@router.post("/preview-pdf/{submission_id}")
def generate_preview_pdf(
    submission_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
):
    """
    สร้าง preview PDF 1 ชุด (ลำดับที่ 1):
      ใบปะหน้า 2 ใบ + ข้อสอบพร้อม header
    ส่งให้อาจารย์ตรวจสอบก่อน release ให้ร้านถ่าย
    """
    sub = db.query(models.ExamSubmission).options(
        joinedload(models.ExamSubmission.section)
            .joinedload(models.Section.course),
        joinedload(models.ExamSubmission.section)
            .joinedload(models.Section.teacher),
    ).filter(models.ExamSubmission.id == submission_id).first()

    if not sub:
        raise HTTPException(404, "ไม่พบ submission")

    log_action(db, current_user, "PREVIEW_SUBMISSION_PDF", "exam_submissions",
               record_id=submission_id, request=request)

    sec      = sub.section
    schedule = db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.room),
        joinedload(models.ExamSchedule.supervisions)
            .joinedload(models.Supervision.user),
    ).filter(models.ExamSchedule.section_id == sec.id).first() if sec else None

    if not schedule:
        raise HTTPException(400, "ยังไม่มีตารางสอบ — ต้อง optimize ก่อน")

    # ดึง PDF ข้อสอบ
    exam_bytes = _get_exam_pdf(sub)

    # สร้างใบปะหน้า (docx→pdf)
    course   = sec.course if sec else None
    teacher  = sec.teacher if sec else None
    sups = [{"name": s.user.full_name, "slot_order": s.slot_order}
            for s in sorted(schedule.supervisions or [], key=lambda x: x.slot_order)
            if s.user]

    from gen_docs import generate_cover_page
    cover_docx = generate_cover_page(
        course_id      = course.course_id if course else "?",
        course_name_th = course.course_name_th if course else "",
        section_no     = sec.section_no,
        exam_date      = schedule.exam_date,
        exam_time      = schedule.exam_time,
        room_name      = schedule.room.room_name if schedule.room else "?",
        exam_type      = schedule.exam_type.value,
        semester       = sec.semester,
        academic_year  = sec.academic_year,
    )

    # convert docx → pdf (LibreOffice)
    import tempfile, subprocess
    with tempfile.TemporaryDirectory() as tmpdir:
        docx_path = os.path.join(tmpdir, "cover.docx")
        with open(docx_path, "wb") as f:
            f.write(cover_docx)

        scripts_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "office", "soffice.py")
        if os.path.exists(scripts_path):
            subprocess.run(
                ["python3", scripts_path, "--headless",
                 "--convert-to", "pdf", "--outdir", tmpdir, docx_path],
                capture_output=True
            )
            pdf_path = os.path.join(tmpdir, "cover.pdf")
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    cover_bytes = f.read()
            else:
                cover_bytes = None
        else:
            cover_bytes = None

    # stamp header (ลำดับ 1 สำหรับ preview)
    stamped = stamp_exam_header(exam_bytes, student_order=1)

    # รวม PDF
    if cover_bytes:
        preview_pdf = merge_exam_with_cover(stamped, cover_bytes)
    else:
        # ถ้า convert ไม่ได้ ส่งแค่ข้อสอบ + header
        preview_pdf = stamped

    course_id  = course.course_id if course else "exam"
    section_no = sec.section_no
    return StreamingResponse(
        io.BytesIO(preview_pdf),
        media_type="application/pdf",
        headers={"Content-Disposition":
                 f'inline; filename="preview_{course_id}_sec{section_no}.pdf"'},
    )


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
    current_user: models.User = Depends(require_staff_or_admin),
):
    schedule = _load_schedule(db, schedule_id)
    ensure_schedule_ready_for_pickup(db, schedule)
    active_qr = get_active_pickup_qr(db, schedule_id)
    latest_qr = get_latest_pickup_qr(db, schedule_id)
    return {
        "schedule": _serialize_schedule_summary(schedule, db),
        "assignments": build_pickup_assignments(db, schedule),
        "active_qr": serialize_pickup_qr(active_qr),
        "latest_qr": serialize_pickup_qr(latest_qr),
        "has_pending_regeneration": bool(latest_qr and not latest_qr.is_active),
    }


@router.post("/pickup-qr/{schedule_id}/regenerate")
def regenerate_pickup_qr(
    schedule_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
):
    schedule = _load_schedule(db, schedule_id)
    ensure_schedule_ready_for_pickup(db, schedule)
    pending_qr = create_pickup_qr(db, schedule, actor_id=current_user.id, activate=False)
    db.commit()
    db.refresh(pending_qr)
    log_action(
        db,
        current_user,
        "REGENERATE_PICKUP_QR",
        "exam_pickup_qr_tokens",
        record_id=pending_qr.id,
        new_values={"schedule_id": schedule_id, "version": pending_qr.version},
        request=request,
    )
    return {
        "schedule": _serialize_schedule_summary(schedule, db),
        "assignments": build_pickup_assignments(db, schedule),
        "active_qr": serialize_pickup_qr(get_active_pickup_qr(db, schedule_id)),
        "latest_qr": serialize_pickup_qr(get_latest_pickup_qr(db, schedule_id)),
        "pending_qr": serialize_pickup_qr(pending_qr),
        "has_pending_regeneration": True,
    }


@router.post("/pickup-qr/{schedule_id}/confirm")
def confirm_pickup_qr(
    schedule_id: int,
    request: Request,
    qr_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_staff_or_admin),
):
    schedule = _load_schedule(db, schedule_id)
    ensure_schedule_ready_for_pickup(db, schedule)

    if qr_id is not None:
        qr_token = db.query(models.ExamPickupQrToken).filter(
            models.ExamPickupQrToken.id == qr_id,
            models.ExamPickupQrToken.schedule_id == schedule_id,
        ).first()
    else:
        qr_token = get_latest_pickup_qr(db, schedule_id)

    if not qr_token:
        raise HTTPException(404, "ไม่พบ QR X สำหรับ schedule นี้")

    activate_pickup_qr(db, qr_token, actor_id=current_user.id)
    db.commit()
    db.refresh(qr_token)
    log_action(
        db,
        current_user,
        "CONFIRM_PICKUP_QR",
        "exam_pickup_qr_tokens",
        record_id=qr_token.id,
        new_values={"schedule_id": schedule_id, "version": qr_token.version},
        request=request,
    )
    return {
        "schedule": _serialize_schedule_summary(schedule, db),
        "assignments": build_pickup_assignments(db, schedule),
        "active_qr": serialize_pickup_qr(qr_token),
        "latest_qr": serialize_pickup_qr(get_latest_pickup_qr(db, schedule_id)),
        "has_pending_regeneration": False,
    }


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
    current_user: models.User = Depends(require_staff_or_admin),
):
    try:
        normalized_type = normalize_document_type(document_type)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

    schedules = _load_export_schedules(
        db,
        schedule_id=schedule_id,
        course_id=course_id,
        section_no=section_no,
        room_id=room_id,
        academic_year=academic_year,
        semester=semester,
        exam_type=exam_type,
    )
    if not schedules:
        raise HTTPException(404, "ไม่พบตารางสอบที่ตรงกับเงื่อนไขสำหรับการส่งออกเอกสาร")

    outputs: list[tuple[str, bytes]] = []
    for schedule in schedules:
        payload = _build_operational_document_payload(
            db,
            schedule,
            actor_id=current_user.id,
            include_qr=normalized_type in {"all", "envelope_cover"},
        )
        for item_type in iter_document_types(normalized_type):
            pdf_bytes = _generate_operational_document_bytes(item_type, payload)
            outputs.append((build_document_filename(item_type, payload), pdf_bytes))

    log_action(
        db,
        current_user,
        "EXPORT_OPERATIONAL_DOCUMENTS",
        "exam_schedules",
        record_id=schedule_id,
        new_values={
            "document_type": normalized_type,
            "count": len(outputs),
            "course_id": course_id,
            "section_no": section_no,
            "room_id": room_id,
        },
        request=request,
    )

    if len(outputs) == 1:
        file_name, pdf_bytes = outputs[0]
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
        )

    scope_bits = [
        course_id or "all-courses",
        section_no or "all-sections",
        str(room_id) if room_id is not None else "all-rooms",
    ]
    scope_label = "_".join(scope_bits)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_name, pdf_bytes in outputs:
            archive.writestr(file_name, pdf_bytes)
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{build_bundle_filename(scope_label, normalized_type)}"'},
    )
