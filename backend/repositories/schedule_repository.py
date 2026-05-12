"""
schedule_repository.py — database access helpers for schedules.
"""
from __future__ import annotations

from collections import defaultdict

from sqlalchemy.orm import joinedload

import models, schemas
from staff_workloads import build_staff_unavailability_map
from time_ranges import parse_time_range


def build_schedule_base_query(db):
    return db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.room),
        joinedload(models.ExamSchedule.supervisions).joinedload(models.Supervision.user),
        joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
        joinedload(models.ExamSchedule.section).joinedload(models.Section.teacher),
        joinedload(models.ExamSchedule.section).joinedload(models.Section.teaching_room),
    )


def load_unavailability_maps(db, data: schemas.OptimizerRequest):
    period = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.academic_year == data.academic_year,
        models.ExamPeriod.semester == data.semester,
        models.ExamPeriod.exam_type == data.exam_type.value,
    ).first()

    if not period:
        return {}, {}

    staff_map = build_staff_unavailability_map(db, period.id)
    room_map = defaultdict(list)

    for row in db.query(models.RoomUnavailability).filter(
        models.RoomUnavailability.exam_period_id == period.id
    ).all():
        start_time = getattr(row, "start_time", None)
        end_time = getattr(row, "end_time", None)
        if not (start_time and end_time):
            start_time, end_time = parse_time_range(row.block_time)
        room_map[row.room_id].append(
            {
                "date": str(row.block_date),
                "block_time": row.block_time or None,
                "start_time": start_time,
                "end_time": end_time,
                "all_day": row.block_time is None and not start_time and not end_time,
            }
        )

    return staff_map, room_map
