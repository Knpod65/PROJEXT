"""
schedule_serializer.py — pure serializer functions for schedule API responses.

All functions are side-effect-free — no DB access, no auth checks, no logging.
Backward-compatible: serialize_schedule re-exports from schedule_query_service
so existing callers in schedule.py continue to work unchanged.
"""
from __future__ import annotations

import models


# ── Re-export from query service for backward compatibility ──
def serialize_schedule(schedule: models.ExamSchedule) -> dict:
    """Serialize a single ExamSchedule ORM row. Canonical implementation lives in schedule_query_service."""
    from services.schedule_query_service import serialize_schedule as _inner
    return _inner(schedule)


def serialize_public_schedule(schedule: models.ExamSchedule) -> dict:
    """Public-safe schedule view — strips PII fields.

    Removed vs serialize_schedule:
      - teacher.full_name
      - teacher.id (replaced with hashed display id)
      - supervision.user.full_name
    """
    sec = schedule.section
    course = sec.course if sec else None
    room = schedule.room
    supervisions = schedule.supervisions or []

    def _hash_id(n: int | None) -> str:
        return f"staff-{abs((n or 0) * 2654435761) % 100000000:08d}"

    return {
        "id": schedule.id,
        "exam_date": schedule.exam_date,
        "exam_time": schedule.exam_time,
        "status": schedule.status,
        "num_pages": schedule.num_pages,
        "total_sheets": schedule.total_sheets,
        "room": (
            {"id": room.id, "room_name": room.room_name, "capacity": room.capacity}
            if room else None
        ),
        "section": (
            {
                "id": sec.id,
                "section_no": sec.section_no,
                "num_students": sec.num_students,
                "is_co_exam": sec.is_co_exam,
            }
            if sec else None
        ),
        "course": (
            {"course_id": course.course_id, "course_name_th": course.course_name_th}
            if course else None
        ),
        "teacher": (
            {"id": _hash_id(teacher.id), "display_id": f"staff-{teacher.id}"}
            if teacher else None
        ),
        "supervisions": [
            {
                "slot_order": sup.slot_order,
                "user": (
                    {"id": _hash_id(sup.user.id), "display_id": f"staff-{sup.user.id}"}
                    if sup.user else None
                ),
                "confirmed": sup.confirmed,
            }
            for sup in supervisions
        ],
    }


def serialize_schedule_group(group: dict) -> dict:
    """Re-serialize a grouped-schedule dict (date + items) using public serializer."""
    return {
        "date": group["date"],
        "items": [serialize_public_schedule(item) for item in group.get("items", [])],
    }


def serialize_copy_count_row(row: dict) -> dict:
    """Pass-through for copy-count rows. Strips nothing; row is already non-PII."""
    return row


def serialize_copy_count_summary(summary: dict) -> dict:
    """Return a copy-count summary envelope. Preserves all existing fields exactly."""
    return {
        "rows": [serialize_copy_count_row(r) for r in summary.get("rows", [])],
        "subtotal_exam": summary.get("subtotal_exam", 0),
        "fraud_forms": summary.get("fraud_forms", 0),
        "grand_total": summary.get("grand_total", 0),
        "cost": summary.get("cost", 0.0),
        "sections_count": summary.get("sections_count", 0),
    }
