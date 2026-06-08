"""Official-style payment document draft preview service.

This service builds an in-app draft table only. Amounts come from the
term-specific payment document settings source and never from active demo
simple-rate configuration.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session, joinedload

import models
from services.invigilation_advance_batch_preview_service import (
    ADVANCE_READY,
    build_preview_from_schedules,
)
from services.payment_document_settings_service import (
    SETTINGS_CONFIGURED,
    SETTINGS_INCOMPLETE,
    resolve_payment_document_settings_for_draft,
)
from time_ranges import normalize_time_range, parse_time_range


PAPER_SOURCE_STATUS = "STAFF_CONFIRMED_MANUAL_DRAFT_INPUT"
CALCULATED_FROM_SETTINGS = "CALCULATED_FROM_SETTINGS"
BLOCKED_PENDING_SETTINGS = "BLOCKED_PENDING_SETTINGS"
BLOCKED_INCOMPLETE_SETTINGS = "BLOCKED_INCOMPLETE_SETTINGS"


def _value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    text = str(_value(value)).strip()
    return text or None


def _normalize_exam_date(value: Any, rates: dict[str, Decimal] | None) -> dict[str, Any]:
    original = _string(value)
    if not original:
        return {
            "exam_date": "",
            "normalized_exam_date": None,
            "day_type": "UNKNOWN",
            "rate_amount": None,
            "valid": False,
        }
    try:
        parsed = value.date() if isinstance(value, datetime) else value
        if not isinstance(parsed, date):
            parsed = date.fromisoformat(original[:10])
        normalized = date(parsed.year - 543, parsed.month, parsed.day) if parsed.year >= 2400 else parsed
    except (TypeError, ValueError, OverflowError):
        return {
            "exam_date": original,
            "normalized_exam_date": None,
            "day_type": "UNKNOWN",
            "rate_amount": None,
            "valid": False,
        }
    day_type = "WEEKEND" if normalized.weekday() >= 5 else "WEEKDAY"
    return {
        "exam_date": original,
        "normalized_exam_date": normalized.isoformat(),
        "day_type": day_type,
        "rate_amount": rates.get(day_type) if rates else None,
        "valid": True,
    }


def _normalize_slot(start_time: str | None, end_time: str | None, exam_time: str | None) -> tuple[str | None, str | None, str]:
    start = _string(start_time)
    end = _string(end_time)
    if not (start and end):
        parsed_start, parsed_end = parse_time_range(exam_time)
        start = start or parsed_start
        end = end or parsed_end
    normalized = normalize_time_range(start, end)
    if normalized:
        slot_start, slot_end = normalized.split("-", 1)
        return slot_start, slot_end, normalized
    fallback = _string(exam_time)
    return start, end, fallback or "unscheduled"


def _bucket_key(normalized_exam_date: str | None, time_slot: str, exam_date: str) -> tuple[str, str]:
    return (normalized_exam_date or exam_date or "unknown-date", time_slot)


def _preview_rates(settings: dict[str, Any]) -> dict[str, Any] | None:
    if settings["settings_source_status"] != SETTINGS_CONFIGURED:
        return None
    return {
        "configuration_status": "CONFIGURED",
        "weekday_rate": {"amount": settings["weekday_rate"]},
        "weekend_rate": {"amount": settings["weekend_rate"]},
    }


def _period_lookup(periods: list[Any]) -> dict[int, Any]:
    return {period.id: period for period in periods if getattr(period, "id", None) is not None}


def _term_context(payload: dict[str, Any], periods: list[Any]) -> dict[str, Any]:
    period = _period_lookup(periods).get(payload.get("period_id")) if payload.get("period_id") is not None else None
    academic_year = payload.get("academic_year") or getattr(period, "academic_year", None)
    semester = payload.get("semester") or getattr(period, "semester", None)
    exam_type = payload.get("exam_type") or getattr(period, "exam_type", None) or "final"
    return {
        "academic_year": str(academic_year) if academic_year is not None else None,
        "semester": str(semester) if semester is not None else None,
        "exam_type": str(_value(exam_type)) if exam_type is not None else None,
        "term_label": f"{semester or ''}/{academic_year or ''}".strip("/"),
    }


def _calculation_status(settings_source_status: str) -> str:
    if settings_source_status == SETTINGS_CONFIGURED:
        return CALCULATED_FROM_SETTINGS
    if settings_source_status == SETTINGS_INCOMPLETE:
        return BLOCKED_INCOMPLETE_SETTINGS
    return BLOCKED_PENDING_SETTINGS


def _metadata(term_context: dict[str, Any], settings: dict[str, Any]) -> dict[str, Any]:
    return {
        **term_context,
        "document_status": "DRAFT_NOT_AUTHORIZED",
        "rate_source": f"PAYMENT_DOCUMENT_SETTINGS:{settings['settings_id']}" if settings["settings_id"] else "PAYMENT_DOCUMENT_SETTINGS",
        "weekday_rate": settings["weekday_rate"] if settings["settings_source_status"] == SETTINGS_CONFIGURED else None,
        "weekend_rate": settings["weekend_rate"] if settings["settings_source_status"] == SETTINGS_CONFIGURED else None,
        "rate_scope": f"TERM_SPECIFIC:{settings['settings_term']}" if settings["settings_term"] else "TERM_UNRESOLVED",
        "paper_distribution_source_status": PAPER_SOURCE_STATUS,
        "settings_source_status": settings["settings_source_status"],
        "settings_term": settings["settings_term"],
        "settings_status": settings["settings_status"],
        "settings_weekday_rate": settings["weekday_rate"],
        "settings_weekend_rate": settings["weekend_rate"],
        "currency": settings["currency"],
        "payment_unit": settings["payment_unit"],
        "paper_distribution_responsible_group": settings["paper_distribution_responsible_group"],
        "paper_distribution_responsible_person": settings["paper_distribution_responsible_person"],
        "calculation_status": _calculation_status(settings["settings_source_status"]),
        "settings_issues": settings["settings_issues"],
    }


def build_official_payment_document_draft_from_sources(
    schedules: list[Any],
    periods: list[Any] | None,
    request_payload: dict[str, Any],
    settings: dict[str, Any],
) -> dict[str, Any]:
    """Build a non-persistent official-style draft table."""
    periods = periods or []
    configured = settings["settings_source_status"] == SETTINGS_CONFIGURED
    rates = (
        {"WEEKDAY": settings["weekday_rate"], "WEEKEND": settings["weekend_rate"]}
        if configured
        else None
    )
    preview = build_preview_from_schedules(
        schedules,
        periods,
        _preview_rates(settings),
        period_id=request_payload.get("period_id"),
        academic_year=request_payload.get("academic_year"),
        semester=request_payload.get("semester"),
        exam_type=request_payload.get("exam_type"),
    )
    buckets: dict[tuple[str, str], dict[str, Any]] = {}
    warnings: set[str] = set(preview.get("warnings", []))
    warnings.update(settings["settings_issues"])

    for row in preview.get("roster_rows", []):
        if row.get("advance_inclusion_status") != ADVANCE_READY:
            reason = row.get("blocked_reason") or row.get("advance_inclusion_status")
            warnings.add(f"{row.get('source_record_ref')}: invigilation row excluded from draft count ({reason}).")
            continue
        date_info = _normalize_exam_date(row.get("exam_date"), rates)
        start, end, time_slot = _normalize_slot(row.get("start_time"), row.get("end_time"), None)
        key = _bucket_key(date_info["normalized_exam_date"], time_slot, date_info["exam_date"])
        bucket = buckets.setdefault(
            key,
            {
                "exam_date": date_info["exam_date"],
                "normalized_exam_date": date_info["normalized_exam_date"],
                "time_slot": time_slot,
                "start_time": start,
                "end_time": end,
                "day_type": date_info["day_type"],
                "rate_amount": date_info["rate_amount"],
                "invigilation_committee_count": 0,
                "paper_distribution_committee_count": 0,
                "source_notes": [],
                "warnings": [],
            },
        )
        bucket["invigilation_committee_count"] += 1
        bucket["source_notes"].append(str(row.get("source_record_ref") or "supervision"))

    for index, manual_row in enumerate(request_payload.get("paper_distribution_rows") or [], start=1):
        date_info = _normalize_exam_date(manual_row.get("exam_date"), rates)
        if not date_info["valid"]:
            warnings.add(f"manual-paper-row:{index}: invalid exam_date; row skipped.")
            continue
        start, end, time_slot = _normalize_slot(
            manual_row.get("start_time"),
            manual_row.get("end_time"),
            manual_row.get("exam_time"),
        )
        key = _bucket_key(date_info["normalized_exam_date"], time_slot, date_info["exam_date"])
        matched_existing = key in buckets
        bucket = buckets.setdefault(
            key,
            {
                "exam_date": date_info["exam_date"],
                "normalized_exam_date": date_info["normalized_exam_date"],
                "time_slot": time_slot,
                "start_time": start,
                "end_time": end,
                "day_type": date_info["day_type"],
                "rate_amount": date_info["rate_amount"],
                "invigilation_committee_count": 0,
                "paper_distribution_committee_count": 0,
                "source_notes": [],
                "warnings": [],
            },
        )
        count = int(manual_row.get("committee_count") or 0)
        bucket["paper_distribution_committee_count"] += count
        note = manual_row.get("notes")
        bucket["source_notes"].append(f"manual-paper-row:{index}" + (f" {note}" if note else ""))
        if not matched_existing:
            warning = f"manual-paper-row:{index}: paper-distribution slot has no matching invigilation draft row."
            bucket["warnings"].append(warning)
            warnings.add(warning)

    rows: list[dict[str, Any]] = []
    totals = defaultdict(lambda: Decimal("0"))
    total_inv_count = 0
    total_paper_count = 0

    for bucket in sorted(buckets.values(), key=lambda item: (item["normalized_exam_date"] or item["exam_date"], item["time_slot"])):
        rate = bucket["rate_amount"]
        inv_count = int(bucket["invigilation_committee_count"])
        paper_count = int(bucket["paper_distribution_committee_count"])
        inv_amount = rate * inv_count if rate is not None else None
        paper_amount = rate * paper_count if rate is not None else None
        total_amount = inv_amount + paper_amount if inv_amount is not None and paper_amount is not None else None
        rows.append(
            {
                **bucket,
                "invigilation_compensation_amount": inv_amount,
                "paper_distribution_compensation_amount": paper_amount,
                "total_compensation_amount": total_amount,
            }
        )
        total_inv_count += inv_count
        total_paper_count += paper_count
        if configured:
            totals["invigilation_compensation_amount"] += inv_amount
            totals["paper_distribution_compensation_amount"] += paper_amount
            totals["grand_total_amount"] += total_amount

    return {
        "metadata": _metadata(_term_context(request_payload, periods), settings),
        "rows": rows,
        "totals": {
            "invigilation_committee_count": total_inv_count,
            "invigilation_compensation_amount": totals["invigilation_compensation_amount"] if configured else None,
            "paper_distribution_committee_count": total_paper_count,
            "paper_distribution_compensation_amount": totals["paper_distribution_compensation_amount"] if configured else None,
            "grand_total_amount": totals["grand_total_amount"] if configured else None,
            "row_count": len(rows),
        },
        "warnings": sorted(warnings),
        "draft_only": True,
        "payment_authorization_enabled": False,
        "final_export_enabled": False,
        "supervisor_finance_review_required": True,
    }


def build_official_payment_document_draft_preview(db: Session, request_payload: dict[str, Any]) -> dict[str, Any]:
    schedules = db.query(models.ExamSchedule).options(
        joinedload(models.ExamSchedule.section).joinedload(models.Section.course),
        joinedload(models.ExamSchedule.room),
        joinedload(models.ExamSchedule.supervisions).joinedload(models.Supervision.user),
    ).all()
    periods = db.query(models.ExamPeriod).all()
    term_context = _term_context(request_payload, periods)
    settings = resolve_payment_document_settings_for_draft(
        db,
        term=term_context["term_label"] or None,
    )
    return build_official_payment_document_draft_from_sources(schedules, periods, request_payload, settings)
