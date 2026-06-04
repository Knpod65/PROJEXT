"""Configuration-only invigilation payment rate rule service.

This service stores user-entered rate rules. It does not calculate payment,
authorize payment, or export official payment reports.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
from services.unit_of_work import atomic


SUPPORTED_PAYMENT_UNITS = {"PER_SESSION"}
DRAFT = "DRAFT"
ACTIVE = "ACTIVE"
ARCHIVED = "ARCHIVED"
SIMPLE_WEEKDAY_SCOPE = "EMS_SIMPLE_WEEKDAY"
SIMPLE_WEEKEND_SCOPE = "EMS_SIMPLE_WEEKEND"
SIMPLE_RATE_SCOPES = {SIMPLE_WEEKDAY_SCOPE, SIMPLE_WEEKEND_SCOPE}
SIMPLE_RATE_NAMES = {
    SIMPLE_WEEKDAY_SCOPE: "EMS Simple Weekday Invigilation Rate",
    SIMPLE_WEEKEND_SCOPE: "EMS Simple Weekend Invigilation Rate",
}


def _enum_value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _clean_text(value: Any, default: str | None = None) -> str | None:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _amount(value: Any) -> Decimal:
    if value is None:
        raise HTTPException(status_code=400, detail="rate_amount is required")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise HTTPException(status_code=400, detail="rate_amount must be numeric")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="rate_amount must be positive")
    return amount


def _validate_unit(value: Any) -> models.InvigilationPaymentUnit:
    unit = _clean_text(value, "PER_SESSION")
    if unit not in SUPPORTED_PAYMENT_UNITS:
        raise HTTPException(status_code=400, detail="payment_unit is not supported in this implementation")
    return models.InvigilationPaymentUnit.per_session


def _validate_dates(effective_from: date | None, effective_to: date | None) -> None:
    if effective_from and effective_to and effective_to < effective_from:
        raise HTTPException(status_code=400, detail="effective_to must not be earlier than effective_from")


def _status(rule: models.InvigilationPaymentRateRule) -> str:
    return _enum_value(rule.status)


def _normalized_scope(value: Any) -> str:
    return (_clean_text(value, "ALL") or "ALL").upper()


def _is_simple_scope(value: Any) -> bool:
    return _normalized_scope(value) in SIMPLE_RATE_SCOPES


def _assert_generic_scope_allowed(value: Any) -> None:
    if _is_simple_scope(value):
        raise HTTPException(status_code=400, detail="reserved simple-rate scopes must use /simple-rates")


def _assert_generic_rule_allowed(rule: models.InvigilationPaymentRateRule) -> None:
    _assert_generic_scope_allowed(rule.role_scope)


def _has_overlap(
    existing_from: date | None,
    existing_to: date | None,
    new_from: date,
    new_to: date | None,
) -> bool:
    if existing_from is None:
        return True
    return (existing_to is None or existing_to >= new_from) and (new_to is None or existing_from <= new_to)


def _assert_no_active_conflict(db: Session, rule: models.InvigilationPaymentRateRule) -> None:
    if rule.effective_from is None:
        raise HTTPException(status_code=400, detail="effective_from is required before activation")

    active_rules = db.query(models.InvigilationPaymentRateRule).filter(
        models.InvigilationPaymentRateRule.status == models.InvigilationRateRuleStatus.active,
        models.InvigilationPaymentRateRule.payment_unit == rule.payment_unit,
        models.InvigilationPaymentRateRule.role_scope == rule.role_scope,
        models.InvigilationPaymentRateRule.person_type_scope == rule.person_type_scope,
        models.InvigilationPaymentRateRule.id != rule.id,
    ).all()

    for existing in active_rules:
        if _has_overlap(existing.effective_from, existing.effective_to, rule.effective_from, rule.effective_to):
            raise HTTPException(
                status_code=409,
                detail="An overlapping active rate rule already exists for this unit and scope",
            )


def _safety_flags() -> dict[str, bool]:
    return {
        "preview_only": True,
        "payment_authorization_enabled": False,
        "final_export_enabled": False,
    }


def serialize_rate_rule(rule: models.InvigilationPaymentRateRule) -> dict[str, Any]:
    return {
        "rate_rule_id": rule.id,
        "rate_name": rule.rate_name,
        "payment_unit": _enum_value(rule.payment_unit),
        "rate_amount": rule.rate_amount,
        "currency": rule.currency,
        "role_scope": rule.role_scope,
        "person_type_scope": rule.person_type_scope,
        "effective_from": rule.effective_from,
        "effective_to": rule.effective_to,
        "status": _status(rule),
        "created_by": rule.created_by,
        "created_at": rule.created_at,
        "updated_by": rule.updated_by,
        "updated_at": rule.updated_at,
        "activated_by": rule.activated_by,
        "activated_at": rule.activated_at,
        "archived_by": rule.archived_by,
        "archived_at": rule.archived_at,
        "note": rule.note,
        **_safety_flags(),
    }


def list_rate_rules(db: Session) -> dict[str, Any]:
    rules = db.query(models.InvigilationPaymentRateRule).filter(
        ~models.InvigilationPaymentRateRule.role_scope.in_(SIMPLE_RATE_SCOPES)
    ).order_by(
        models.InvigilationPaymentRateRule.id.desc()
    ).all()
    return {"rate_rules": [serialize_rate_rule(rule) for rule in rules], **_safety_flags()}


def create_rate_rule(db: Session, payload: Any, actor_id: int | None = None) -> dict[str, Any]:
    name = _clean_text(getattr(payload, "rate_name", None))
    if not name:
        raise HTTPException(status_code=400, detail="rate_name is required")
    payment_unit = _validate_unit(getattr(payload, "payment_unit", None))
    rate_amount = _amount(getattr(payload, "rate_amount", None))
    effective_from = getattr(payload, "effective_from", None)
    effective_to = getattr(payload, "effective_to", None)
    role_scope = _normalized_scope(getattr(payload, "role_scope", None))
    _assert_generic_scope_allowed(role_scope)
    _validate_dates(effective_from, effective_to)

    rule = models.InvigilationPaymentRateRule(
        rate_name=name,
        payment_unit=payment_unit,
        rate_amount=rate_amount,
        currency=(_clean_text(getattr(payload, "currency", None), "THB") or "THB").upper(),
        role_scope=role_scope,
        person_type_scope=(_clean_text(getattr(payload, "person_type_scope", None), "ALL") or "ALL").upper(),
        effective_from=effective_from,
        effective_to=effective_to,
        status=models.InvigilationRateRuleStatus.draft,
        created_by=actor_id,
        note=_clean_text(getattr(payload, "note", None)),
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return {"rate_rule": serialize_rate_rule(rule), **_safety_flags()}


def get_rate_rule(db: Session, rate_rule_id: int) -> models.InvigilationPaymentRateRule:
    rule = db.query(models.InvigilationPaymentRateRule).filter(
        models.InvigilationPaymentRateRule.id == rate_rule_id
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="rate rule not found")
    return rule


def update_rate_rule(db: Session, rate_rule_id: int, payload: Any, actor_id: int | None = None) -> dict[str, Any]:
    rule = get_rate_rule(db, rate_rule_id)
    _assert_generic_rule_allowed(rule)
    if _status(rule) == ARCHIVED:
        raise HTTPException(status_code=400, detail="archived rate rules cannot be edited")

    data = payload.model_dump(exclude_unset=True) if hasattr(payload, "model_dump") else dict(payload)

    if "rate_name" in data:
        name = _clean_text(data["rate_name"])
        if not name:
            raise HTTPException(status_code=400, detail="rate_name is required")
        rule.rate_name = name
    if "payment_unit" in data:
        rule.payment_unit = _validate_unit(data["payment_unit"])
    if "rate_amount" in data:
        rule.rate_amount = _amount(data["rate_amount"])
    if "currency" in data:
        rule.currency = (_clean_text(data["currency"], "THB") or "THB").upper()
    if "role_scope" in data:
        role_scope = _normalized_scope(data["role_scope"])
        _assert_generic_scope_allowed(role_scope)
        rule.role_scope = role_scope
    if "person_type_scope" in data:
        rule.person_type_scope = (_clean_text(data["person_type_scope"], "ALL") or "ALL").upper()
    if "effective_from" in data:
        rule.effective_from = data["effective_from"]
    if "effective_to" in data:
        rule.effective_to = data["effective_to"]
    if "note" in data:
        rule.note = _clean_text(data["note"])

    _validate_dates(rule.effective_from, rule.effective_to)
    if _status(rule) == ACTIVE:
        _assert_no_active_conflict(db, rule)

    rule.updated_by = actor_id
    rule.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(rule)
    return {"rate_rule": serialize_rate_rule(rule), **_safety_flags()}


def activate_rate_rule(db: Session, rate_rule_id: int, actor_id: int | None = None) -> dict[str, Any]:
    rule = get_rate_rule(db, rate_rule_id)
    _assert_generic_rule_allowed(rule)
    if _status(rule) == ARCHIVED:
        raise HTTPException(status_code=400, detail="archived rate rules cannot be activated")
    _validate_dates(rule.effective_from, rule.effective_to)
    _assert_no_active_conflict(db, rule)
    rule.status = models.InvigilationRateRuleStatus.active
    rule.activated_by = actor_id
    rule.activated_at = datetime.now(timezone.utc)
    rule.updated_by = actor_id
    rule.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(rule)
    return {"rate_rule": serialize_rate_rule(rule), **_safety_flags()}


def archive_rate_rule(db: Session, rate_rule_id: int, actor_id: int | None = None) -> dict[str, Any]:
    rule = get_rate_rule(db, rate_rule_id)
    _assert_generic_rule_allowed(rule)
    rule.status = models.InvigilationRateRuleStatus.archived
    rule.archived_by = actor_id
    rule.archived_at = datetime.now(timezone.utc)
    rule.updated_by = actor_id
    rule.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(rule)
    return {"rate_rule": serialize_rate_rule(rule), **_safety_flags()}


def _serialize_simple_rate(
    day_scope: str,
    rule: models.InvigilationPaymentRateRule | None,
) -> dict[str, Any]:
    return {
        "day_scope": day_scope,
        "amount": rule.rate_amount if rule else None,
        "amount_status": "CONFIGURED" if rule else "PENDING_CONFIGURATION",
        "rate_rule_id": rule.id if rule else None,
        "saved_at": (rule.updated_at or rule.activated_at or rule.created_at) if rule else None,
    }


def get_simple_rates(db: Session) -> dict[str, Any]:
    active_rules = db.query(models.InvigilationPaymentRateRule).filter(
        models.InvigilationPaymentRateRule.role_scope.in_(SIMPLE_RATE_SCOPES),
        models.InvigilationPaymentRateRule.person_type_scope == "ALL",
        models.InvigilationPaymentRateRule.payment_unit == models.InvigilationPaymentUnit.per_session,
        models.InvigilationPaymentRateRule.status == models.InvigilationRateRuleStatus.active,
    ).order_by(models.InvigilationPaymentRateRule.id.desc()).all()

    rules_by_scope: dict[str, models.InvigilationPaymentRateRule] = {}
    for rule in active_rules:
        rules_by_scope.setdefault(rule.role_scope, rule)

    weekday_rule = rules_by_scope.get(SIMPLE_WEEKDAY_SCOPE)
    weekend_rule = rules_by_scope.get(SIMPLE_WEEKEND_SCOPE)
    configured_count = int(weekday_rule is not None) + int(weekend_rule is not None)
    configuration_status = (
        "CONFIGURED" if configured_count == 2
        else "INCOMPLETE" if configured_count == 1
        else "NOT_CONFIGURED"
    )

    return {
        "currency": "THB",
        "payment_unit": "PER_SESSION",
        "configuration_status": configuration_status,
        "weekday_rate": _serialize_simple_rate("WEEKDAY", weekday_rule),
        "weekend_rate": _serialize_simple_rate("WEEKEND", weekend_rule),
        **_safety_flags(),
    }


def save_simple_rates(db: Session, payload: Any, actor_id: int | None = None) -> dict[str, Any]:
    weekday_amount = _amount(getattr(payload, "weekday_amount", None))
    weekend_amount = _amount(getattr(payload, "weekend_amount", None))
    now = datetime.now(timezone.utc)

    with atomic(db) as session:
        previous_rules = session.query(models.InvigilationPaymentRateRule).filter(
            models.InvigilationPaymentRateRule.role_scope.in_(SIMPLE_RATE_SCOPES),
            models.InvigilationPaymentRateRule.status != models.InvigilationRateRuleStatus.archived,
        ).all()
        for rule in previous_rules:
            rule.status = models.InvigilationRateRuleStatus.archived
            rule.archived_by = actor_id
            rule.archived_at = now
            rule.updated_by = actor_id
            rule.updated_at = now

        for scope, amount in (
            (SIMPLE_WEEKDAY_SCOPE, weekday_amount),
            (SIMPLE_WEEKEND_SCOPE, weekend_amount),
        ):
            session.add(models.InvigilationPaymentRateRule(
                rate_name=SIMPLE_RATE_NAMES[scope],
                payment_unit=models.InvigilationPaymentUnit.per_session,
                rate_amount=amount,
                currency="THB",
                role_scope=scope,
                person_type_scope="ALL",
                effective_from=date.today(),
                status=models.InvigilationRateRuleStatus.active,
                created_by=actor_id,
                updated_by=actor_id,
                updated_at=now,
                activated_by=actor_id,
                activated_at=now,
                note="Managed by simple weekday/weekend rate facade. Preview configuration only.",
            ))
        session.flush()

    return get_simple_rates(db)
