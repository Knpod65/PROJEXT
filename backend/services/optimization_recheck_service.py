"""
services/optimization_recheck_service.py

Post-generation validation for optimized schedules.
The service is read-only and returns structured issues for review.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Iterable, Optional

from sqlalchemy.orm import joinedload

import models


@dataclass(frozen=True)
class RecheckIssue:
    severity: str
    code: str
    message: str
    course_id: str | None = None
    section: str | None = None
    exam_date: str | None = None
    exam_time: str | None = None
    room_id: int | None = None
    actor_id: int | None = None
    suggested_fix: str | None = None
    can_override: bool = False


def _issue(
    severity: str,
    code: str,
    message: str,
    *,
    course_id: str | None = None,
    section: str | None = None,
    exam_date: str | None = None,
    exam_time: str | None = None,
    room_id: int | None = None,
    actor_id: int | None = None,
    suggested_fix: str | None = None,
    can_override: bool = False,
) -> RecheckIssue:
    return RecheckIssue(
        severity=severity,
        code=code,
        message=message,
        course_id=course_id,
        section=section,
        exam_date=exam_date,
        exam_time=exam_time,
        room_id=room_id,
        actor_id=actor_id,
        suggested_fix=suggested_fix,
        can_override=can_override,
    )


def _suggested_fix_for(code: str) -> str:
    mapping = {
        "ROOM_CAPACITY_EXCEEDED": "Move the section to a larger room or split the exam into multiple rooms.",
        "STUDENT_CONFLICT": "Move one of the conflicting exams to a different slot.",
        "INSTRUCTOR_CONFLICT": "Reassign invigilation or move one overlapping exam.",
        "ROOM_CONFLICT": "Assign a different room for one of the overlapping exams.",
        "MISSING_ROOM": "Assign a valid exam room before confirming.",
        "MISSING_INVIGILATOR": "Assign at least one invigilator or supervisor for the slot.",
        "MISSING_DISTRIBUTION_STAFF": "Assign a paper distributor before confirmation.",
        "EXAM_OUTSIDE_PERIOD": "Regenerate the schedule within the active exam period.",
        "INVALID_SECTION_COURSE_LINKAGE": "Repair the schedule row so it points to a valid section and course.",
        "INVALID_ROOM_SEMANTICS": "Move the exam to an approved exam room if teaching-room reuse is not allowed.",
        "LOW_ROOM_UTILIZATION": "Consider grouping compatible sections or moving to a smaller room.",
        "SPLIT_EXAM_TOO_MANY_ROOMS": "Reduce the number of rooms used for the same course or section.",
        "WORKLOAD_IMBALANCE": "Rebalance invigilation assignments across staff.",
        "CONSECUTIVE_INVIGILATION_OVERLOAD": "Avoid stacking the same person across consecutive slots.",
        "SAME_DAY_OVERLOAD": "Reduce the number of sessions assigned to the same person on the same day.",
        "MISSING_QR_READINESS": "Generate pickup QR and readiness artifacts for the schedule.",
        "MISSING_DOCUMENT_READINESS": "Generate cover sheet and attendance/export readiness artifacts.",
        "COPY_COUNT_MISMATCH": "Align the generated copy count with the teacher submission or adjust the schedule artifacts.",
    }
    return mapping.get(code, "Review the generated schedule and correct the affected record.")


def _slot_key(schedule) -> tuple[str | None, str | None]:
    return str(getattr(schedule, "exam_date", None)), getattr(schedule, "exam_time", None)


def _slot_label(schedule) -> tuple[str | None, str | None]:
    return str(getattr(schedule, "exam_date", None)), getattr(schedule, "exam_time", None)


def _submission_exam_type(submission) -> str | None:
    if not submission or not getattr(submission, "exam_type_choice", None):
        return None
    return submission.exam_type_choice.value if hasattr(submission.exam_type_choice, "value") else str(submission.exam_type_choice)


def _is_info_excluded(submission) -> bool:
    return _submission_exam_type(submission) in {"no_exam", "online", "outside_sched"}


def build_recheck_report(
    *,
    period,
    schedules: Iterable,
    submissions_by_section: dict[int, object] | None = None,
    enrollments_by_section: dict[int, set[str]] | None = None,
) -> dict:
    submissions_by_section = submissions_by_section or {}
    enrollments_by_section = enrollments_by_section or {}

    issues: list[RecheckIssue] = []
    schedule_list = list(schedules)
    slots: dict[tuple[str | None, str | None], list] = defaultdict(list)
    room_ids: set[int] = set()

    for schedule in schedule_list:
        slots[_slot_key(schedule)].append(schedule)
        if getattr(schedule, "room_id", None) is not None:
            room_ids.add(schedule.room_id)

    def add(issue: RecheckIssue):
        issues.append(issue)

    for schedule in schedule_list:
        section = getattr(schedule, "section", None)
        room = getattr(schedule, "room", None)
        section_id = getattr(section, "id", None)
        submission = submissions_by_section.get(section_id)
        course = getattr(section, "course", None) if section else None
        teacher = getattr(section, "teacher", None) if section else None
        exam_type = getattr(schedule, "exam_type", None)
        exam_type_value = exam_type.value if hasattr(exam_type, "value") else str(exam_type) if exam_type else None

        if not section or not course:
            add(_issue(
                "ERROR",
                "INVALID_SECTION_COURSE_LINKAGE",
                "Generated schedule references an unknown section or course.",
                exam_date=str(getattr(schedule, "exam_date", None)),
                exam_time=getattr(schedule, "exam_time", None),
                room_id=getattr(schedule, "room_id", None),
                suggested_fix=_suggested_fix_for("INVALID_SECTION_COURSE_LINKAGE"),
                can_override=True,
            ))
            continue

        if exam_type_value and period and exam_type_value != getattr(period, "exam_type", exam_type_value):
            add(_issue(
                "ERROR",
                "EXAM_OUTSIDE_PERIOD",
                f"Schedule exam type '{exam_type_value}' does not match active period '{getattr(period, 'exam_type', None)}'.",
                course_id=getattr(course, "course_id", None),
                section=getattr(section, "section_no", None),
                exam_date=str(getattr(schedule, "exam_date", None)),
                exam_time=getattr(schedule, "exam_time", None),
                room_id=getattr(schedule, "room_id", None),
                actor_id=getattr(teacher, "id", None),
                suggested_fix=_suggested_fix_for("EXAM_OUTSIDE_PERIOD"),
                can_override=True,
            ))

        if _is_info_excluded(submission):
            add(_issue(
                "INFO",
                "EXCLUDED_NON_ONSITE_EXAM",
                "No-exam or online-style submission is excluded from room optimization.",
                course_id=getattr(course, "course_id", None),
                section=getattr(section, "section_no", None),
                exam_date=str(getattr(schedule, "exam_date", None)),
                exam_time=getattr(schedule, "exam_time", None),
                room_id=getattr(schedule, "room_id", None),
                actor_id=getattr(teacher, "id", None),
                suggested_fix="No room action is required for this schedule.",
                can_override=False,
            ))
            continue

        if room is None and getattr(schedule, "room_id", None) is None:
            add(_issue(
                "ERROR",
                "MISSING_ROOM",
                "Onsite exam schedule is missing a room assignment.",
                course_id=getattr(course, "course_id", None),
                section=getattr(section, "section_no", None),
                exam_date=str(getattr(schedule, "exam_date", None)),
                exam_time=getattr(schedule, "exam_time", None),
                suggested_fix=_suggested_fix_for("MISSING_ROOM"),
                can_override=True,
            ))
            continue

        students = enrollments_by_section.get(section_id, set())
        student_count = len(students) or getattr(section, "num_students", 0) or 0

        if room and getattr(room, "capacity", None) is not None and student_count > room.capacity:
            add(_issue(
                "ERROR",
                "ROOM_CAPACITY_EXCEEDED",
                f"{student_count} students exceed room capacity {room.capacity}.",
                course_id=getattr(course, "course_id", None),
                section=getattr(section, "section_no", None),
                exam_date=str(getattr(schedule, "exam_date", None)),
                exam_time=getattr(schedule, "exam_time", None),
                room_id=getattr(room, "id", getattr(schedule, "room_id", None)),
                actor_id=getattr(teacher, "id", None),
                suggested_fix=_suggested_fix_for("ROOM_CAPACITY_EXCEEDED"),
                can_override=True,
            ))

        if room and getattr(section, "teaching_room", None) and room.id == section.teaching_room.id:
            add(_issue(
                "INFO",
                "INVALID_ROOM_SEMANTICS",
                "Teaching room was reused as the exam room; review whether this is allowed.",
                course_id=getattr(course, "course_id", None),
                section=getattr(section, "section_no", None),
                exam_date=str(getattr(schedule, "exam_date", None)),
                exam_time=getattr(schedule, "exam_time", None),
                room_id=room.id,
                actor_id=getattr(teacher, "id", None),
                suggested_fix=_suggested_fix_for("INVALID_ROOM_SEMANTICS"),
                can_override=False,
            ))

        if room and getattr(room, "capacity", None):
            utilization = (student_count / room.capacity) if room.capacity else 0
            if utilization < 0.4:
                add(_issue(
                    "WARNING",
                    "LOW_ROOM_UTILIZATION",
                    f"Room utilization is low at {utilization:.0%}.",
                    course_id=getattr(course, "course_id", None),
                    section=getattr(section, "section_no", None),
                    exam_date=str(getattr(schedule, "exam_date", None)),
                    exam_time=getattr(schedule, "exam_time", None),
                    room_id=room.id,
                    actor_id=getattr(teacher, "id", None),
                    suggested_fix=_suggested_fix_for("LOW_ROOM_UTILIZATION"),
                    can_override=False,
                ))

        supervisions = list(getattr(schedule, "supervisions", []) or [])
        if not supervisions:
            add(_issue(
                "ERROR",
                "MISSING_INVIGILATOR",
                "Onsite exam schedule has no invigilator or supervision assignment.",
                course_id=getattr(course, "course_id", None),
                section=getattr(section, "section_no", None),
                exam_date=str(getattr(schedule, "exam_date", None)),
                exam_time=getattr(schedule, "exam_time", None),
                room_id=getattr(room, "id", getattr(schedule, "room_id", None)),
                suggested_fix=_suggested_fix_for("MISSING_INVIGILATOR"),
                can_override=True,
            ))
        else:
            if room and not getattr(schedule, "paper_distributor", None):
                add(_issue(
                    "ERROR",
                    "MISSING_DISTRIBUTION_STAFF",
                    "Paper distribution is required but no distributor was assigned.",
                    course_id=getattr(course, "course_id", None),
                    section=getattr(section, "section_no", None),
                    exam_date=str(getattr(schedule, "exam_date", None)),
                    exam_time=getattr(schedule, "exam_time", None),
                    room_id=room.id,
                    suggested_fix=_suggested_fix_for("MISSING_DISTRIBUTION_STAFF"),
                    can_override=True,
                ))

        if not getattr(schedule, "pickup_qr_tokens", None):
            add(_issue(
                "INFO",
                "MISSING_QR_READINESS",
                "No pickup QR artifacts are attached to this generated schedule.",
                course_id=getattr(course, "course_id", None),
                section=getattr(section, "section_no", None),
                exam_date=str(getattr(schedule, "exam_date", None)),
                exam_time=getattr(schedule, "exam_time", None),
                room_id=getattr(room, "id", getattr(schedule, "room_id", None)),
                suggested_fix=_suggested_fix_for("MISSING_QR_READINESS"),
                can_override=False,
            ))

        if submission and getattr(submission, "a4_pages_count", None) and getattr(schedule, "num_pages", None):
            if submission.a4_pages_count != schedule.num_pages:
                add(_issue(
                    "WARNING",
                    "COPY_COUNT_MISMATCH",
                    "Teacher submission copy count differs from the generated schedule page count.",
                    course_id=getattr(course, "course_id", None),
                    section=getattr(section, "section_no", None),
                    exam_date=str(getattr(schedule, "exam_date", None)),
                    exam_time=getattr(schedule, "exam_time", None),
                    room_id=getattr(room, "id", getattr(schedule, "room_id", None)),
                    suggested_fix=_suggested_fix_for("COPY_COUNT_MISMATCH"),
                    can_override=False,
                ))

    # Slot-level checks
    for (exam_date, exam_time), items in slots.items():
        if len(items) < 2:
            continue

        room_bucket: dict[int, list] = defaultdict(list)
        teacher_bucket: dict[int, list] = defaultdict(list)
        user_bucket: dict[int, list] = defaultdict(list)
        student_bucket: dict[str, list] = defaultdict(list)

        for schedule in items:
            room_id = getattr(schedule, "room_id", None)
            if room_id is not None:
                room_bucket[room_id].append(schedule)
            section = getattr(schedule, "section", None)
            teacher = getattr(section, "teacher", None) if section else None
            if teacher and getattr(teacher, "id", None) is not None:
                teacher_bucket[teacher.id].append(schedule)
            for supervision in getattr(schedule, "supervisions", []) or []:
                user = getattr(supervision, "user", None)
                if user and getattr(user, "id", None) is not None:
                    user_bucket[user.id].append(schedule)
            for student_id in enrollments_by_section.get(getattr(section, "id", None), set()):
                student_bucket[student_id].append(schedule)

        for room_id, room_items in room_bucket.items():
            if len(room_items) > 1:
                first = room_items[0]
                section = getattr(first, "section", None)
                course = getattr(section, "course", None) if section else None
                teacher = getattr(section, "teacher", None) if section else None
                add(_issue(
                    "ERROR",
                    "ROOM_CONFLICT",
                    "The same room is assigned to more than one exam in the same slot.",
                    course_id=getattr(course, "course_id", None),
                    section=getattr(section, "section_no", None),
                    exam_date=exam_date,
                    exam_time=exam_time,
                    room_id=room_id,
                    actor_id=getattr(teacher, "id", None),
                    suggested_fix=_suggested_fix_for("ROOM_CONFLICT"),
                    can_override=True,
                ))

        for teacher_id, teacher_items in teacher_bucket.items():
            if len(teacher_items) > 1:
                first = teacher_items[0]
                section = getattr(first, "section", None)
                course = getattr(section, "course", None) if section else None
                add(_issue(
                    "ERROR",
                    "INSTRUCTOR_CONFLICT",
                    "The same instructor is scheduled for overlapping exams.",
                    course_id=getattr(course, "course_id", None),
                    section=getattr(section, "section_no", None),
                    exam_date=exam_date,
                    exam_time=exam_time,
                    actor_id=teacher_id,
                    suggested_fix=_suggested_fix_for("INSTRUCTOR_CONFLICT"),
                    can_override=True,
                ))

        for user_id, user_items in user_bucket.items():
            if len(user_items) > 1:
                first = user_items[0]
                section = getattr(first, "section", None)
                course = getattr(section, "course", None) if section else None
                add(_issue(
                    "ERROR",
                    "INSTRUCTOR_CONFLICT",
                    "The same invigilator is assigned to overlapping exams.",
                    course_id=getattr(course, "course_id", None),
                    section=getattr(section, "section_no", None),
                    exam_date=exam_date,
                    exam_time=exam_time,
                    actor_id=user_id,
                    suggested_fix=_suggested_fix_for("INSTRUCTOR_CONFLICT"),
                    can_override=True,
                ))

        for student_id, student_items in student_bucket.items():
            if len(student_items) > 1:
                first = student_items[0]
                section = getattr(first, "section", None)
                course = getattr(section, "course", None) if section else None
                add(_issue(
                    "ERROR",
                    "STUDENT_CONFLICT",
                    f"A student appears in multiple exams in the same slot ({len(student_items)} overlaps detected).",
                    course_id=getattr(course, "course_id", None),
                    section=getattr(section, "section_no", None),
                    exam_date=exam_date,
                    exam_time=exam_time,
                    suggested_fix=_suggested_fix_for("STUDENT_CONFLICT"),
                    can_override=True,
                ))
                break

    # Workload warnings across all schedules
    workload_by_actor: dict[int, list[tuple[str, str | None]]] = defaultdict(list)
    for schedule in schedule_list:
        slot = (str(getattr(schedule, "exam_date", None)), getattr(schedule, "exam_time", None))
        section = getattr(schedule, "section", None)
        teacher = getattr(section, "teacher", None) if section else None
        if teacher and getattr(teacher, "id", None) is not None:
            workload_by_actor[teacher.id].append(slot)
        for supervision in getattr(schedule, "supervisions", []) or []:
            user = getattr(supervision, "user", None)
            if user and getattr(user, "id", None) is not None:
                workload_by_actor[user.id].append(slot)

    for actor_id, slots_for_actor in workload_by_actor.items():
        total = len(slots_for_actor)
        day_counts: dict[str, int] = defaultdict(int)
        ordered = sorted(slots_for_actor)
        longest_streak = 1
        streak = 1
        for index, slot in enumerate(ordered):
            day_counts[slot[0]] += 1
            if index > 0 and ordered[index - 1][0] == slot[0] and ordered[index - 1][1] != slot[1]:
                streak += 1
                longest_streak = max(longest_streak, streak)
            elif index > 0 and ordered[index - 1] == slot:
                continue
            else:
                streak = 1

        if total > 4:
            sample = schedule_list[0]
            section = getattr(sample, "section", None)
            course = getattr(section, "course", None) if section else None
            add(_issue(
                "WARNING",
                "WORKLOAD_IMBALANCE",
                f"Actor {actor_id} has {total} assigned duties in the generated schedule.",
                course_id=getattr(course, "course_id", None),
                section=getattr(section, "section_no", None),
                actor_id=actor_id,
                suggested_fix=_suggested_fix_for("WORKLOAD_IMBALANCE"),
                can_override=False,
            ))
        if longest_streak >= 3:
            sample = schedule_list[0]
            section = getattr(sample, "section", None)
            course = getattr(section, "course", None) if section else None
            add(_issue(
                "WARNING",
                "CONSECUTIVE_INVIGILATION_OVERLOAD",
                f"Actor {actor_id} is scheduled in {longest_streak} consecutive slots.",
                course_id=getattr(course, "course_id", None),
                section=getattr(section, "section_no", None),
                actor_id=actor_id,
                suggested_fix=_suggested_fix_for("CONSECUTIVE_INVIGILATION_OVERLOAD"),
                can_override=False,
            ))
        if any(count > 2 for count in day_counts.values()):
            sample = schedule_list[0]
            section = getattr(sample, "section", None)
            course = getattr(section, "course", None) if section else None
            add(_issue(
                "WARNING",
                "SAME_DAY_OVERLOAD",
                f"Actor {actor_id} has more than two assignments on the same day.",
                course_id=getattr(course, "course_id", None),
                section=getattr(section, "section_no", None),
                actor_id=actor_id,
                suggested_fix=_suggested_fix_for("SAME_DAY_OVERLOAD"),
                can_override=False,
            ))

    hard_error_count = sum(1 for issue in issues if issue.severity == "ERROR")
    warning_count = sum(1 for issue in issues if issue.severity == "WARNING")
    info_count = sum(1 for issue in issues if issue.severity == "INFO")
    status = "PASS"
    if hard_error_count > 0:
        status = "FAIL"
    elif warning_count > 0:
        status = "PASS_WITH_WARNINGS"

    return {
        "status": status,
        "summary": {
            "hard_error_count": hard_error_count,
            "warning_count": warning_count,
            "info_count": info_count,
            "checked_schedule_count": len(schedule_list),
            "checked_slot_count": len(slots),
            "checked_room_count": len(room_ids),
        },
        "issues": [asdict(issue) for issue in issues],
    }


def run_optimization_recheck(db, session_id: int) -> dict:
    session = db.query(models.OptimizeSession).filter(models.OptimizeSession.id == session_id).first()
    if not session:
        raise ValueError(f"Unknown optimize session id={session_id}")

    period = db.query(models.ExamPeriod).filter(models.ExamPeriod.id == session.exam_period_id).first()
    if not period:
        raise ValueError(f"Unknown exam period id={session.exam_period_id}")

    sections = db.query(models.Section).filter(
        models.Section.semester == period.semester,
        models.Section.academic_year == period.academic_year,
    ).all()
    section_ids = [section.id for section in sections]

    schedules = db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
        joinedload(models.ExamSchedule.section).joinedload(models.Section.teacher),
        joinedload(models.ExamSchedule.section).joinedload(models.Section.teaching_room),
        joinedload(models.ExamSchedule.room),
        joinedload(models.ExamSchedule.supervisions).joinedload(models.Supervision.user),
    ).filter(models.ExamSchedule.section_id.in_(section_ids)).all() if section_ids else []

    submissions = db.query(models.ExamSubmission).filter(models.ExamSubmission.section_id.in_(section_ids)).all() if section_ids else []
    enrollments = db.query(models.EnrollmentRecord).filter(models.EnrollmentRecord.section_id.in_(section_ids)).all() if section_ids else []

    submission_map = {submission.section_id: submission for submission in submissions}
    enrollment_map: dict[int, set[str]] = defaultdict(set)
    for enrollment in enrollments:
        enrollment_map[enrollment.section_id].add(str(enrollment.student_id))

    return build_recheck_report(
        period=period,
        schedules=schedules,
        submissions_by_section=submission_map,
        enrollments_by_section=enrollment_map,
    )
