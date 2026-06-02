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
    activate_rate_rule,
    archive_rate_rule,
    create_rate_rule,
    list_rate_rules,
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

