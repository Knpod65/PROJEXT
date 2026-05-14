"""Tests for services/transaction_event_bridge_service.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from events.event_envelope import EventEnvelope
from services.event_outbox_service import clear_staged_events, list_staged_events
from services.transaction_event_bridge_service import (
    build_transaction_event_bundle,
    stage_transaction_events,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _bundle(**kwargs):
    defaults = {
        "event_type":    "SCHEDULE_PUBLISHED",
        "domain":        "governance",
        "audit_action":  "SCHEDULE_PUBLISHED",
        "resource_type": "OptimizeSession",
    }
    defaults.update(kwargs)
    return build_transaction_event_bundle(**defaults)


def setup_function():
    clear_staged_events()


# ── Bundle structure ──────────────────────────────────────────────────────────

def test_bundle_has_all_three_keys():
    b = _bundle()
    assert "mutation_event" in b
    assert "audit_event" in b
    assert "outbox_record" in b


def test_mutation_event_is_event_envelope():
    b = _bundle()
    assert isinstance(b["mutation_event"], EventEnvelope)


def test_audit_event_has_immutable_true():
    b = _bundle()
    assert b["audit_event"]["immutable"] is True


def test_outbox_record_has_status_staged():
    b = _bundle()
    assert b["outbox_record"]["status"] == "STAGED"


def test_outbox_record_event_id_matches_mutation_event():
    b = _bundle()
    assert b["outbox_record"]["event_id"] == b["mutation_event"].event_id


# ── Correlation ID shared ─────────────────────────────────────────────────────

def test_correlation_id_propagated_to_mutation_event():
    b = _bundle(correlation_id="corr-abc")
    assert b["mutation_event"].correlation_id == "corr-abc"


def test_actor_id_propagated_to_both():
    b = _bundle(actor_id=7, actor_role="admin")
    assert b["mutation_event"].actor_id == 7
    assert b["audit_event"]["actor_id"] == 7


# ── stage_transaction_events ──────────────────────────────────────────────────

def test_stage_transaction_events_adds_to_outbox():
    b = _bundle()
    stage_transaction_events(b)
    staged = list_staged_events()
    assert len(staged) == 1


def test_stage_transaction_events_returns_outbox_record():
    b = _bundle()
    result = stage_transaction_events(b)
    assert "event_id" in result
    assert result["status"] == "STAGED"


# ── Snapshots and reason ──────────────────────────────────────────────────────

def test_snapshots_passed_to_audit_event():
    b = _bundle(
        before_snapshot={"status": "APPROVED"},
        after_snapshot={"status": "PUBLISHED"},
        reason="Manual override.",
    )
    assert b["audit_event"]["before_snapshot"] == {"status": "APPROVED"}
    assert b["audit_event"]["after_snapshot"] == {"status": "PUBLISHED"}
    assert b["audit_event"]["reason"] == "Manual override."


# ── Empty payloads ────────────────────────────────────────────────────────────

def test_empty_payloads_do_not_raise():
    b = build_transaction_event_bundle(
        event_type="TEST_EVENT",
        domain="test",
        audit_action="TEST_ACTION",
        resource_type="TestResource",
    )
    assert b["mutation_event"].payload == {}
