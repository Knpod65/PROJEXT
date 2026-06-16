"""Document domain service.

Routes call into this service for document assembly, preview payloads,
operational exports, and pickup QR orchestration.
"""
from __future__ import annotations

import io
import math
import os
import subprocess
import sys
import tempfile
import zipfile
from typing import Optional

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

import models
from auth_utils import log_action
from exam_pdf_processor import merge_exam_with_cover, split_students_by_room, stamp_exam_header
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
from gen_docs import generate_cover_page, generate_envelope_cover, generate_attendance_sheet
from operational_documents import (
    build_bundle_filename,
    build_document_filename,
    generate_envelope_cover_pdf,
    generate_participant_code_announcement_pdf,
    generate_signature_sheet_pdf,
    iter_document_types,
    normalize_document_type,
)
from repositories.document_repository import (
    load_enrollment_records,
    load_export_schedules,
    load_legacy_enrollments,
    load_period,
    load_published_schedules,
    load_schedule,
    load_submission,
    load_submission_schedule,
)
from serializers.document_serializer import (
    serialize_document_preview,
    serialize_exam_print_info,
    serialize_pickup_qr_bundle,
    serialize_schedule_summary,
)
from services.thai_export_service import binary_streaming_response


QR_IMAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "qr_regulation.png")


class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_generators_available(self) -> None:
        if generate_cover_page and generate_envelope_cover and generate_attendance_sheet:
            return
        raise HTTPException(503, "Document generation dependencies are unavailable in this local environment.")

    @staticmethod
    def _safe_filename(value: str) -> str:
        import re
        return re.sub(r"[^\w\-.]", "_", value)

    def _build_docs(self, schedule: models.ExamSchedule) -> dict[str, object]:
        self._ensure_generators_available()
        section = schedule.section
        course = section.course if section else None
        teacher = section.teacher if section else None
        room = schedule.room

        course_id = course.course_id if course else "UNKNOWN"
        section_no = section.section_no if section else "?"
        exam_date = schedule.exam_date or "2026-01-01"
        exam_time = schedule.exam_time or "00.00-00.00"
        room_name = room.room_name if room else "?"
        teacher_name = teacher.full_name if teacher else "-"
        num_students = section.num_students if section else 0
        exam_type = schedule.exam_type.value if schedule.exam_type else "final"
        semester = section.semester if section else "2"
        acad_year = section.academic_year if section else "2568"

        supervisors = [
            {"name": sup.user.full_name or "", "slot_order": sup.slot_order}
            for sup in sorted(schedule.supervisions or [], key=lambda s: s.slot_order)
            if sup.user
        ]

        enrollment_records = load_enrollment_records(self.db, section.id) if section else []
        students = [{"student_id": r.student_id, "student_name": r.student_name} for r in enrollment_records]
        if not students:
            students = [
                {"student_id": f"xxxxxxx{i:04d}", "student_name": f"(นักศึกษาลำดับที่ {i})"}
                for i in range(1, num_students + 1)
            ]

        prefix = self._safe_filename(f"{course_id}_ตอน{section_no}_{room_name}")
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
            "cover_page": generate_cover_page(**common, course_name_th=course.course_name_th if course else ""),
            "envelope": generate_envelope_cover(
                **common,
                teacher_name=teacher_name,
                supervisors=supervisors,
                num_students=num_students,
                num_exam_sets=num_students,
                qr_image_path=qr_path,
            ),
            "attendance": generate_attendance_sheet(**common, teacher_name=teacher_name, students=students),
            "filename_prefix": prefix,
        }

    def generate_documents(self, schedule_id: int, request: Request, current_user: models.User, doc_type: str = "all"):
        schedule = load_schedule(self.db, schedule_id)
        if not schedule:
            raise HTTPException(404, f"ไม่พบ schedule id={schedule_id}")
        docs = self._build_docs(schedule)
        prefix = docs["filename_prefix"]

        log_action(self.db, current_user, "GENERATE_DOCUMENTS", "exam_schedules", record_id=schedule_id, new_values={"doc_type": doc_type}, request=request)

        if doc_type == "cover_page":
            filename = f"ใบปะหน้า_{prefix}.docx"
            return binary_streaming_response(docs["cover_page"], media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=filename)
        if doc_type == "envelope":
            filename = f"ปกซอง_{prefix}.docx"
            return binary_streaming_response(docs["envelope"], media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=filename)
        if doc_type == "attendance":
            filename = f"ใบลงมือชื่อ_{prefix}.docx"
            return binary_streaming_response(docs["attendance"], media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=filename)

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"ใบปะหน้า_{prefix}.docx", docs["cover_page"])
            zf.writestr(f"ปกซอง_{prefix}.docx", docs["envelope"])
            zf.writestr(f"ใบลงมือชื่อ_{prefix}.docx", docs["attendance"])
        zip_buf.seek(0)
        return binary_streaming_response(zip_buf, media_type="application/zip", filename=f"เอกสารสอบ_{prefix}.zip")

    def generate_batch_documents(self, request: Request, current_user: models.User, *, semester: str, academic_year: str, exam_type: str, doc_type: str = "all"):
        exam_type_enum = models.ExamType.final if exam_type == "final" else models.ExamType.midterm
        schedules = load_published_schedules(self.db, semester=semester, academic_year=academic_year, exam_type=exam_type_enum)
        if not schedules:
            raise HTTPException(404, "ไม่พบ schedule ที่ publish แล้วในช่วงเวลาที่เลือก")

        log_action(self.db, current_user, "GENERATE_BATCH_DOCUMENTS", "exam_schedules", new_values={"semester": semester, "academic_year": academic_year, "exam_type": exam_type, "doc_type": doc_type, "count": len(schedules)}, request=request)

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for schedule in schedules:
                try:
                    docs = self._build_docs(schedule)
                    prefix = docs["filename_prefix"]
                    date = schedule.exam_date or "nodate"
                    folder = f"{date}/"
                    if doc_type in ("cover_page", "all"):
                        zf.writestr(f"{folder}ใบปะหน้า_{prefix}.docx", docs["cover_page"])
                    if doc_type in ("envelope", "all"):
                        zf.writestr(f"{folder}ปกซอง_{prefix}.docx", docs["envelope"])
                    if doc_type in ("attendance", "all"):
                        zf.writestr(f"{folder}ใบลงมือชื่อ_{prefix}.docx", docs["attendance"])
                except Exception as exc:
                    zf.writestr(f"ERROR_{schedule.id}.txt", str(exc))

        zip_buf.seek(0)
        exam_type_th = "ปลายภาค" if exam_type == "final" else "กลางภาค"
        fname = f"เอกสารสอบ_{exam_type_th}_{academic_year}_ภาค{semester}.zip"
        return binary_streaming_response(zip_buf, media_type="application/zip", filename=fname)

    def preview_document_info(self, schedule_id: int) -> dict[str, object]:
        schedule = load_schedule(self.db, schedule_id)
        if not schedule:
            raise HTTPException(404, f"ไม่พบ schedule id={schedule_id}")
        enrollment_count = len(load_enrollment_records(self.db, schedule.section.id)) if schedule.section else 0
        return serialize_document_preview(schedule, enrollment_count)

    def get_exam_print_info(self, submission_id: int) -> dict[str, object]:
        submission = load_submission(self.db, submission_id)
        if not submission:
            raise HTTPException(404, "ไม่พบ submission")
        if submission.status not in (models.SubmissionStatus.approved, models.SubmissionStatus.released):
            raise HTTPException(400, f"submission ยังไม่ได้ approve (status={submission.status.value})")

        section = submission.section
        schedule = load_submission_schedule(self.db, section.id) if section else None

        exam_pages = 0
        if submission.pdf_stripped_path and os.path.exists(submission.pdf_stripped_path):
            from pypdf import PdfReader as _R
            exam_pages = len(_R(submission.pdf_stripped_path).pages)
        elif submission.pdf_original_path and os.path.exists(submission.pdf_original_path):
            from pypdf import PdfReader as _R
            exam_pages = len(_R(submission.pdf_original_path).pages)
        elif submission.a4_pages_count:
            exam_pages = submission.a4_pages_count

        cover_pages = 2
        total_pages = exam_pages + cover_pages
        num_students = section.num_students if section else 0
        buffer_pct = self._get_buffer_pct()
        buffer_sets = math.ceil(num_students * buffer_pct / 100)
        print_sets = num_students + buffer_sets
        print_sheets = print_sets * total_pages

        students = self._get_students_sorted(section.id) if section else []
        room_caps = self._get_room_capacities(schedule) if schedule else []
        splits = split_students_by_room(students, room_caps) if (students and room_caps) else []

        staple_labels = {
            "none": "ไม่เย็บ",
            "corner_left": "เย็บมุมบนซ้าย",
            "side_left": "เย็บกลางซ้าย (2 จุด)",
            "custom": f"เย็บแยกที่หน้า {submission.print_staple_page}",
        }
        physical_sheets = math.ceil(total_pages / 2) if submission.print_duplex else total_pages
        physical_total = print_sets * physical_sheets

        material_request = None
        if hasattr(submission, "material_request") and submission.material_request:
            mr = submission.material_request
            material_request = {
                "answer_paper_sheets": mr.answer_paper_sheets,
                "answer_paper_staple": mr.answer_paper_staple,
                "answer_booklet_count": mr.answer_booklet_count,
                "omr_sheet_count": mr.omr_sheet_count,
                "omr_form_code": mr.omr_form_code,
                "scratch_paper_sheets": mr.scratch_paper_sheets,
                "special_note": mr.special_note,
                "answer_paper_total": mr.answer_paper_sheets * print_sets if mr.answer_paper_sheets else 0,
                "booklet_total": mr.answer_booklet_count * print_sets if mr.answer_booklet_count else 0,
                "omr_total": mr.omr_sheet_count * print_sets if mr.omr_sheet_count else 0,
                "scratch_total": mr.scratch_paper_sheets * print_sets if mr.scratch_paper_sheets else 0,
            }

        print_spec = {
            "duplex": submission.print_duplex or False,
            "staple": submission.print_staple or "none",
            "staple_label": staple_labels.get(submission.print_staple or "none", "ไม่เย็บ"),
            "staple_page": submission.print_staple_page,
            "note": submission.print_note or "",
            "spec_confirmed": submission.print_spec_confirmed or False,
            "physical_sheets_per_set": physical_sheets,
            "physical_sheets_total": physical_total,
            "duplex_label": "พิมพ์หน้า-หลัง (Duplex)" if submission.print_duplex else "พิมพ์หน้าเดียว (Simplex)",
        }

        room_splits = [
            {"room_name": r["room_name"], "count": r["count"], "start_order": r["start_order"], "end_order": r["end_order"]}
            for r in splits
        ]

        return serialize_exam_print_info(
            submission,
            exam_pages=exam_pages,
            cover_pages=cover_pages,
            total_pages=total_pages,
            num_students=num_students,
            buffer_pct=buffer_pct,
            buffer_sets=buffer_sets,
            print_sets=print_sets,
            print_sheets=print_sheets,
            material_request=material_request,
            print_spec=print_spec,
            enrollment_ready=len(students) > 0,
            room_splits=room_splits,
        )

    def generate_preview_pdf(self, submission_id: int, request: Request, current_user: models.User):
        submission = load_submission(self.db, submission_id)
        if not submission:
            raise HTTPException(404, "ไม่พบ submission")
        log_action(self.db, current_user, "PREVIEW_SUBMISSION_PDF", "exam_submissions", record_id=submission_id, request=request)

        section = submission.section
        schedule = load_submission_schedule(self.db, section.id) if section else None
        if not schedule:
            raise HTTPException(400, "ยังไม่มีตารางสอบ — ต้อง optimize ก่อน")

        exam_bytes = self._get_exam_pdf(submission)
        course = section.course if section else None
        teacher = section.teacher if section else None
        _ = teacher

        from gen_docs import generate_cover_page
        cover_docx = generate_cover_page(
            course_id=course.course_id if course else "?",
            course_name_th=course.course_name_th if course else "",
            section_no=section.section_no,
            exam_date=schedule.exam_date,
            exam_time=schedule.exam_time,
            room_name=schedule.room.room_name if schedule.room else "?",
            exam_type=schedule.exam_type.value,
            semester=section.semester,
            academic_year=section.academic_year,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = os.path.join(tmpdir, "cover.docx")
            with open(docx_path, "wb") as f:
                f.write(cover_docx)
            scripts_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "office", "soffice.py")
            if os.path.exists(scripts_path):
                subprocess.run(["python3", scripts_path, "--headless", "--convert-to", "pdf", "--outdir", tmpdir, docx_path], capture_output=True)
                pdf_path = os.path.join(tmpdir, "cover.pdf")
                cover_bytes = open(pdf_path, "rb").read() if os.path.exists(pdf_path) else None
            else:
                cover_bytes = None

        stamped = stamp_exam_header(exam_bytes, student_order=1)
        preview_pdf = merge_exam_with_cover(stamped, cover_bytes) if cover_bytes else stamped
        course_id = course.course_id if course else "exam"
        section_no = section.section_no
        return binary_streaming_response(
            preview_pdf,
            media_type="application/pdf",
            filename=f"preview_{course_id}_sec{section_no}.pdf",
            disposition="inline",
        )

    def get_pickup_qr_status(self, schedule_id: int):
        schedule = load_schedule(self.db, schedule_id)
        if not schedule:
            raise HTTPException(404, f"ไม่พบ schedule id={schedule_id}")
        ensure_schedule_ready_for_pickup(self.db, schedule)
        active_qr = get_active_pickup_qr(self.db, schedule_id)
        latest_qr = get_latest_pickup_qr(self.db, schedule_id)
        teacher = get_confirmed_section_owner(self.db, schedule)
        return serialize_pickup_qr_bundle(
            schedule,
            build_pickup_assignments(self.db, schedule),
            serialize_pickup_qr(active_qr),
            serialize_pickup_qr(latest_qr),
            teacher=teacher,
            has_pending_regeneration=bool(latest_qr and not latest_qr.is_active),
        )

    def regenerate_pickup_qr(self, schedule_id: int, request: Request, current_user: models.User):
        schedule = load_schedule(self.db, schedule_id)
        if not schedule:
            raise HTTPException(404, f"ไม่พบ schedule id={schedule_id}")
        ensure_schedule_ready_for_pickup(self.db, schedule)
        pending_qr = create_pickup_qr(self.db, schedule, actor_id=current_user.id, activate=False)
        self.db.commit()
        self.db.refresh(pending_qr)
        log_action(self.db, current_user, "REGENERATE_PICKUP_QR", "exam_pickup_qr_tokens", record_id=pending_qr.id, new_values={"schedule_id": schedule_id, "version": pending_qr.version}, request=request)
        return {
            "schedule": serialize_schedule_summary(schedule),
            "assignments": build_pickup_assignments(self.db, schedule),
            "active_qr": serialize_pickup_qr(get_active_pickup_qr(self.db, schedule_id)),
            "latest_qr": serialize_pickup_qr(get_latest_pickup_qr(self.db, schedule_id)),
            "pending_qr": serialize_pickup_qr(pending_qr),
            "has_pending_regeneration": True,
        }

    def confirm_pickup_qr(self, schedule_id: int, request: Request, current_user: models.User, qr_id: Optional[int] = None):
        schedule = load_schedule(self.db, schedule_id)
        if not schedule:
            raise HTTPException(404, f"ไม่พบ schedule id={schedule_id}")
        ensure_schedule_ready_for_pickup(self.db, schedule)
        if qr_id is not None:
            qr_token = self.db.query(models.ExamPickupQrToken).filter(models.ExamPickupQrToken.id == qr_id, models.ExamPickupQrToken.schedule_id == schedule_id).first()
        else:
            qr_token = get_latest_pickup_qr(self.db, schedule_id)
        if not qr_token:
            raise HTTPException(404, "ไม่พบ QR X สำหรับ schedule นี้")
        activate_pickup_qr(self.db, qr_token, actor_id=current_user.id)
        self.db.commit()
        self.db.refresh(qr_token)
        log_action(self.db, current_user, "CONFIRM_PICKUP_QR", "exam_pickup_qr_tokens", record_id=qr_token.id, new_values={"schedule_id": schedule_id, "version": qr_token.version}, request=request)
        return {
            "schedule": serialize_schedule_summary(schedule),
            "assignments": build_pickup_assignments(self.db, schedule),
            "active_qr": serialize_pickup_qr(qr_token),
            "latest_qr": serialize_pickup_qr(get_latest_pickup_qr(self.db, schedule_id)),
            "has_pending_regeneration": False,
        }

    def export_operational_documents(self, request: Request, current_user: models.User, *, schedule_id: Optional[int] = None, course_id: Optional[str] = None, section_no: Optional[str] = None, room_id: Optional[int] = None, academic_year: Optional[str] = None, semester: Optional[str] = None, exam_type: Optional[str] = None, document_type: str = "all"):
        try:
            normalized_type = normalize_document_type(document_type)
        except ValueError as exc:
            raise HTTPException(400, str(exc))
        if schedule_id is not None:
            schedules = [load_schedule(self.db, schedule_id)]
        else:
            period = load_period(self.db, academic_year=academic_year, semester=semester, exam_type=exam_type)
            if not period:
                raise HTTPException(404, "ไม่พบภาคสอบที่ต้องการสำหรับการสร้างเอกสาร")
            schedules = load_export_schedules(self.db, period=period, course_id=course_id, section_no=section_no, room_id=room_id)
        schedules = [s for s in schedules if s]
        if not schedules:
            raise HTTPException(404, "ไม่พบตารางสอบที่ตรงกับเงื่อนไขสำหรับการส่งออกเอกสาร")

        outputs: list[tuple[str, bytes]] = []
        for schedule in schedules:
            payload = self._build_operational_document_payload(schedule, include_qr=normalized_type in {"all", "envelope_cover"}, actor_id=current_user.id)
            for item_type in iter_document_types(normalized_type):
                pdf_bytes = self._generate_operational_document_bytes(item_type, payload)
                outputs.append((build_document_filename(item_type, payload), pdf_bytes))

        log_action(self.db, current_user, "EXPORT_OPERATIONAL_DOCUMENTS", "exam_schedules", record_id=schedule_id, new_values={"document_type": normalized_type, "count": len(outputs), "course_id": course_id, "section_no": section_no, "room_id": room_id}, request=request)

        if len(outputs) == 1:
            file_name, pdf_bytes = outputs[0]
            return binary_streaming_response(pdf_bytes, media_type="application/pdf", filename=file_name)

        scope_bits = [course_id or "all-courses", section_no or "all-sections", str(room_id) if room_id is not None else "all-rooms"]
        scope_label = "_".join(scope_bits)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for file_name, pdf_bytes in outputs:
                archive.writestr(file_name, pdf_bytes)
        zip_buffer.seek(0)
        return binary_streaming_response(zip_buffer, media_type="application/zip", filename=build_bundle_filename(scope_label, normalized_type))

    def _get_buffer_pct(self) -> float:
        from routers.settings import get_setting
        val = get_setting(self.db, "printshop_copies_buffer")
        try:
            return float(val) if val else 5.0
        except Exception:
            return 5.0

    def _get_exam_pdf(self, submission: models.ExamSubmission) -> bytes:
        path = submission.pdf_stripped_path or submission.pdf_original_path
        if not path or not os.path.exists(path):
            raise HTTPException(404, "ไม่พบไฟล์ PDF ข้อสอบ — อาจารย์ยังไม่ได้ upload หรือไฟล์หาย")
        with open(path, "rb") as f:
            return f.read()

    def _get_students_sorted(self, section_id: int) -> list[dict[str, str]]:
        rows = load_enrollment_records(self.db, section_id)
        if rows:
            return [{"student_id": r.student_id, "student_name": r.student_name or ""} for r in rows]
        legacy_rows = load_legacy_enrollments(self.db, section_id)
        return [{"student_id": row.student_id, "student_name": row.student.full_name if row.student else ""} for row in legacy_rows]

    def _get_room_capacities(self, schedule: models.ExamSchedule) -> list[dict[str, object]]:
        section = schedule.section
        if not section:
            return []
        all_schedules = (
            self.db.query(models.ExamSchedule)
            .options(joinedload(models.ExamSchedule.room))
            .filter(models.ExamSchedule.section_id == section.id, models.ExamSchedule.exam_type == schedule.exam_type)
            .order_by(models.ExamSchedule.id)
            .all()
        )
        rooms = []
        for sch in all_schedules:
            if sch.room:
                rooms.append({"room_name": sch.room.room_name, "capacity": sch.room.capacity, "schedule_id": sch.id})
        if not rooms and schedule.room:
            rooms = [{"room_name": schedule.room.room_name, "capacity": schedule.room.capacity, "schedule_id": schedule.id}]
        return rooms

    def _build_operational_document_payload(self, schedule: models.ExamSchedule, *, include_qr: bool, actor_id: int) -> dict[str, object]:
        ensure_schedule_ready_for_pickup(self.db, schedule)
        section = schedule.section
        course = section.course if section and section.course else None
        room = schedule.room
        teacher = get_confirmed_section_owner(self.db, schedule)
        students = self._get_students_sorted(section.id) if section else []
        invigilators = [
            {"name": supervision.user.full_name or supervision.user.username, "role": supervision.role_in_exam or "invigilator"}
            for supervision in sorted(schedule.supervisions or [], key=lambda item: item.slot_order or 0)
            if supervision.user
        ]
        if include_qr and not invigilators:
            raise HTTPException(400, "ยังไม่ได้ยืนยันผู้คุมสอบหรือผู้รับข้อสอบสำหรับการพิมพ์ปกซองข้อสอบ")
        active_qr = ensure_active_pickup_qr(self.db, schedule, actor_id=actor_id) if include_qr else None
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

    @staticmethod
    def _generate_operational_document_bytes(document_type: str, payload: dict[str, object]) -> bytes:
        if document_type == "participant_codes":
            return generate_participant_code_announcement_pdf(payload)
        if document_type == "signature_sheet":
            return generate_signature_sheet_pdf(payload)
        if document_type == "envelope_cover":
            return generate_envelope_cover_pdf(payload)
        raise HTTPException(400, f"Unsupported document type: {document_type}")
