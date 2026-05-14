"""Tests for services/event_outbox_service.py"""
import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from events.event_envelope import create_event_envelope
from services.event_outbox_service import (
    STATUS_DISPATCHED,
    STATUS_STAGED,
    build_outbox_record,
    clear_staged_events,
    get_staged_event,
    list_staged_events,
    mark_event_dispatched,
    stage_event,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _env(**kwargs):
    defaults = {"event_type": "SCHEDULE_PUBLISHED", "domain": "governance"}
    defaults.update(kwargs)
    return create_event_envelope(**defaults)


def setup_function():
    """Clear outbox before each test."""
    clear_staged_events()


# ── build_outbox_record ───────────────────────────────────────────────────────

def test_build_outbox_record_has_all_keys():
    record = build_outbox_record(_env())
    for key in (
        "event_id", "event_type", "domain", "aggregate_type",
        "aggregate_id", "payload_json", "metadata_json",
        "status", "created_at", "dispatched_at",
    ):
        assert key in record, f"Missing key: {key}"


def test_build_outbox_record_status_is_staged():
    record = build_outbox_record(_env())
    assert record["status"] == STATUS_STAGED


def test_build_outbox_record_payload_json_is_valid():
    e = _env(payload={"section_id": 42, "course": "POL101"})
    record = build_outbox_record(e)
    parsed = json.loads(record["payload_json"])
    assert parsed["section_id"] == 42


def test_build_outbox_record_dispatched_at_is_none():
    record = build_outbox_record(_env())
    assert record["dispatched_at"] is None


def test_build_outbox_record_non_serializable_payload_raises():
    e = create_event_envelope("TEST", "test")
    # Monkey-patch a non-serializable value into payload via object.__setattr__ bypass
    # We can't mutate frozen dataclass directly, so test via a dict
    from events.event_envelope import EventEnvelope
    bad_env = EventEnvelope(
        event_id="bad-id",
        event_type="TEST",
        domain="test",
        severity="INFO",
        actor_id=None,
        actor_role=None,
        session_id=None,
        correlation_id=None,
        causation_id=None,
        aggregate_type=None,
        aggregate_id=None,
        timestamp="2026-01-01T00:00:00+00:00",
        payload={"obj": object()},  # not JSON-serializable
        metadata={},
        pdpa_classification="internal",
        contains_pii=False,
        retention_hint=None,
        schema_version="1.0",
    )
    with pytest.raises(ValueError, match="JSON-serializable"):
        build_outbox_record(bad_env)


# ── stage_event ───────────────────────────────────────────────────────────────

def test_stage_event_adds_to_list():
    stage_event(_env())
    assert len(list_staged_events()) == 1


def test_stage_event_returns_record():
    record = stage_event(_env())
    assert "event_id" in record
    assert record["status"] == STATUS_STAGED


def test_two_staged_events_appear_separately():
    stage_event(_env(event_type="EVT_A"))
    stage_event(_env(event_type="EVT_B"))
    staged = list_staged_events()
    assert len(staged) == 2
    types = {r["event_type"] for r in staged}
    assert "EVT_A" in types
    assert "EVT_B" in types


# ── list_staged_events (copy isolation) ───────────────────────────────────────

def test_list_staged_events_returns_copy():
    stage_event(_env())
    result = list_staged_events()
    result.clear()
    assert len(list_staged_events()) == 1  # internal list unaffected


# ── clear_staged_events ───────────────────────────────────────────────────────

def test_clear_staged_events_empties_list():
    stage_event(_env())
    stage_event(_env())
    clear_staged_events()
    assert list_staged_events() == []


# ── mark_event_dispatched ─────────────────────────────────────────────────────

def test_mark_event_dispatched_returns_true_for_known_id():
    e = _env()
    stage_event(e)
    result = mark_event_dispatched(e.event_id)
    assert result is True


def test_mark_event_dispatched_updates_status():
    e = _env()
    stage_event(e)
    mark_event_dispatched(e.event_id)
    record = get_staged_event(e.event_id)
    assert record["status"] == STATUS_DISPATCHED


def test_mark_event_dispatched_sets_dispatched_at():
    e = _env()
    stage_event(e)
    mark_event_dispatched(e.event_id)
    record = get_staged_event(e.event_id)
    assert record["dispatched_at"] is not None


def test_mark_event_dispatched_returns_false_for_unknown_id():
    result = mark_event_dispatched("nonexistent-id")
    assert result is False


# ── get_staged_event ──────────────────────────────────────────────────────────

def test_get_staged_event_returns_none_for_unknown():
    assert get_staged_event("does-not-exist") is None


def test_get_staged_event_returns_record_for_known():
    e = _env()
    stage_event(e)
    record = get_staged_event(e.event_id)
    assert record is not None
    assert record["event_id"] == e.event_id
