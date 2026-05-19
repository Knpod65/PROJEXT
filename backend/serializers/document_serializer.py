"""Document response serializers.

All functions here are pure and PDPA-aware by default.
"""
from __future__ import annotations

from typing import Any

import models


def _course_name(course: Any) -> str | None:
    if not course:
        return None
    return getattr(course, "course_name_th", None) or getattr(course, "course_name_en", None)


def serialize_schedule_summary(schedule: models.ExamSchedule, teacher: Any = None) -> dict[str, object]:
    section = schedule.section
    course = section.course if section else None
    return {
        "id": schedule.id,
        "course_code": course.course_id if course else None,
        "course_name": _course_name(course),
        "section_no": section.section_no if section else None,
        "exam_date": schedule.exam_date.isoformat() if hasattr(schedule.exam_date, "isoformat") else str(schedule.exam_date),
        "exam_time": schedule.exam_time,
        "room_name": schedule.room.room_name if schedule.room else None,
        "teacher_name": teacher.full_name if teacher else None,
        "status": schedule.status.value if hasattr(schedule.status, "value") else str(schedule.status),
    }


def serialize_pickup_qr_bundle(
    schedule: models.ExamSchedule,
    assignments: list[dict[str, object]],
    active_qr: dict[str, object] | None,
    latest_qr: dict[str, object] | None,
    *,
    teacher: Any = None,
    has_pending_regeneration: bool,
) -> dict[str, object]:
    return {
        "schedule": serialize_schedule_summary(schedule, teacher=teacher),
        "assignments": assignments,
        "active_qr": active_qr,
        "latest_qr": latest_qr,
        "has_pending_regeneration": has_pending_regeneration,
    }


def serialize_document_preview(
    schedule: models.ExamSchedule,
    enrollment_count: int,
) -> dict[str, object]:
    section = schedule.section
    course = section.course if section else None
    supervisors = [
        {"name": s.user.full_name, "slot": s.slot_order}
        for s in sorted(schedule.supervisions or [], key=lambda x: x.slot_order)
        if s.user
    ]
    return {
        "schedule_id": schedule.id,
        "course_id": course.course_id if course else None,
        "course_name_th": course.course_name_th if course else None,
        "section_no": section.section_no if section else None,
        "exam_date": schedule.exam_date,
        "exam_time": schedule.exam_time,
        "room": schedule.room.room_name if schedule.room else None,
        "teacher": section.teacher.full_name if section and section.teacher else None,
        "num_students": section.num_students if section else 0,
        "enrollment_records": enrollment_count,
        "supervisors": supervisors,
        "status": schedule.status.value if schedule.status else None,
        "ready": enrollment_count > 0,
        "note": None if enrollment_count > 0 else f"⚠ ยังไม่มี enrollment records — ใบลงมือชื่อจะใช้ placeholder {section.num_students if section else 0} คน",
    }


def serialize_exam_print_info(
    submission: models.ExamSubmission,
    *,
    exam_pages: int,
    cover_pages: int,
    total_pages: int,
    num_students: int,
    buffer_pct: float,
    buffer_sets: int,
    print_sets: int,
    print_sheets: int,
    material_request: dict[str, object] | None,
    print_spec: dict[str, object],
    enrollment_ready: bool,
    room_splits: list[dict[str, object]],
) -> dict[str, object]:
    section = submission.section
    course = section.course if section and section.course else None
    return {
        "submission_id": submission.id,
        "course_id": section.course.course_id if section and section.course else None,
        "section_no": section.section_no if section else None,
        "exam_pages": exam_pages,
        "cover_pages": cover_pages,
        "total_pages": total_pages,
        "num_students": num_students,
        "buffer_pct": buffer_pct,
        "buffer_sets": buffer_sets,
        "print_sets": print_sets,
        "print_sheets": print_sheets,
        "material_request": material_request,
        "print_spec": print_spec,
        "enrollment_ready": enrollment_ready,
        "room_splits": room_splits,
    }
