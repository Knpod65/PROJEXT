"""Configurable settings for draft payment-document preparation.

Settings are separate from payment truth, review records, active simple rates,
and export/authorization workflows.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from auth_utils import get_effective_role

READ_ROLES = {
    models.UserRole.admin,
    models.UserRole.esq_head,
    models.UserRole.secretary,
    models.UserRole.staff,
}

WRITE_ROLES = {
    models.UserRole.admin,
    models.UserRole.esq_head,
    models.UserRole.secretary,
}

ALLOWED_STATUSES = {
    "DRAFT_CONFIG",
    "ACTIVE_FOR_DRAFT_PREVIEW",
    "ARCHIVED",
}

DEFAULT_RESPONSIBLE_GROUP = "Education_Student_Quality"
PAYMENT_UNIT = "PER_PERSON_SESSION"
CURRENCY = "THB"


def _role(user: models.User) -> models.UserRole:
    return get_effective_role(user)


def _ensure_read(user: models.User) -> None:
    if _role(user) not in READ_ROLES:
        raise HTTPException(status_code=403, detail="payment document settings access requires staff or reviewer role")


def _ensure_write(user: models.User) -> None:
    if _role(user) not in WRITE_ROLES:
        raise HTTPException(status_code=403, detail="payment document settings updates require reviewer role")


def _settings_id(term: str) -> str:
    return f"payment-document-settings-{term.replace('/', '-')}"


def _clean_text(value: Any, default: str | None = None) -> str | None:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _positive_amount(value: Any, field_name: str) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise HTTPException(status_code=400, detail=f"{field_name} must be numeric")
    if amount <= 0:
        raise HTTPException(status_code=400, detail=f"{field_name} must be positive")
    return amount


def _status_value(value: object) -> str:
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)


def _status_enum(value: object) -> models.PaymentDocumentSettingsStatus:
    status = _status_value(value)
    if status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="unknown payment document settings status")
    return models.PaymentDocumentSettingsStatus(status)


def _validate_constants(currency: str, payment_unit: str) -> None:
    if currency.upper() != CURRENCY:
        raise HTTPException(status_code=400, detail="currency must be THB")
    if payment_unit != PAYMENT_UNIT:
        raise HTTPException(status_code=400, detail="payment_unit must be PER_PERSON_SESSION")


def _validate_dates(effective_from, effective_to) -> None:
    if effective_from and effective_to and effective_to < effective_from:
        raise HTTPException(status_code=400, detail="effective_to must not be earlier than effective_from")


def _serialize(record: models.PaymentDocumentSettings) -> schemas.PaymentDocumentSettingsOut:
    return schemas.PaymentDocumentSettingsOut(
        settings_id=record.settings_id,
        term=record.term,
        weekday_rate=record.weekday_rate,
        weekend_rate=record.weekend_rate,
        currency=record.currency,
        payment_unit=record.payment_unit,
        paper_distribution_responsible_group=record.paper_distribution_responsible_group,
        paper_distribution_responsible_person=record.paper_distribution_responsible_person,
        status=_status_value(record.status),
        configuration_status="CONFIGURED",
        effective_from=record.effective_from,
        effective_to=record.effective_to,
        note=record.note,
        updated_by=record.updated_by,
        updated_at=record.updated_at,
        payment_authorization_enabled=False,
        final_export_enabled=False,
    )


def _pending(term: str) -> schemas.PaymentDocumentSettingsOut:
    return schemas.PaymentDocumentSettingsOut(
        settings_id=_settings_id(term),
        term=term,
        weekday_rate=None,
        weekend_rate=None,
        currency=CURRENCY,
        payment_unit=PAYMENT_UNIT,
        paper_distribution_responsible_group=DEFAULT_RESPONSIBLE_GROUP,
        paper_distribution_responsible_person=None,
        status="DRAFT_CONFIG",
        configuration_status="PENDING_CONFIGURATION",
        effective_from=None,
        effective_to=None,
        note="Suggested defaults only. Save settings before using them as draft-document configuration.",
        updated_by=None,
        updated_at=None,
        payment_authorization_enabled=False,
        final_export_enabled=False,
    )


def list_payment_document_settings(
    db: Session,
    *,
    current_user: models.User,
) -> schemas.PaymentDocumentSettingsListResponse:
    _ensure_read(current_user)
    records = db.query(models.PaymentDocumentSettings).order_by(
        models.PaymentDocumentSettings.term.asc()
    ).all()
    return schemas.PaymentDocumentSettingsListResponse(
        settings=[_serialize(record) for record in records],
        payment_authorization_enabled=False,
        final_export_enabled=False,
    )


def get_payment_document_settings(
    db: Session,
    *,
    current_user: models.User,
    term: str,
) -> schemas.PaymentDocumentSettingsOut:
    _ensure_read(current_user)
    clean_term = _clean_text(term)
    if not clean_term:
        raise HTTPException(status_code=400, detail="term is required")
    record = db.query(models.PaymentDocumentSettings).filter(
        models.PaymentDocumentSettings.term == clean_term
    ).first()
    return _serialize(record) if record else _pending(clean_term)


def save_payment_document_settings(
    db: Session,
    *,
    current_user: models.User,
    term: str,
    payload: schemas.PaymentDocumentSettingsUpdate,
) -> schemas.PaymentDocumentSettingsOut:
    _ensure_write(current_user)
    clean_path_term = _clean_text(term)
    clean_body_term = _clean_text(payload.term)
    if not clean_path_term or not clean_body_term:
        raise HTTPException(status_code=400, detail="term is required")
    if clean_path_term != clean_body_term:
        raise HTTPException(status_code=400, detail="path term and payload term must match")

    _validate_constants(payload.currency, payload.payment_unit)
    _validate_dates(payload.effective_from, payload.effective_to)
    weekday_rate = _positive_amount(payload.weekday_rate, "weekday_rate")
    weekend_rate = _positive_amount(payload.weekend_rate, "weekend_rate")
    responsible_group = _clean_text(payload.paper_distribution_responsible_group)
    if not responsible_group:
        raise HTTPException(status_code=400, detail="paper_distribution_responsible_group is required")

    status = _status_enum(payload.status)
    now = datetime.now(timezone.utc)
    record = db.query(models.PaymentDocumentSettings).filter(
        models.PaymentDocumentSettings.term == clean_path_term
    ).first()
    if not record:
        record = models.PaymentDocumentSettings(
            settings_id=_settings_id(clean_path_term),
            term=clean_path_term,
        )
        db.add(record)

    record.weekday_rate = weekday_rate
    record.weekend_rate = weekend_rate
    record.currency = CURRENCY
    record.payment_unit = PAYMENT_UNIT
    record.paper_distribution_responsible_group = responsible_group
    record.paper_distribution_responsible_person = _clean_text(payload.paper_distribution_responsible_person)
    record.status = status
    record.effective_from = payload.effective_from
    record.effective_to = payload.effective_to
    record.note = _clean_text(payload.note)
    record.updated_by = getattr(current_user, "id", None)
    record.updated_at = now
    record.payment_authorization_enabled = False
    record.final_export_enabled = False

    db.commit()
    db.refresh(record)
    return _serialize(record)
