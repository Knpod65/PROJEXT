"""Preview-only advance invigilation batch roster service.

This module builds a read-only roster from existing invigilation assignments.
It never calculates money and never treats check-in as an advance inclusion gate.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy.orm import Session, joinedload

import models
from services.invigilation_rate_rule_service import get_simple_rates
from time_ranges import parse_time_range


ADVANCE_READY = "READY_FOR_BATCH_REVIEW"
BLOCKED_MISSING_DATA = "BLOCKED_MISSING_ASSIGNMENT_DATA"
BLOCKED_DUPLICATE = "BLOCKED_DUPLICATE_DUTY"
BLOCKED_RULE_GAP = "BLOCKED_RULE_GAP"
PENDING_RATE_RULE = "PENDING_RATE_RULE"
RATE_RULE_AVAILABLE = "RATE_RULE_AVAILABLE"
PREVIEW_CALCULATED = "PREVIEW_CALCULATED"
BLOCKED_MISSING_EXAM_DATE = "BLOCKED_MISSING_EXAM_DATE"
BLOCKED_INVALID_EXAM_DATE = "BLOCKED_INVALID_EXAM_DATE"
BLOCKED_ROSTER_INELIGIBLE = "BLOCKED_ROSTER_INELIGIBLE"
PENDING_RECONCILIATION = "PENDING_POST_DUTY_RECONCILIATION"
RATE_SOURCE = "SIMPLE_WEEKDAY_WEEKEND_RATE"
NOT_AUTHORIZED = "NOT_AUTHORIZED_PREVIEW_ONLY"


def _value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    text = str(_value(value)).strip()
    return text or None


def _normalized_exam_date(value: Any) -> dict[str, str | None]:
    original = _string(value)
    if not original:
        return {
            "exam_date": None,
            "exam_date_calendar": None,
            "normalized_exam_date": None,
            "rate_day_type": "UNKNOWN",
            "date_amount_status": BLOCKED_MISSING_EXAM_DATE,
        }

    try:
        parsed = value.date() if isinstance(value, datetime) else value
        if not isinstance(parsed, date):
            parsed = date.fromisoformat(original[:10])
        calendar = "BE_NORMALIZED" if parsed.year >= 2400 else "CE"
        normalized = date(parsed.year - 543, parsed.month, parsed.day) if parsed.year >= 2400 else parsed
    except (TypeError, ValueError, OverflowError):
        return {
            "exam_date": original,
            "exam_date_calendar": "UNKNOWN",
            "normalized_exam_date": None,
            "rate_day_type": "UNKNOWN",
            "date_amount_status": BLOCKED_INVALID_EXAM_DATE,
        }

    return {
        "exam_date": original,
        "exam_date_calendar": calendar,
        "normalized_exam_date": normalized.isoformat(),
        "rate_day_type": "WEEKEND" if normalized.weekday() >= 5 else "WEEKDAY",
        "date_amount_status": None,
    }


def _decimal_amount(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return amount if amount > 0 else None


def _configured_simple_rates(simple_rates: dict[str, Any] | None) -> dict[str, Decimal] | None:
    if not simple_rates or simple_rates.get("configuration_status") != "CONFIGURED":
        return None
    weekday = _decimal_amount((simple_rates.get("weekday_rate") or {}).get("amount"))
    weekend = _decimal_amount((simple_rates.get("weekend_rate") or {}).get("amount"))
    if weekday is None or weekend is None:
        return None
    return {"WEEKDAY": weekday, "WEEKEND": weekend}


def _time_bounds(schedule: Any) -> tuple[str | None, str | None]:
    start = _string(getattr(schedule, "exam_time_start", None))
    end = _string(getattr(schedule, "exam_time_end", None))
    if start or end:
        return start, end
    parsed_start, parsed_end = parse_time_range(getattr(schedule, "exam_time", None))
    return parsed_start, parsed_end


def _exam_type(schedule: Any) -> str | None:
    return _string(getattr(schedule, "exam_type", None))


def _period_lookup(periods: list[Any]) -> dict[tuple[str, str, str], Any]:
    lookup: dict[tuple[str, str, str], Any] = {}
    for period in periods:
        key = (
            str(getattr(period, "academic_year", "") or ""),
            str(getattr(period, "semester", "") or ""),
            str(_value(getattr(period, "exam_type", "")) or "").lower(),
        )
        lookup[key] = period
    return lookup


def _period_for_schedule(schedule: Any, lookup: dict[tuple[str, str, str], Any]) -> Any | None:
    section = getattr(schedule, "section", None)
    if section is None:
        return None
    key = (
        str(getattr(section, "academic_year", "") or ""),
        str(getattr(section, "semester", "") or ""),
        str(_exam_type(schedule) or "").lower(),
    )
    return lookup.get(key)


def _matches_filters(
    schedule: Any,
    period: Any | None,
    *,
    period_id: int | None,
    academic_year: str | None,
    semester: str | None,
    exam_type: str | None,
) -> bool:
    section = getattr(schedule, "section", None)
    if period_id is not None and getattr(period, "id", None) != period_id:
        return False
    if academic_year and str(getattr(section, "academic_year", "") or "") != str(academic_year):
        return False
    if semester and str(getattr(section, "semester", "") or "") != str(semester):
        return False
    if exam_type and str(_exam_type(schedule) or "").lower() != str(exam_type).lower():
        return False
    return True


def _duplicate_key(row: dict[str, Any]) -> tuple[str, str, str | None, str | None]:
    return (
        str(row.get("person_id") or ""),
        str(row.get("exam_date") or ""),
        row.get("start_time"),
        row.get("end_time"),
    )


def build_preview_from_schedules(
    schedules: list[Any],
    periods: list[Any] | None = None,
    simple_rates: dict[str, Any] | None = None,
    *,
    period_id: int | None = None,
    academic_year: str | None = None,
    semester: str | None = None,
    exam_type: str | None = None,
) -> dict[str, Any]:
    periods = periods or []
    lookup = _period_lookup(periods)
    rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    warnings: list[str] = []
    rule_gaps: set[str] = {
        "PAY-001 payment unit is pending.",
        "PAY-002/PAY-003 rate rule is pending; all amount fields are PENDING_RATE_RULE.",
        "PAY-009 advance batch approval owner is pending.",
    }

    for schedule in schedules:
        period = _period_for_schedule(schedule, lookup)
        if not _matches_filters(
            schedule,
            period,
            period_id=period_id,
            academic_year=academic_year,
            semester=semester,
            exam_type=exam_type,
        ):
            continue

        section = getattr(schedule, "section", None)
        course = getattr(section, "course", None) if section is not None else None
        room = getattr(schedule, "room", None)
        start_time, end_time = _time_bounds(schedule)
        schedule_id = getattr(schedule, "id", None)
        date_info = _normalized_exam_date(getattr(schedule, "exam_date", None))
        exam_date = date_info["exam_date"]
        schedule_status = str(_value(getattr(schedule, "status", "")) or "").lower()
        is_cancelled = schedule_status in {"cancelled", "canceled"}

        for supervision in getattr(schedule, "supervisions", []) or []:
            user = getattr(supervision, "user", None)
            duty_id = getattr(supervision, "id", None)
            row_warnings: list[str] = []
            blocked_reason = None
            inclusion_status = ADVANCE_READY

            if user is None or getattr(user, "id", None) is None:
                inclusion_status = BLOCKED_MISSING_DATA
                blocked_reason = "Missing assigned person."
            elif date_info["date_amount_status"] == BLOCKED_MISSING_EXAM_DATE or not (start_time or getattr(schedule, "exam_time", None)):
                inclusion_status = BLOCKED_MISSING_DATA
                blocked_reason = "Missing exam date or time."
            elif date_info["date_amount_status"] == BLOCKED_INVALID_EXAM_DATE:
                inclusion_status = BLOCKED_MISSING_DATA
                blocked_reason = "Invalid exam date."
            elif is_cancelled:
                inclusion_status = BLOCKED_RULE_GAP
                blocked_reason = "Cancelled-before-batch handling requires admin/finance rule."

            if room is None:
                row_warnings.append("Missing room; roster row remains reviewable.")
            if not getattr(supervision, "role_in_exam", None):
                row_warnings.append("Missing duty role; using UNKNOWN_ROLE.")
            if period is None:
                row_warnings.append("Missing payment period candidate.")
                rule_gaps.add("PAY-010 payment period is missing or not mapped.")
            if getattr(supervision, "is_swapped", False) or getattr(supervision, "is_emergency_sub", False):
                row_warnings.append("Substitution/emergency flag present; reconciliation rule pending.")
                rule_gaps.add("PAY-006/PAY-024 substitution handling is pending.")

            row = {
                "advance_batch_id": None,
                "batch_period": getattr(period, "label", None) if period is not None else None,
                "academic_year": str(getattr(section, "academic_year", "") or "") or None,
                "semester": str(getattr(section, "semester", "") or "") or None,
                "exam_period": _exam_type(schedule),
                "batch_status": "PREVIEW_ONLY",
                "prepared_by": None,
                "prepared_at": None,
                "approved_by": None,
                "approved_at": None,
                "duty_id": duty_id,
                "exam_id": schedule_id,
                "schedule_id": schedule_id,
                "course_code": getattr(course, "course_id", None),
                "course_title": getattr(course, "course_name_en", None) or getattr(course, "course_name_th", None),
                "section": getattr(section, "section_no", None),
                "exam_date": exam_date,
                "exam_date_calendar": date_info["exam_date_calendar"],
                "normalized_exam_date": date_info["normalized_exam_date"],
                "start_time": start_time,
                "end_time": end_time,
                "room_id": getattr(room, "id", None) if room is not None else None,
                "room_name": getattr(room, "room_name", None) if room is not None else None,
                "person_id": str(getattr(user, "id", "")) if user is not None and getattr(user, "id", None) is not None else None,
                "person_name": (
                    getattr(user, "full_name", None) or getattr(user, "username", None)
                    if user is not None
                    else None
                ),
                "person_type": _string(getattr(user, "role", None)) if user is not None else None,
                "department": getattr(user, "department", None) if user is not None else None,
                "duty_role": getattr(supervision, "role_in_exam", None) or "UNKNOWN_ROLE",
                "advance_inclusion_status": inclusion_status,
                "inclusion_reason": "Assigned invigilation duty included for advance roster review." if inclusion_status == ADVANCE_READY else None,
                "blocked_reason": blocked_reason,
                "rate_rule_status": PENDING_RATE_RULE,
                "amount_status": PENDING_RATE_RULE,
                "amount_preview": None,
                "rate_day_type": date_info["rate_day_type"],
                "rate_source": None,
                "payment_authorization_status": NOT_AUTHORIZED,
                "_date_amount_status": date_info["date_amount_status"],
                "reconciliation_status": PENDING_RECONCILIATION,
                "post_duty_evidence_status": "NOT_REVIEWED",
                "absence_explanation_status": "NOT_REQUIRED_YET",
                "refund_offset_status": "NOT_STARTED",
                "source_record_ref": f"supervisions:{duty_id}" if duty_id is not None else f"schedule:{schedule_id}:supervision:unknown",
                "audit_note": "Preview only. No amount calculated. Check-in is not an advance inclusion gate.",
                "warnings": row_warnings,
            }
            rows.append(row)
            warnings.extend(f"{row['source_record_ref']}: {item}" for item in row_warnings)
            if blocked_reason:
                blockers.append(f"{row['source_record_ref']}: {blocked_reason}")

    duplicates = Counter(_duplicate_key(row) for row in rows if row.get("person_id") and row.get("exam_date"))
    for row in rows:
        key = _duplicate_key(row)
        if duplicates.get(key, 0) > 1:
            row["advance_inclusion_status"] = BLOCKED_DUPLICATE
            row["blocked_reason"] = "Duplicate same person/date/time duty."
            warning = f"{row['source_record_ref']}: Duplicate same person/date/time duty."
            blockers.append(warning)
            row.setdefault("warnings", []).append("Duplicate same person/date/time duty.")

    configured_rates = _configured_simple_rates(simple_rates)
    preview_total = Decimal("0")
    preview_weekday_count = 0
    preview_weekend_count = 0
    pending_rate_rule_count = 0
    missing_exam_date_count = 0
    invalid_exam_date_count = 0
    blocked_roster_amount_count = 0

    for row in rows:
        date_amount_status = row.pop("_date_amount_status", None)
        row["rate_rule_status"] = RATE_RULE_AVAILABLE if configured_rates else PENDING_RATE_RULE

        if date_amount_status == BLOCKED_MISSING_EXAM_DATE:
            row["amount_status"] = BLOCKED_MISSING_EXAM_DATE
            missing_exam_date_count += 1
        elif date_amount_status == BLOCKED_INVALID_EXAM_DATE:
            row["amount_status"] = BLOCKED_INVALID_EXAM_DATE
            invalid_exam_date_count += 1
        elif row["advance_inclusion_status"] != ADVANCE_READY:
            row["amount_status"] = BLOCKED_ROSTER_INELIGIBLE
            blocked_roster_amount_count += 1
        elif not configured_rates:
            row["amount_status"] = PENDING_RATE_RULE
            pending_rate_rule_count += 1
        else:
            day_type = row["rate_day_type"]
            amount = configured_rates[day_type]
            row["amount_status"] = PREVIEW_CALCULATED
            row["amount_preview"] = amount
            row["rate_source"] = RATE_SOURCE
            preview_total += amount
            if day_type == "WEEKDAY":
                preview_weekday_count += 1
            else:
                preview_weekend_count += 1

    status_counts = Counter(row["advance_inclusion_status"] for row in rows)
    ready_count = status_counts.get(ADVANCE_READY, 0)
    blocked_count = len(rows) - ready_count

    if configured_rates:
        rule_gaps.discard("PAY-001 payment unit is pending.")
        rule_gaps.discard("PAY-002/PAY-003 rate rule is pending; all amount fields are PENDING_RATE_RULE.")

    return {
        "summary": {
            "preview_only": True,
            "amount_calculation": "PREVIEW_ONLY" if configured_rates else "NOT_IMPLEMENTED",
            "amount_calculation_enabled": False,
            "amount_status": PREVIEW_CALCULATED if configured_rates else PENDING_RATE_RULE,
            "preview_amount_enabled": configured_rates is not None,
            "preview_total_amount": preview_total,
            "preview_weekday_count": preview_weekday_count,
            "preview_weekend_count": preview_weekend_count,
            "total_rows": len(rows),
            "total_assignments": len(rows),
            "ready_for_batch_review": ready_count,
            "included_in_advance_batch": 0,
            "blocked_missing_assignment_data": status_counts.get(BLOCKED_MISSING_DATA, 0),
            "blocked_duplicate_duty": status_counts.get(BLOCKED_DUPLICATE, 0),
            "blocked_rule_gap": status_counts.get(BLOCKED_RULE_GAP, 0),
            "blocked_rows": blocked_count,
            "pending_rate_rule_count": pending_rate_rule_count,
            "missing_exam_date_count": missing_exam_date_count,
            "invalid_exam_date_count": invalid_exam_date_count,
            "blocked_roster_amount_count": blocked_roster_amount_count,
            "warning_count": len(warnings),
            "payment_authorization_enabled": False,
            "final_export_enabled": False,
        },
        "roster_rows": rows,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "rule_gaps": sorted(rule_gaps),
    }


def build_advance_batch_preview(
    db: Session,
    *,
    period_id: int | None = None,
    academic_year: str | None = None,
    semester: str | None = None,
    exam_type: str | None = None,
) -> dict[str, Any]:
    schedules = db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
        joinedload(models.ExamSchedule.room),
        joinedload(models.ExamSchedule.supervisions).joinedload(models.Supervision.user),
    ).all()
    periods = db.query(models.ExamPeriod).all()
    simple_rates = get_simple_rates(db)
    return build_preview_from_schedules(
        schedules,
        periods,
        simple_rates,
        period_id=period_id,
        academic_year=academic_year,
        semester=semester,
        exam_type=exam_type,
    )
