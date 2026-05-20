"""workload_duty_analytics_repository.py — raw duty normalization for workload analytics."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy.orm import Session, joinedload

import models
from staff_workloads import get_period_workload_snapshot
from time_ranges import normalize_time_range, parse_time_range


def _role_group_from_user(user: models.User | None) -> str:
    role = getattr(user, "role", None)
    if hasattr(role, "value"):
        role = role.value
    role = str(role or "staff").lower()
    if role in {"dept_supervisor", "esq_head", "secretary"}:
        return "supervisor"
    if role in {"admin", "staff", "supervisor", "teacher", "dpo"}:
        return role
    return "staff"


def _normalize_time_slot(start: str | None, end: str | None, fallback: str | None = None) -> str:
    normalized = normalize_time_range(start, end)
    if normalized:
        return normalized
    if fallback:
        parsed_start, parsed_end = parse_time_range(fallback)
        normalized = normalize_time_range(parsed_start, parsed_end)
        if normalized:
            return normalized
    return "unscheduled"


def _display_name(user: models.User | None, fallback: str = "") -> str:
    if user is None:
        return fallback
    return (user.full_name or user.username or fallback or "").strip() or fallback


def _person_identity(user: models.User | None, fallback: str = "") -> str:
    if user is None:
        return fallback
    if user.id is not None:
        return str(user.id)
    return fallback or (user.username or "")


def _name_key(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


class WorkloadDutyAnalyticsRepository:
    """Database queries that normalize workload duty sources into a common shape."""

    @staticmethod
    def _load_period_lookup(db: Session) -> dict[tuple[str, str, str], int]:
        lookup: dict[tuple[str, str, str], int] = {}
        for period in db.query(models.ExamPeriod).all():
            lookup[(str(period.academic_year), str(period.semester), str(period.exam_type).lower())] = period.id
        return lookup

    @staticmethod
    def _load_user_lookup(db: Session) -> dict[str, models.User]:
        lookup: dict[str, models.User] = {}
        for user in db.query(models.User).all():
            lookup[str(user.id)] = user
            username_key = _name_key(user.username)
            if username_key:
                lookup[username_key] = user
            full_name_key = _name_key(user.full_name)
            if full_name_key:
                lookup[full_name_key] = user
        return lookup

    @staticmethod
    def _period_id_for_schedule(schedule: models.ExamSchedule, period_lookup: dict[tuple[str, str, str], int]) -> int | None:
        section = schedule.section
        if section is None or schedule.exam_type is None:
            return None
        semester = str(getattr(section, "semester", "") or "")
        academic_year = str(getattr(section, "academic_year", "") or "")
        exam_type = str(getattr(schedule.exam_type, "value", schedule.exam_type)).lower()
        return period_lookup.get((academic_year, semester, exam_type))

    @staticmethod
    def fetch_normalized_duty_records(db: Session, period_id: int | None = None) -> list[dict[str, Any]]:
        period_lookup = WorkloadDutyAnalyticsRepository._load_period_lookup(db)
        user_lookup = WorkloadDutyAnalyticsRepository._load_user_lookup(db)
        records: list[dict[str, Any]] = []

        schedules = db.query(models.ExamSchedule).options(
            joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
            joinedload(models.ExamSchedule.supervisions).joinedload(models.Supervision.user),
            joinedload(models.ExamSchedule.room),
        ).all()

        for schedule in schedules:
            section = schedule.section
            course = section.course if section else None
            period_for_schedule = WorkloadDutyAnalyticsRepository._period_id_for_schedule(schedule, period_lookup)
            exam_date = str(schedule.exam_date) if schedule.exam_date else ""
            time_slot = _normalize_time_slot(schedule.exam_time_start, schedule.exam_time_end, schedule.exam_time)
            semester = str(getattr(section, "semester", "") or "")
            academic_year = str(getattr(section, "academic_year", "") or "")
            exam_type = str(getattr(schedule.exam_type, "value", schedule.exam_type) or "").lower()
            course_id = str(getattr(course, "course_id", "") or "")
            section_no = str(getattr(section, "section_no", "") or "")

            for supervision in schedule.supervisions or []:
                if supervision.user is None:
                    continue
                if str(getattr(supervision, "role_in_exam", "")).lower() == "room_keeper":
                    continue
                user = supervision.user
                records.append(
                    {
                        "person_id": _person_identity(user),
                        "display_name": _display_name(user),
                        "role_group": _role_group_from_user(user),
                        "duty_type": "invigilation",
                        "exam_date": exam_date,
                        "time_slot": time_slot,
                        "course_id": course_id,
                        "section_no": section_no,
                        "source": "supervision",
                        "semester": semester,
                        "academic_year": academic_year,
                        "exam_type": exam_type,
                        "period_id": period_for_schedule,
                        "workload_units": 1,
                    }
                )

            if schedule.paper_distributor:
                distributor_key = _name_key(schedule.paper_distributor)
                user = user_lookup.get(distributor_key)
                person_id = _person_identity(user, f"paper_distributor:{schedule.id}")
                display_name = _display_name(user, schedule.paper_distributor)
                records.append(
                    {
                        "person_id": person_id,
                        "display_name": display_name,
                        "role_group": _role_group_from_user(user),
                        "duty_type": "paper_distribution",
                        "exam_date": exam_date,
                        "time_slot": time_slot,
                        "course_id": course_id,
                        "section_no": section_no,
                        "source": "paper_distributor",
                        "semester": semester,
                        "academic_year": academic_year,
                        "exam_type": exam_type,
                        "period_id": period_for_schedule,
                        "workload_units": 1,
                    }
                )

        assignments = db.query(models.PaperDistributionAssignment).options(
            joinedload(models.PaperDistributionAssignment.user),
            joinedload(models.PaperDistributionAssignment.period),
        ).all()

        for assignment in assignments:
            user = assignment.user
            period = assignment.period
            records.append(
                {
                    "person_id": _person_identity(user, str(assignment.user_id)),
                    "display_name": _display_name(user, f"User #{assignment.user_id}"),
                    "role_group": _role_group_from_user(user),
                    "duty_type": "paper_distribution",
                    "exam_date": str(assignment.exam_date or ""),
                    "time_slot": _normalize_time_slot(assignment.start_time, assignment.end_time, assignment.exam_time),
                    "course_id": "",
                    "section_no": "",
                    "source": "workload_record",
                    "semester": str(getattr(period, "semester", "") or ""),
                    "academic_year": str(getattr(period, "academic_year", "") or ""),
                    "exam_type": str(getattr(period, "exam_type", "") or "").lower(),
                    "period_id": getattr(period, "id", assignment.exam_period_id),
                    "workload_units": int(getattr(assignment, "workload_units", 1) or 1),
                }
            )

        checkins = db.query(models.ExamPickupCheckin).options(
            joinedload(models.ExamPickupCheckin.user),
            joinedload(models.ExamPickupCheckin.qr_token).joinedload(models.ExamPickupQrToken.schedule).joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
        ).all()

        for checkin in checkins:
            if str(getattr(checkin.status, "value", checkin.status)).lower() != "success":
                continue
            qr_token = checkin.qr_token
            schedule = qr_token.schedule if qr_token else checkin.schedule
            if schedule is None or schedule.section is None:
                continue
            section = schedule.section
            course = section.course if section else None
            user = checkin.user
            exam_date = str(getattr(schedule, "exam_date", "") or getattr(qr_token, "exam_date", "") or "")
            time_slot = _normalize_time_slot(
                getattr(schedule, "exam_time_start", None) or getattr(qr_token, "start_time", None),
                getattr(schedule, "exam_time_end", None) or getattr(qr_token, "end_time", None),
                getattr(schedule, "exam_time", None),
            )
            semester = str(getattr(section, "semester", "") or "")
            academic_year = str(getattr(section, "academic_year", "") or "")
            exam_type = str(getattr(schedule.exam_type, "value", schedule.exam_type) or "").lower()
            period_id_for_checkin = period_lookup.get((academic_year, semester, exam_type))
            records.append(
                {
                    "person_id": _person_identity(user, str(checkin.user_id or "")),
                    "display_name": _display_name(user, f"User #{checkin.user_id or ''}"),
                    "role_group": _role_group_from_user(user),
                    "duty_type": "paper_distribution",
                    "exam_date": exam_date,
                    "time_slot": time_slot,
                    "course_id": str(getattr(course, "course_id", "") or ""),
                    "section_no": str(getattr(section, "section_no", "") or ""),
                    "source": "pickup_qr",
                    "semester": semester,
                    "academic_year": academic_year,
                    "exam_type": exam_type,
                    "period_id": period_id_for_checkin,
                    "workload_units": 1,
                }
            )

        if not records and period_id is not None:
            period_snapshot = db.query(models.ExamPeriod).filter(models.ExamPeriod.id == period_id).first()
            if period_snapshot is not None:
                snapshot = get_period_workload_snapshot(db, period_snapshot)
                for row in snapshot.get("details", []):
                    duty_type = str(row.get("duty_type", "")).lower()
                    if duty_type not in {"invigilation", "paper_distribution"}:
                        continue
                    records.append(
                        {
                            "person_id": str(row.get("user_id", "")),
                            "display_name": str(row.get("staff_name", "")),
                            "role_group": "staff",
                            "duty_type": duty_type,
                            "exam_date": str(row.get("date", "")),
                            "time_slot": _normalize_time_slot(None, None, str(row.get("time", ""))),
                            "course_id": "",
                            "section_no": "",
                            "source": "workload_record",
                            "semester": str(period_snapshot.semester),
                            "academic_year": str(period_snapshot.academic_year),
                            "exam_type": str(period_snapshot.exam_type).lower(),
                            "period_id": period_snapshot.id,
                            "workload_units": int(row.get("workload_count", 1) or 1),
                        }
                    )

        return records
