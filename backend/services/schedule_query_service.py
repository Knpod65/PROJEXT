"""
schedule_query_service.py — schedule query orchestration.
"""
from __future__ import annotations

from fastapi import HTTPException

import models
from policies.schedule_policy import apply_schedule_scope
from repositories.schedule_repository import build_schedule_base_query, load_unavailability_maps
from time_ranges import parse_time_range, ranges_overlap


def build_schedule_query(
    db,
    current_user: models.User,
    exam_date: str | None = None,
    room_id: int | None = None,
    status: str | None = None,
):
    query = build_schedule_base_query(db)

    if exam_date:
        query = query.filter(models.ExamSchedule.exam_date == exam_date)
    if room_id is not None:
        query = query.filter(models.ExamSchedule.room_id == room_id)
    if status:
        try:
            query = query.filter(models.ExamSchedule.status == models.ScheduleStatus(status))
        except ValueError:
            raise HTTPException(400, f"status ไม่ถูกต้อง: {status}")

    return apply_schedule_scope(query, db, current_user)


def serialize_schedule(schedule: models.ExamSchedule) -> dict:
    sec = schedule.section
    course = sec.course if sec else None
    teacher = sec.teacher if sec else None
    room = schedule.room
    supervisions = schedule.supervisions or []

    def _enum_value(value):
        return value.value if hasattr(value, "value") else value

    def _user_payload(user):
        if not user:
            return None
        return {
            "id": user.id,
            "username": getattr(user, "username", f"user-{user.id}"),
            "email": getattr(user, "email", f"user-{user.id}@example.invalid"),
            "full_name": getattr(user, "full_name", None),
            "role": _enum_value(getattr(user, "role", models.UserRole.staff)),
            "department": getattr(user, "department", None),
            "dept_code": getattr(user, "dept_code", None),
            "is_active": bool(getattr(user, "is_active", True)),
            "created_at": getattr(user, "created_at", None),
        }

    def _room_payload(room_obj):
        if not room_obj:
            return None
        return {
            "id": room_obj.id,
            "room_name": room_obj.room_name,
            "building": getattr(room_obj, "building", None),
            "capacity": getattr(room_obj, "capacity", 0),
            "e_room_code": getattr(room_obj, "e_room_code", None),
            "is_active": bool(getattr(room_obj, "is_active", True)),
        }

    def _course_payload(course_obj):
        if not course_obj:
            return None
        return {
            "id": getattr(course_obj, "id", 0),
            "course_id": course_obj.course_id,
            "course_name_th": getattr(course_obj, "course_name_th", None),
            "course_name_en": getattr(course_obj, "course_name_en", None),
            "credits": getattr(course_obj, "credits", 0) or 0,
            "department": getattr(course_obj, "department", None),
            "academic_group": getattr(course_obj, "academic_group", None),
            "academic_group_label": getattr(course_obj, "academic_group_label", None),
        }

    return {
        "id": schedule.id,
        "exam_date": schedule.exam_date,
        "exam_time": schedule.exam_time,
        "exam_type": _enum_value(getattr(schedule, "exam_type", None)),
        "status": _enum_value(schedule.status),
        "num_pages": schedule.num_pages,
        "total_sheets": schedule.total_sheets,
        "paper_distributor": schedule.paper_distributor,
        "notes": schedule.notes,
        "room": _room_payload(room),
        "section": {
            "id": sec.id,
            "section_no": sec.section_no,
            "num_students": sec.num_students,
            "is_co_exam": sec.is_co_exam,
            "co_group_id": getattr(sec, "co_group_id", None),
            "semester": getattr(sec, "semester", ""),
            "academic_year": getattr(sec, "academic_year", ""),
            "academic_group": getattr(sec, "academic_group", None),
            "academic_group_label": getattr(sec, "academic_group_label", None),
            "course": _course_payload(course),
            "teacher": _user_payload(teacher),
            "teaching_room": (
                _room_payload(sec.teaching_room)
                if sec and sec.teaching_room
                else None
            ),
        } if sec else None,
        "course": _course_payload(course),
        "teacher": _user_payload(teacher),
        "supervisions": [
            {
                "id": getattr(supervision, "id", 0),
                "role_in_exam": getattr(supervision, "role_in_exam", "supervisor"),
                "slot_order": supervision.slot_order,
                "compensation": float(getattr(supervision, "compensation", 0.0) or 0.0),
                "user": _user_payload(supervision.user) if supervision.user else None,
                "confirmed": supervision.confirmed,
                "is_swapped": bool(getattr(supervision, "is_swapped", False)),
                "is_emergency_sub": bool(getattr(supervision, "is_emergency_sub", False)),
                "swap_requested": bool(getattr(supervision, "swap_requested", False)),
            }
            for supervision in supervisions
        ],
    }


def group_schedules_by_date(schedules: list[models.ExamSchedule]) -> list[dict[str, object]]:
    grouped: dict[str, list[models.ExamSchedule]] = {}
    for schedule in schedules:
        grouped.setdefault(schedule.exam_date, []).append(schedule)
    result = []
    for exam_date in sorted(grouped.keys()):
        result.append(
            {
                "date": exam_date,
                "items": [serialize_schedule(item) for item in sorted(grouped[exam_date], key=lambda item: item.exam_time)],
            }
        )
    return result


def schedule_time_bounds(exam_time: str | None, start: str | None = None, end: str | None = None):
    if start and end:
        return start, end
    return parse_time_range(exam_time)


def is_room_unavailable(
    room_unavail_map,
    room_id: int,
    block_date,
    block_time: str | None,
    block_start: str | None = None,
    block_end: str | None = None,
) -> bool:
    if not room_unavail_map:
        return False
    blocked = room_unavail_map.get(room_id, [])
    key_date = str(block_date)
    slot_start, slot_end = schedule_time_bounds(block_time, block_start, block_end)
    for row in blocked:
        if row["date"] != key_date:
            continue
        if row["all_day"]:
            return True
        if row["block_time"] == block_time and row["block_time"] is not None:
            return True
        if ranges_overlap(slot_start, slot_end, row["start_time"], row["end_time"]):
            return True
    return False
