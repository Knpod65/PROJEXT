import os
import sys
from datetime import date
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import models
from database import Base
from services.invigilation_rate_rule_service import (
    SIMPLE_WEEKDAY_SCOPE,
    activate_rate_rule,
    archive_rate_rule,
    create_rate_rule,
    get_simple_rates,
    list_rate_rules,
    save_simple_rates,
    update_rate_rule,
)


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def _payload(**overrides):
    data = {
        "rate_name": "ค่าคุมสอบปกติ",
        "payment_unit": "PER_SESSION",
        "rate_amount": "500.00",
        "currency": "THB",
        "role_scope": "ALL",
        "person_type_scope": "ALL",
        "effective_from": date(2026, 6, 1),
        "effective_to": None,
        "note": "Preview configuration only",
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def _assert_safe(payload):
    assert payload["preview_only"] is True
    assert payload["payment_authorization_enabled"] is False
    assert payload["final_export_enabled"] is False


def test_list_empty_rate_rules(db):
    payload = list_rate_rules(db)
    assert payload["rate_rules"] == []
    _assert_safe(payload)


def test_create_draft_per_session_rate(db):
    payload = create_rate_rule(db, _payload(), actor_id=1)
    _assert_safe(payload)
    rule = payload["rate_rule"]
    assert rule["status"] == "DRAFT"
    assert rule["payment_unit"] == "PER_SESSION"
    assert str(rule["rate_amount"]) == "500.00"
    assert rule["preview_only"] is True


def test_reject_missing_rate_name(db):
    with pytest.raises(HTTPException) as exc:
        create_rate_rule(db, _payload(rate_name=" "), actor_id=1)
    assert exc.value.status_code == 400


def test_reject_missing_rate_amount(db):
    with pytest.raises(HTTPException) as exc:
        create_rate_rule(db, _payload(rate_amount=None), actor_id=1)
    assert exc.value.status_code == 400


@pytest.mark.parametrize("amount", ["0", "-1"])
def test_reject_zero_or_negative_rate_amount(db, amount):
    with pytest.raises(HTTPException) as exc:
        create_rate_rule(db, _payload(rate_amount=amount), actor_id=1)
    assert exc.value.status_code == 400


def test_reject_unsupported_payment_unit(db):
    with pytest.raises(HTTPException) as exc:
        create_rate_rule(db, _payload(payment_unit="PER_HOUR"), actor_id=1)
    assert exc.value.status_code == 400


def test_activate_draft_rate(db):
    created = create_rate_rule(db, _payload(), actor_id=1)
    rate_rule_id = created["rate_rule"]["rate_rule_id"]
    activated = activate_rate_rule(db, rate_rule_id, actor_id=1)
    _assert_safe(activated)
    assert activated["rate_rule"]["status"] == "ACTIVE"
    assert activated["rate_rule"]["activated_by"] == 1


def test_activate_requires_effective_from(db):
    created = create_rate_rule(db, _payload(effective_from=None), actor_id=1)
    with pytest.raises(HTTPException) as exc:
        activate_rate_rule(db, created["rate_rule"]["rate_rule_id"], actor_id=1)
    assert exc.value.status_code == 400


def test_reject_conflicting_active_rate_same_scope(db):
    first = create_rate_rule(db, _payload(), actor_id=1)
    activate_rate_rule(db, first["rate_rule"]["rate_rule_id"], actor_id=1)

    second = create_rate_rule(db, _payload(rate_name="ค่าคุมสอบชุดใหม่"), actor_id=1)
    with pytest.raises(HTTPException) as exc:
        activate_rate_rule(db, second["rate_rule"]["rate_rule_id"], actor_id=1)
    assert exc.value.status_code == 409


def test_multiple_draft_rates_can_exist_for_different_scopes(db):
    create_rate_rule(db, _payload(role_scope="CHIEF"), actor_id=1)
    create_rate_rule(db, _payload(role_scope="ASSISTANT"), actor_id=1)
    payload = list_rate_rules(db)
    assert len(payload["rate_rules"]) == 2


def test_archive_active_rate_and_prevent_reactivation_or_edit(db):
    created = create_rate_rule(db, _payload(), actor_id=1)
    rate_rule_id = created["rate_rule"]["rate_rule_id"]
    activate_rate_rule(db, rate_rule_id, actor_id=1)
    archived = archive_rate_rule(db, rate_rule_id, actor_id=1)
    assert archived["rate_rule"]["status"] == "ARCHIVED"

    with pytest.raises(HTTPException) as reactivate_exc:
        activate_rate_rule(db, rate_rule_id, actor_id=1)
    assert reactivate_exc.value.status_code == 400

    with pytest.raises(HTTPException) as update_exc:
        update_rate_rule(db, rate_rule_id, _payload(rate_name="Updated"), actor_id=1)
    assert update_exc.value.status_code == 400


def test_update_active_rule_preserves_conflict_guard(db):
    first = create_rate_rule(db, _payload(role_scope="CHIEF"), actor_id=1)
    activate_rate_rule(db, first["rate_rule"]["rate_rule_id"], actor_id=1)

    second = create_rate_rule(db, _payload(role_scope="ASSISTANT"), actor_id=1)
    activate_rate_rule(db, second["rate_rule"]["rate_rule_id"], actor_id=1)

    with pytest.raises(HTTPException) as exc:
        update_rate_rule(
            db,
            second["rate_rule"]["rate_rule_id"],
            SimpleNamespace(model_dump=lambda exclude_unset=True: {"role_scope": "CHIEF"}),
            actor_id=1,
        )
    assert exc.value.status_code == 409


def test_get_simple_rates_when_not_configured(db):
    payload = get_simple_rates(db)
    _assert_safe(payload)
    assert payload["configuration_status"] == "NOT_CONFIGURED"
    assert payload["currency"] == "THB"
    assert payload["payment_unit"] == "PER_SESSION"
    assert payload["weekday_rate"]["amount"] is None
    assert payload["weekday_rate"]["amount_status"] == "PENDING_CONFIGURATION"
    assert payload["weekend_rate"]["amount"] is None


def test_save_and_get_simple_rates(db):
    payload = save_simple_rates(
        db,
        SimpleNamespace(weekday_amount="300", weekend_amount="500"),
        actor_id=1,
    )
    _assert_safe(payload)
    assert payload["configuration_status"] == "CONFIGURED"
    assert str(payload["weekday_rate"]["amount"]) == "300.00"
    assert str(payload["weekend_rate"]["amount"]) == "500.00"
    assert payload["weekday_rate"]["amount_status"] == "CONFIGURED"
    assert payload["weekend_rate"]["amount_status"] == "CONFIGURED"
    assert "payment_amount" not in payload
    assert "final_payment" not in payload


def test_get_simple_rates_reports_incomplete_configuration(db):
    db.add(models.InvigilationPaymentRateRule(
        rate_name="Internal weekday",
        payment_unit=models.InvigilationPaymentUnit.per_session,
        rate_amount="300",
        currency="THB",
        role_scope=SIMPLE_WEEKDAY_SCOPE,
        person_type_scope="ALL",
        status=models.InvigilationRateRuleStatus.active,
    ))
    db.commit()

    payload = get_simple_rates(db)
    assert payload["configuration_status"] == "INCOMPLETE"
    assert payload["weekday_rate"]["amount_status"] == "CONFIGURED"
    assert payload["weekend_rate"]["amount_status"] == "PENDING_CONFIGURATION"


@pytest.mark.parametrize(
    "weekday_amount,weekend_amount",
    [
        (None, "500"),
        ("300", None),
        ("0", "500"),
        ("300", "0"),
        ("-1", "500"),
        ("300", "-1"),
        ("bad", "500"),
    ],
)
def test_reject_invalid_simple_rate_amounts(db, weekday_amount, weekend_amount):
    with pytest.raises(HTTPException) as exc:
        save_simple_rates(
            db,
            SimpleNamespace(weekday_amount=weekday_amount, weekend_amount=weekend_amount),
            actor_id=1,
        )
    assert exc.value.status_code == 400
    assert get_simple_rates(db)["configuration_status"] == "NOT_CONFIGURED"


def test_simple_rate_replacement_archives_history_and_preserves_legacy_rules(db):
    legacy = create_rate_rule(db, _payload(role_scope="CHIEF"), actor_id=1)
    save_simple_rates(db, SimpleNamespace(weekday_amount="300", weekend_amount="500"), actor_id=1)
    first = get_simple_rates(db)
    first_pair_ids = {
        first["weekday_rate"]["rate_rule_id"],
        first["weekend_rate"]["rate_rule_id"],
    }

    save_simple_rates(db, SimpleNamespace(weekday_amount="350", weekend_amount="550"), actor_id=2)

    archived = db.query(models.InvigilationPaymentRateRule).filter(
        models.InvigilationPaymentRateRule.id.in_(first_pair_ids)
    ).all()
    assert all(rule.status == models.InvigilationRateRuleStatus.archived for rule in archived)
    assert all(rule.archived_by == 2 for rule in archived)
    generic = list_rate_rules(db)
    assert [rule["rate_rule_id"] for rule in generic["rate_rules"]] == [legacy["rate_rule"]["rate_rule_id"]]
    assert str(get_simple_rates(db)["weekday_rate"]["amount"]) == "350.00"


def test_invalid_second_simple_amount_does_not_archive_existing_pair(db):
    save_simple_rates(db, SimpleNamespace(weekday_amount="300", weekend_amount="500"), actor_id=1)
    before = get_simple_rates(db)

    with pytest.raises(HTTPException):
        save_simple_rates(db, SimpleNamespace(weekday_amount="350", weekend_amount="0"), actor_id=2)

    after = get_simple_rates(db)
    assert after["weekday_rate"]["rate_rule_id"] == before["weekday_rate"]["rate_rule_id"]
    assert after["weekend_rate"]["rate_rule_id"] == before["weekend_rate"]["rate_rule_id"]


def test_generic_create_rejects_reserved_simple_scope(db):
    with pytest.raises(HTTPException) as exc:
        create_rate_rule(db, _payload(role_scope=SIMPLE_WEEKDAY_SCOPE), actor_id=1)
    assert exc.value.status_code == 400


@pytest.mark.parametrize("operation", ["update", "activate", "archive"])
def test_generic_mutations_reject_reserved_simple_records(db, operation):
    save_simple_rates(db, SimpleNamespace(weekday_amount="300", weekend_amount="500"), actor_id=1)
    rate_rule_id = get_simple_rates(db)["weekday_rate"]["rate_rule_id"]

    with pytest.raises(HTTPException) as exc:
        if operation == "update":
            update_rate_rule(db, rate_rule_id, _payload(rate_amount="400"), actor_id=1)
        elif operation == "activate":
            activate_rate_rule(db, rate_rule_id, actor_id=1)
        else:
            archive_rate_rule(db, rate_rule_id, actor_id=1)
    assert exc.value.status_code == 400
