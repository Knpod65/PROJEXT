from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

import models
from auth_utils import is_room_keeper
from time_ranges import normalize_time_range, normalize_time_value, parse_time_range, ranges_overlap
from config.policy import (
    PAPER_DISTRIBUTION_DIVISION,
    PAPER_DISTRIBUTION_EXCLUDED_NAME_SNIPPETS,
    PAPER_DISTRIBUTION_EXCLUDED_USERNAMES,
)


def is_paper_distribution_candidate(user: models.User) -> bool:
    if user.role != models.UserRole.staff or not user.is_active:
        return False
    if user.division != PAPER_DISTRIBUTION_DIVISION:
        return False
    if user.username in PAPER_DISTRIBUTION_EXCLUDED_USERNAMES:
        return False
    full_name = (user.full_name or "").strip()
    if any(snippet in full_name for snippet in PAPER_DISTRIBUTION_EXCLUDED_NAME_SNIPPETS):
        return False
    if is_room_keeper(user):
        return False
    return True


def build_staff_unavailability_map(db: Session, period_id: int | None) -> dict[int, list[dict[str, Any]]]:
    if not period_id:
        return {}

    rows = db.query(models.StaffUnavailability).filter(
        models.StaffUnavailability.exam_period_id == period_id
    ).all()

    result: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        start_time = normalize_time_value(getattr(row, "start_time", None))
        end_time = normalize_time_value(getattr(row, "end_time", None))
        parsed_block_start, parsed_block_end = parse_time_range(row.block_time)
        block_time = normalize_time_range(start_time, end_time) or normalize_time_range(parsed_block_start, parsed_block_end) or row.block_time
        if not (start_time and end_time) and block_time:
            parsed_start, parsed_end = parse_time_range(block_time)
            start_time = start_time or parsed_start
            end_time = end_time or parsed_end
        result[row.user_id].append(
            {
                "date": str(row.block_date),
                "block_time": block_time or None,
                "start_time": start_time,
                "end_time": end_time,
                "all_day": block_time is None and not start_time and not end_time,
                "reason": row.reason,
            }
        )
    return dict(result)


def is_staff_unavailable(
    unavailability_map: dict[int, list[dict[str, Any]]] | None,
    user_id: int,
    block_date: str | Any,
    block_time: str | None,
    block_start: str | None = None,
    block_end: str | None = None,
) -> bool:
    if not unavailability_map:
        return False
    rows = unavailability_map.get(user_id, [])
    if not rows:
        return False

    target_date = str(block_date)
    slot_start = normalize_time_value(block_start)
    slot_end = normalize_time_value(block_end)
    parsed_block_start, parsed_block_end = parse_time_range(block_time)
    normalized_time = normalize_time_range(slot_start, slot_end) if slot_start and slot_end else normalize_time_range(parsed_block_start, parsed_block_end) or block_time
    if not (slot_start and slot_end):
        parsed_start, parsed_end = parse_time_range(normalized_time)
        slot_start = slot_start or parsed_start
        slot_end = slot_end or parsed_end

    for row in rows:
        if row["date"] != target_date:
            continue
        if row["all_day"]:
            return True
        if row["block_time"] and normalized_time and row["block_time"] == normalized_time:
            return True
        if ranges_overlap(slot_start, slot_end, row.get("start_time"), row.get("end_time")):
            return True
    return False


def get_accumulated_workload_breakdown(db: Session) -> dict[int, dict[str, int]]:
    counts: dict[int, dict[str, int]] = defaultdict(
        lambda: {
            "invigilation_count": 0,
            "paper_distribution_count": 0,
            "external_exam_count": 0,
            "total_workload": 0,
        }
    )

    for user_id, duty_count in db.query(
        models.SupervisionBaseline.user_id,
        func.count(models.SupervisionBaseline.id),
    ).group_by(models.SupervisionBaseline.user_id).all():
        counts[user_id]["invigilation_count"] += int(duty_count or 0)

    for user_id, duty_count in db.query(
        models.PaperDistributionAssignment.user_id,
        func.count(models.PaperDistributionAssignment.id),
    ).group_by(models.PaperDistributionAssignment.user_id).all():
        counts[user_id]["paper_distribution_count"] += int(duty_count or 0)

    for user_id, duty_count in db.query(
        models.ExternalSupervision.user_id,
        func.count(models.ExternalSupervision.id),
    ).group_by(models.ExternalSupervision.user_id).all():
        counts[user_id]["external_exam_count"] += int(duty_count or 0)

    for payload in counts.values():
        payload["total_workload"] = (
            payload["invigilation_count"]
            + payload["paper_distribution_count"]
            + payload["external_exam_count"]
        )

    return dict(counts)


def get_period_workload_snapshot(db: Session, period: models.ExamPeriod) -> dict[str, Any]:
    slot_schedules = db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
        joinedload(models.ExamSchedule.room),
        joinedload(models.ExamSchedule.supervisions).joinedload(models.Supervision.user),
    ).join(models.Section).filter(
        models.Section.academic_year == period.academic_year,
        models.Section.semester == period.semester,
        models.ExamSchedule.exam_type == period.exam_type,
    ).all()

    details: list[dict[str, Any]] = []

    for schedule in slot_schedules:
        course = schedule.section.course if schedule.section else None
        for supervision in schedule.supervisions or []:
            if not supervision.user or supervision.role_in_exam == "room_keeper":
                continue
            details.append(
                {
                    "user_id": supervision.user_id,
                    "staff_name": supervision.user.full_name or supervision.user.username,
                    "department": supervision.user.division or supervision.user.unit or "",
                    "duty_type": models.StaffDutyType.invigilation.value,
                    "date": str(schedule.exam_date) if schedule.exam_date else "",
                    "time": schedule.exam_time,
                    "context_label": f"{course.course_id if course else 'Course'} Sec {schedule.section.section_no if schedule.section else '-'}",
                    "room": schedule.room.room_name if schedule.room else None,
                    "workload_count": 1,
                }
            )

    distribution_rows = db.query(models.PaperDistributionAssignment).options(
        joinedload(models.PaperDistributionAssignment.user)
    ).filter(
        models.PaperDistributionAssignment.exam_period_id == period.id
    ).order_by(
        models.PaperDistributionAssignment.exam_date,
        models.PaperDistributionAssignment.exam_time,
        models.PaperDistributionAssignment.slot_order,
    ).all()

    slot_context_map: dict[tuple[str, str], dict[str, Any]] = defaultdict(lambda: {"courses": [], "rooms": []})
    for schedule in slot_schedules:
        key = (str(schedule.exam_date) if schedule.exam_date else "", schedule.exam_time or "")
        course = schedule.section.course if schedule.section else None
        if course and schedule.section:
            slot_context_map[key]["courses"].append(f"{course.course_id} Sec {schedule.section.section_no}")
        if schedule.room and schedule.room.room_name not in slot_context_map[key]["rooms"]:
            slot_context_map[key]["rooms"].append(schedule.room.room_name)

    for assignment in distribution_rows:
        context = slot_context_map[(assignment.exam_date, assignment.exam_time)]
        details.append(
            {
                "user_id": assignment.user_id,
                "staff_name": assignment.user.full_name if assignment.user else f"User #{assignment.user_id}",
                "department": (assignment.user.division or assignment.user.unit) if assignment.user else "",
                "duty_type": models.StaffDutyType.paper_distribution.value,
                "date": assignment.exam_date,
                "time": assignment.exam_time,
                "context_label": ", ".join(context["courses"]) if context["courses"] else "Slot-wide paper distribution",
                "room": ", ".join(context["rooms"]) if context["rooms"] else None,
                "workload_count": assignment.workload_units or 1,
            }
        )

    external_rows = db.query(models.ExternalSupervision).options(
        joinedload(models.ExternalSupervision.user),
        joinedload(models.ExternalSupervision.external_exam),
    ).join(models.ExternalExam).filter(
        models.ExternalExam.exam_period_id == period.id
    ).all()

    for supervision in external_rows:
        exam = supervision.external_exam
        details.append(
            {
                "user_id": supervision.user_id,
                "staff_name": supervision.user.full_name if supervision.user else f"User #{supervision.user_id}",
                "department": (supervision.user.division or supervision.user.unit) if supervision.user else "",
                "duty_type": models.StaffDutyType.external_exam.value,
                "date": exam.exam_date if exam else "",
                "time": exam.exam_time if exam else "",
                "context_label": exam.title if exam else "External exam",
                "room": exam.room_name if exam else None,
                "workload_count": 1,
            }
        )

    details.sort(key=lambda row: (row["date"], row["time"], row["staff_name"], row["duty_type"]))

    historical = get_accumulated_workload_breakdown(db)
    summary: dict[int, dict[str, Any]] = {}
    for row in details:
        staff = summary.setdefault(
            row["user_id"],
            {
                "user_id": row["user_id"],
                "staff_name": row["staff_name"],
                "department": row["department"],
                "invigilation_count": 0,
                "paper_distribution_count": 0,
                "external_exam_count": 0,
                "total_workload": 0,
                "historical_total_workload": historical.get(row["user_id"], {}).get("total_workload", 0),
                "assignments": [],
            },
        )
        if row["duty_type"] == models.StaffDutyType.invigilation.value:
            staff["invigilation_count"] += row["workload_count"]
        elif row["duty_type"] == models.StaffDutyType.paper_distribution.value:
            staff["paper_distribution_count"] += row["workload_count"]
        elif row["duty_type"] == models.StaffDutyType.external_exam.value:
            staff["external_exam_count"] += row["workload_count"]
        staff["total_workload"] += row["workload_count"]
        staff["assignments"].append(row)

    summary_rows = sorted(summary.values(), key=lambda row: (-row["total_workload"], row["staff_name"]))
    fairness_pool = [row["historical_total_workload"] for row in summary_rows]
    fairness_score = 0.0
    if len(fairness_pool) > 1:
        import statistics
        fairness_score = round(statistics.stdev(fairness_pool), 2)

    return {
        "summary": summary_rows,
        "details": details,
        "fairness_score": fairness_score,
        "total_assignments": len(details),
    }


def assign_paper_distribution_for_period(
    db: Session,
    period: models.ExamPeriod,
    actor_id: int | None = None,
) -> dict[str, Any]:
    slot_schedules = db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
        joinedload(models.ExamSchedule.room),
        joinedload(models.ExamSchedule.supervisions),
    ).join(models.Section).filter(
        models.Section.academic_year == period.academic_year,
        models.Section.semester == period.semester,
        models.ExamSchedule.exam_type == period.exam_type,
    ).order_by(
        models.ExamSchedule.exam_date,
        models.ExamSchedule.exam_time,
        models.ExamSchedule.id,
    ).all()

    slot_map: dict[tuple[str, str], list[models.ExamSchedule]] = defaultdict(list)
    for schedule in slot_schedules:
        slot_map[(str(schedule.exam_date) if schedule.exam_date else "", schedule.exam_time or "")].append(schedule)

    db.query(models.PaperDistributionAssignment).filter(
        models.PaperDistributionAssignment.exam_period_id == period.id
    ).delete(synchronize_session=False)
    db.flush()

    candidates = [
        user
        for user in db.query(models.User).filter(
            models.User.role == models.UserRole.staff,
            models.User.is_active == True,
        ).order_by(models.User.full_name).all()
        if is_paper_distribution_candidate(user)
    ]

    workload = get_accumulated_workload_breakdown(db)
    unavailability_map = build_staff_unavailability_map(db, period.id)
    assigned_rows = []
    warnings: list[str] = []

    for (exam_date, exam_time), schedules in sorted(slot_map.items()):
        if not exam_date or not exam_time:
            continue
        block_start, block_end = parse_time_range(exam_time)
        conflict_user_ids = {
            supervision.user_id
            for schedule in schedules
            for supervision in (schedule.supervisions or [])
            if supervision.user_id
        }
        external_conflicts = {
            row[0]
            for row in db.query(models.ExternalSupervision.user_id).join(
                models.ExternalExam,
                models.ExternalSupervision.external_exam_id == models.ExternalExam.id,
            ).filter(
                models.ExternalExam.exam_period_id == period.id,
                models.ExternalExam.exam_date == exam_date,
                models.ExternalExam.exam_time == exam_time,
            ).all()
        }

        available_candidates = [
            user
            for user in candidates
            if user.id not in conflict_user_ids
            and user.id not in external_conflicts
            and not is_staff_unavailable(unavailability_map, user.id, exam_date, exam_time, block_start, block_end)
        ]
        available_candidates.sort(
            key=lambda user: (
                workload.get(user.id, {}).get("total_workload", 0),
                workload.get(user.id, {}).get("paper_distribution_count", 0),
                user.full_name or user.username,
            )
        )

        if not available_candidates:
            warnings.append(f"No eligible paper-distribution staff available for {exam_date} {exam_time}.")
            continue

        selected = available_candidates[0]
        assignment = models.PaperDistributionAssignment(
            exam_period_id=period.id,
            user_id=selected.id,
            exam_date=exam_date,
            exam_time=exam_time,
            start_time=block_start,
            end_time=block_end,
            slot_order=1,
            duty_type=models.StaffDutyType.paper_distribution,
            workload_units=1,
            assignment_mode="auto",
            covered_schedule_count=len(schedules),
            created_by=actor_id,
        )
        db.add(assignment)
        db.flush()
        assigned_rows.append(assignment)
        workload.setdefault(
            selected.id,
            {
                "invigilation_count": 0,
                "paper_distribution_count": 0,
                "external_exam_count": 0,
                "total_workload": 0,
            },
        )
        workload[selected.id]["paper_distribution_count"] += 1
        workload[selected.id]["total_workload"] += 1

    return {
        "assigned_count": len(assigned_rows),
        "slot_count": len(slot_map),
        "unfilled_count": max(len(slot_map) - len(assigned_rows), 0),
        "warnings": warnings,
    }
