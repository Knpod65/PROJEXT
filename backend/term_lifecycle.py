from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models


TERM_STATUS_DRAFT = "draft"
TERM_STATUS_ACTIVE = "active"
TERM_STATUS_ARCHIVED = "archived"
TERM_STATUS_LOCKED = "locked"
LOCKED_TERM_MESSAGE = "This term has been closed and is now read-only. Editing is no longer allowed."

EDITABLE_STATUSES = {TERM_STATUS_DRAFT, TERM_STATUS_ACTIVE, TERM_STATUS_ARCHIVED}
CLOSEABLE_STATUSES = {TERM_STATUS_ACTIVE, TERM_STATUS_ARCHIVED}


def semester_sort_value(value: Optional[str]) -> int:
    mapping = {"1": 1, "2": 2, "summer": 3}
    return mapping.get(str(value).lower(), 0)


def exam_type_sort_value(value: Optional[str]) -> int:
    mapping = {"midterm": 1, "final": 2}
    return mapping.get(str(value).lower(), 0)


def get_period_status(period: "models.ExamPeriod") -> str:
    status = getattr(period, "lifecycle_status", None)
    if status:
        return status
    return TERM_STATUS_ACTIVE if period.is_active else TERM_STATUS_ARCHIVED


def is_period_locked(period: "models.ExamPeriod") -> bool:
    return get_period_status(period) == TERM_STATUS_LOCKED


def is_period_historical(period: "models.ExamPeriod") -> bool:
    return get_period_status(period) in {TERM_STATUS_ARCHIVED, TERM_STATUS_LOCKED}


def is_period_editable(period: "models.ExamPeriod") -> bool:
    return get_period_status(period) in EDITABLE_STATUSES


def period_summary(period: "models.ExamPeriod") -> str:
    status = get_period_status(period)
    if status == TERM_STATUS_ACTIVE:
        return "This term is active and editable."
    if status == TERM_STATUS_LOCKED:
        return "This term has been closed and is now read-only."
    if status == TERM_STATUS_ARCHIVED:
        return "This is a historical term. Historical data remains visible for audit and reporting."
    return "This term is in draft setup and can be edited before activation."


def period_preview_summary(period: "models.ExamPeriod") -> str:
    status = get_period_status(period)
    if status == TERM_STATUS_LOCKED:
        return "This term is locked. Admin Settings shows it as read-only preview."
    if status == TERM_STATUS_ARCHIVED:
        return "This term is historical. Admin Settings preview remains read-only while historical data stays visible."
    if status == TERM_STATUS_ACTIVE:
        return "This term is active and editable."
    return "This term is still in draft setup."


def period_to_dict(period: "models.ExamPeriod") -> dict:
    return {
        "id": period.id,
        "academic_year": period.academic_year,
        "semester": period.semester,
        "exam_type": period.exam_type,
        "label": period.label,
        "is_active": period.is_active,
        "lifecycle_status": get_period_status(period),
        "is_historical": is_period_historical(period),
        "is_editable": is_period_editable(period),
        "is_read_only": is_period_locked(period),
        "status_summary": period_summary(period),
        "preview_summary": period_preview_summary(period),
        "archived_at": period.archived_at.isoformat() if getattr(period, "archived_at", None) else None,
        "locked_at": period.locked_at.isoformat() if getattr(period, "locked_at", None) else None,
        "created_at": period.created_at.isoformat() if period.created_at else None,
    }


def sort_periods(periods: list["models.ExamPeriod"]) -> list["models.ExamPeriod"]:
    return sorted(
        periods,
        key=lambda period: (
            int(period.academic_year or 0),
            semester_sort_value(period.semester),
            exam_type_sort_value(period.exam_type),
            period.id or 0,
        ),
        reverse=True,
    )


def get_all_periods(db: Session) -> list["models.ExamPeriod"]:
    return sort_periods(db.query(models.ExamPeriod).all())


def get_active_period(db: Session) -> Optional["models.ExamPeriod"]:
    active_period = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.lifecycle_status == TERM_STATUS_ACTIVE
    ).first()
    if active_period:
        return active_period
    return db.query(models.ExamPeriod).filter(
        models.ExamPeriod.is_active == True
    ).first()


def get_latest_term(db: Session) -> Optional["models.ExamPeriod"]:
    periods = get_all_periods(db)
    return periods[0] if periods else None


def get_latest_historical_term(db: Session) -> Optional["models.ExamPeriod"]:
    periods = [
        period for period in get_all_periods(db)
        if is_period_historical(period)
    ]
    return periods[0] if periods else None


def get_default_preview_term(db: Session) -> Optional["models.ExamPeriod"]:
    return get_active_period(db) or get_latest_historical_term(db) or get_latest_term(db)


def get_period_by_id(db: Session, period_id: int) -> Optional["models.ExamPeriod"]:
    return db.query(models.ExamPeriod).filter(models.ExamPeriod.id == period_id).first()


def resolve_preview_term(db: Session, period_id: Optional[int] = None) -> Optional["models.ExamPeriod"]:
    if period_id is not None:
        return get_period_by_id(db, period_id)
    return get_default_preview_term(db)


def find_period(
    db: Session,
    academic_year: str,
    semester: str,
    exam_type: Optional[str] = None,
) -> Optional["models.ExamPeriod"]:
    query = db.query(models.ExamPeriod).filter(
        models.ExamPeriod.academic_year == academic_year,
        models.ExamPeriod.semester == semester,
    )
    if exam_type:
        query = query.filter(models.ExamPeriod.exam_type == exam_type)
    else:
        query = query.order_by(models.ExamPeriod.id.desc())
    return query.first()


def assert_period_editable(
    db: Session,
    academic_year: str,
    semester: str,
    exam_type: Optional[str] = None,
) -> Optional["models.ExamPeriod"]:
    period = find_period(db, academic_year, semester, exam_type)
    if period and is_period_locked(period):
        raise ValueError("Selected term is locked and read-only")
    return period


def locked_term_http_exception() -> HTTPException:
    return HTTPException(status_code=409, detail=LOCKED_TERM_MESSAGE)


def ensure_period_record_editable(period: Optional["models.ExamPeriod"]) -> Optional["models.ExamPeriod"]:
    if period and is_period_locked(period):
        raise locked_term_http_exception()
    return period


def require_period_editable_for_values(
    db: Session,
    academic_year: str,
    semester: str,
    exam_type: Optional[str] = None,
) -> Optional["models.ExamPeriod"]:
    period = find_period(db, academic_year, semester, exam_type)
    return ensure_period_record_editable(period)


def require_active_period_for_mutation(
    db: Session,
    missing_message: str = "ไม่มี active period",
) -> "models.ExamPeriod":
    active_period = get_active_period(db)
    if active_period:
        ensure_period_record_editable(active_period)
        return active_period

    latest_term = get_latest_term(db)
    if latest_term and is_period_locked(latest_term):
        raise locked_term_http_exception()

    raise HTTPException(status_code=400, detail=missing_message)


def get_close_blocking_reasons(period: Optional["models.ExamPeriod"]) -> list[str]:
    if not period:
        return ["Selected term does not exist."]

    status = get_period_status(period)
    blockers: list[str] = []

    if status == TERM_STATUS_LOCKED:
        blockers.append("This term is already locked.")

    if status not in CLOSEABLE_STATUSES:
        blockers.append("Only active or archived terms can be closed.")

    return blockers


def mark_period_active(period: "models.ExamPeriod") -> None:
    period.is_active = True
    period.lifecycle_status = TERM_STATUS_ACTIVE
    period.archived_at = None
    period.locked_at = None


def mark_period_archived(period: "models.ExamPeriod") -> None:
    period.is_active = False
    if get_period_status(period) != TERM_STATUS_LOCKED:
        period.lifecycle_status = TERM_STATUS_ARCHIVED
    if not getattr(period, "archived_at", None):
        period.archived_at = datetime.now(timezone.utc)


def mark_period_locked(period: "models.ExamPeriod") -> None:
    period.is_active = False
    period.lifecycle_status = TERM_STATUS_LOCKED
    if not getattr(period, "archived_at", None):
        period.archived_at = datetime.now(timezone.utc)
    period.locked_at = datetime.now(timezone.utc)
