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
    return {
        "id": schedule.id,
        "exam_date": schedule.exam_date,
        "exam_time": schedule.exam_time,
        "status": schedule.status,
        "num_pages": schedule.num_pages,
        "total_sheets": schedule.total_sheets,
        "paper_distributor": schedule.paper_distributor,
        "notes": schedule.notes,
        "room": {"id": room.id, "room_name": room.room_name, "capacity": room.capacity} if room else None,
        "section": {
            "id": sec.id,
            "section_no": sec.section_no,
            "num_students": sec.num_students,
            "is_co_exam": sec.is_co_exam,
            "teaching_room": (
                {
                    "id": sec.teaching_room.id,
                    "room_name": sec.teaching_room.room_name,
                    "capacity": sec.teaching_room.capacity,
                    "building": sec.teaching_room.building,
                }
                if sec and sec.teaching_room
                else None
            ),
        } if sec else None,
        "course": {
            "course_id": course.course_id,
            "course_name_th": course.course_name_th,
        } if course else None,
        "teacher": {
            "id": teacher.id,
            "full_name": teacher.full_name,
        } if teacher else None,
        "supervisions": [
            {
                "slot_order": supervision.slot_order,
                "user": {"id": supervision.user.id, "full_name": supervision.user.full_name} if supervision.user else None,
                "confirmed": supervision.confirmed,
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
