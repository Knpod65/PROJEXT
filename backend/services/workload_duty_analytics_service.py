"""workload_duty_analytics_service.py — workload duty analytics aggregation.

This module normalizes invigilation and paper-distribution duties into a
single analytics payload with fairness scoring and chart-ready series.
"""
from __future__ import annotations

from collections import defaultdict
from types import SimpleNamespace
from typing import Any

from fastapi import HTTPException

from policies.workload_duty_analytics_policy import (
    allowed_role_groups,
    can_view_person_workload,
    can_view_teacher_workload,
    can_view_workload_dashboard,
    normalize_role_group,
)
from repositories.workload_duty_analytics_repository import WorkloadDutyAnalyticsRepository
from serializers.workload_duty_analytics_serializer import WorkloadDutyAnalyticsSerializer
from services.workload_analytics_service import compute_workload_analytics


_ROLE_RISK_BAND = {
    "green": "good",
    "amber": "warning",
    "red": "critical",
}


def _user_role(user: Any | None) -> str:
    if user is None:
        return "admin"
    role = getattr(user, "view_as_role", None) or getattr(user, "role", None)
    if hasattr(role, "value"):
        role = role.value
    return str(role or "").lower()


def _user_identity(user: Any | None) -> str:
    if user is None:
        return ""
    user_id = getattr(user, "id", None)
    if user_id is not None:
        return str(user_id)
    return str(getattr(user, "username", "") or "")


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _risk_band(imbalance_score: float) -> str:
    if imbalance_score < 0.15:
        return "good"
    if imbalance_score < 0.25:
        return "info"
    if imbalance_score < 0.4:
        return "warning"
    return "critical"


def _record_key(record: dict[str, Any]) -> tuple[str, str, str, str, str, str]:
    return (
        str(record.get("person_id", "")),
        str(record.get("role_group", "")),
        str(record.get("duty_type", "")),
        str(record.get("exam_date", "")),
        str(record.get("time_slot", "")),
        f"{record.get('course_id', '')}:{record.get('section_no', '')}",
    )


def _source_priority(source: str) -> int:
    order = {
        "supervision": 0,
        "paper_distributor": 1,
        "pickup_qr": 2,
        "workload_record": 3,
    }
    return order.get(str(source), 99)


def _is_visible_record(record: dict[str, Any], current_role: str, filters: dict[str, Any], current_user: Any | None) -> bool:
    role_group = normalize_role_group(record.get("role_group"))
    if role_group == "teacher" and not filters.get("include_teachers", True):
        return False
    if role_group in {"admin", "staff", "supervisor"} and not filters.get("include_staff", True):
        return False

    requested_role_group = normalize_role_group(filters.get("role_group"))
    if requested_role_group != "all" and role_group != requested_role_group:
        return False

    if filters.get("semester") and str(record.get("semester", "")) != str(filters["semester"]):
        return False
    if filters.get("academic_year") and str(record.get("academic_year", "")) != str(filters["academic_year"]):
        return False
    if filters.get("exam_type") and str(record.get("exam_type", "")).lower() != str(filters["exam_type"]).lower():
        return False
    if filters.get("period_id") is not None and _safe_int(record.get("period_id")) != _safe_int(filters.get("period_id")):
        return False

    duty_type = str(record.get("duty_type", "")).lower()
    requested_duty_type = str(filters.get("duty_type", "all")).lower()
    if requested_duty_type == "invigilation" and duty_type != "invigilation":
        return False
    if requested_duty_type == "paper_distribution" and duty_type != "paper_distribution":
        return False
    if requested_duty_type == "combined" and duty_type not in {"invigilation", "paper_distribution"}:
        return False

    person_id = filters.get("person_id")
    if person_id is not None and str(record.get("person_id", "")) != str(person_id):
        return False

    if current_role == "teacher":
        current_identity = _user_identity(current_user)
        return str(record.get("person_id", "")) == current_identity and role_group == "teacher"

    if current_role == "dpo":
        return True

    if current_role in {"staff", "supervisor", "dept_supervisor", "esq_head", "secretary", "admin"}:
        return role_group in allowed_role_groups(current_user)

    return False


def _dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[tuple[str, str, str, str, str, str], dict[str, Any]] = {}
    for record in records:
        key = _record_key(record)
        current = deduped.get(key)
        if current is None or _source_priority(record.get("source", "")) < _source_priority(current.get("source", "")):
            deduped[key] = record
    return list(deduped.values())


def _aggregate_by_person(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "person_id": "",
            "display_name": "",
            "role_group": "staff",
            "invigilation_count": 0,
            "distribution_count": 0,
            "combined_count": 0,
        }
    )
    for record in records:
        person_id = str(record.get("person_id", ""))
        row = grouped[person_id]
        row["person_id"] = person_id
        row["display_name"] = str(record.get("display_name", ""))
        row["role_group"] = normalize_role_group(record.get("role_group"))
        units = _safe_int(record.get("workload_units", 1), 1)
        if str(record.get("duty_type", "")).lower() == "invigilation":
            row["invigilation_count"] += units
        else:
            row["distribution_count"] += units
        row["combined_count"] += units
    return sorted(grouped.values(), key=lambda row: (-row["combined_count"], row["display_name"], row["person_id"]))


def _aggregate_daily(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "date": "",
            "invigilation_count": 0,
            "distribution_count": 0,
            "combined_count": 0,
        }
    )
    for record in records:
        date = str(record.get("exam_date", ""))
        row = buckets[date]
        row["date"] = date
        units = _safe_int(record.get("workload_units", 1), 1)
        if str(record.get("duty_type", "")).lower() == "invigilation":
            row["invigilation_count"] += units
        else:
            row["distribution_count"] += units
        row["combined_count"] += units

    ordered_dates = sorted(buckets.keys())
    cumulative_inv = 0
    cumulative_dist = 0
    cumulative_combined = 0
    series: list[dict[str, Any]] = []
    for date in ordered_dates:
        row = buckets[date]
        cumulative_inv += row["invigilation_count"]
        cumulative_dist += row["distribution_count"]
        cumulative_combined += row["combined_count"]
        series.append(
            {
                "date": date,
                "invigilation_count": row["invigilation_count"],
                "distribution_count": row["distribution_count"],
                "combined_count": row["combined_count"],
                "cumulative_invigilation": cumulative_inv,
                "cumulative_distribution": cumulative_dist,
                "cumulative_combined": cumulative_combined,
            }
        )
    return series


def _aggregate_time_slots(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "time_slot": "",
            "invigilation_count": 0,
            "distribution_count": 0,
            "combined_count": 0,
        }
    )
    for record in records:
        time_slot = str(record.get("time_slot", "unscheduled") or "unscheduled")
        row = buckets[time_slot]
        row["time_slot"] = time_slot
        units = _safe_int(record.get("workload_units", 1), 1)
        if str(record.get("duty_type", "")).lower() == "invigilation":
            row["invigilation_count"] += units
        else:
            row["distribution_count"] += units
        row["combined_count"] += units

    def _sort_key(slot: str) -> tuple[int, str]:
        if slot == "unscheduled":
            return (9999, slot)
        start = slot.split("-", 1)[0]
        parts = start.split(":")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            return (int(parts[0]) * 60 + int(parts[1]), slot)
        return (9998, slot)

    return [buckets[key] for key in sorted(buckets.keys(), key=_sort_key)]


def _build_fairness(person_rows: list[dict[str, Any]], aggregate_only: bool = False) -> dict[str, Any]:
    if aggregate_only:
        return {
            "imbalance_score": 0.0,
            "overloaded_people": [],
            "underloaded_people": [],
            "risk_band": "good",
        }

    staff_loads = [
        {
            "user_id": row["person_id"],
            "staff_name": row["display_name"],
            "department": row.get("role_group", ""),
            "total_load": row["combined_count"],
        }
        for row in person_rows
    ]
    analytics = compute_workload_analytics(staff_loads, [])
    average = sum(row["combined_count"] for row in person_rows) / len(person_rows) if person_rows else 0.0
    overloaded_threshold = average * 1.5 if average > 0 else 0.0
    underloaded_threshold = average * 0.5 if average > 0 else 0.0

    overloaded_people = [
        {
            "person_id": row["person_id"],
            "display_name": row["display_name"],
            "role_group": row["role_group"],
            "invigilation_count": row["invigilation_count"],
            "distribution_count": row["distribution_count"],
            "combined_count": row["combined_count"],
        }
        for row in person_rows
        if row["combined_count"] >= overloaded_threshold and overloaded_threshold > 0
    ]
    underloaded_people = [
        {
            "person_id": row["person_id"],
            "display_name": row["display_name"],
            "role_group": row["role_group"],
            "invigilation_count": row["invigilation_count"],
            "distribution_count": row["distribution_count"],
            "combined_count": row["combined_count"],
        }
        for row in person_rows
        if row["combined_count"] <= underloaded_threshold and underloaded_threshold > 0
    ]

    return {
        "imbalance_score": _safe_float(analytics.get("imbalance_score", 0.0)),
        "overloaded_people": overloaded_people,
        "underloaded_people": underloaded_people,
        "risk_band": _ROLE_RISK_BAND.get(str(analytics.get("fairness_band", "green")), "good"),
    }


class WorkloadDutyAnalyticsService:
    """Workload duty analytics aggregator."""

    @staticmethod
    def build_workload_duty_analytics(
        db,
        current_user: Any,
        semester: str | None = None,
        academic_year: str | None = None,
        period_id: int | None = None,
        exam_type: str | None = None,
        role_group: str = "all",
        person_id: str | None = None,
        include_teachers: bool = True,
        include_staff: bool = True,
        duty_type: str = "all",
    ) -> dict[str, Any]:
        filters = {
            "semester": semester,
            "academic_year": academic_year,
            "period_id": period_id,
            "exam_type": exam_type,
            "role_group": role_group,
            "person_id": person_id,
            "include_teachers": include_teachers,
            "include_staff": include_staff,
            "duty_type": duty_type,
        }
        if not can_view_workload_dashboard(current_user, filters):
            raise HTTPException(status_code=403, detail="ไม่ได้รับอนุญาตให้ดู workload dashboard")

        records = WorkloadDutyAnalyticsRepository.fetch_normalized_duty_records(db, period_id=period_id)
        return WorkloadDutyAnalyticsService.build_workload_duty_analytics_from_records(records, current_user, filters)

    @staticmethod
    def build_workload_duty_analytics_from_records(
        records: list[dict[str, Any]],
        current_user: Any | None,
        filters: dict[str, Any],
    ) -> dict[str, Any]:
        current_role = _user_role(current_user)
        requested_role_group = normalize_role_group(filters.get("role_group"))
        visible_roles = allowed_role_groups(current_user)
        aggregate_only = current_role == "dpo"

        if requested_role_group != "all" and requested_role_group not in visible_roles and current_role != "admin":
            raise HTTPException(status_code=403, detail="role_group นี้อยู่นอกขอบเขตของผู้ใช้ปัจจุบัน")

        effective_person_id = filters.get("person_id")
        if current_role == "teacher":
            effective_person_id = _user_identity(current_user)
            if filters.get("person_id") and str(filters.get("person_id")) != effective_person_id:
                raise HTTPException(status_code=403, detail="teacher ดูได้เฉพาะ workload ของตนเอง")

        scoped_records = [
            record
            for record in records
            if _is_visible_record(
                record,
                current_role,
                {
                    **filters,
                    "person_id": effective_person_id,
                    "role_group": requested_role_group,
                },
                current_user,
            )
        ]

        deduped_records = _dedupe_records(scoped_records)
        person_rows = _aggregate_by_person(deduped_records)
        daily_series = _aggregate_daily(deduped_records)
        time_slot_series = _aggregate_time_slots(deduped_records)
        fairness = _build_fairness(person_rows, aggregate_only=aggregate_only)

        total_invigilation = sum(row["invigilation_count"] for row in person_rows)
        total_distribution = sum(row["distribution_count"] for row in person_rows)
        total_combined = sum(row["combined_count"] for row in person_rows)
        average_per_person = round(total_combined / len(person_rows), 2) if person_rows else 0.0
        max_duties = max((row["combined_count"] for row in person_rows), default=0)

        payload = {
            "filters": {
                "semester": filters.get("semester"),
                "academic_year": filters.get("academic_year"),
                "period_id": filters.get("period_id"),
                "exam_type": filters.get("exam_type"),
                "role_group": requested_role_group,
                "person_id": filters.get("person_id"),
                "duty_type": filters.get("duty_type", "all"),
            },
            "summary": {
                "total_people": len(person_rows),
                "total_invigilation_duties": total_invigilation,
                "total_distribution_duties": total_distribution,
                "total_combined_duties": total_combined,
                "average_duties_per_person": average_per_person,
                "max_duties": max_duties,
                "imbalance_score": fairness["imbalance_score"],
            },
            "by_person": [] if aggregate_only else person_rows,
            "daily_series": daily_series,
            "time_slot_series": time_slot_series,
            "fairness": fairness,
        }
        return payload

    @staticmethod
    def serialize_workload_duty_analytics(payload: dict[str, Any]) -> dict[str, Any]:
        return WorkloadDutyAnalyticsSerializer.serialize_payload(payload)
