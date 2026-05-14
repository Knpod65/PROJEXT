"""Tests for events/event_envelope.py"""
import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from events.event_envelope import (
    EventEnvelope,
    create_event_envelope,
    event_envelope_to_dict,
    sanitize_event_payload,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _envelope(**kwargs) -> EventEnvelope:
    defaults = {"event_type": "TEST_EVENT", "domain": "test"}
    defaults.update(kwargs)
    return create_event_envelope(**defaults)


# ── All required keys in dict ─────────────────────────────────────────────────

def test_all_keys_present_in_dict():
    d = event_envelope_to_dict(_envelope())
    for key in (
        "event_id", "event_type", "domain", "severity", "actor_id",
        "actor_role", "session_id", "correlation_id", "causation_id",
        "aggregate_type", "aggregate_id", "timestamp", "payload",
        "metadata", "pdpa_classification", "contains_pii",
        "retention_hint", "schema_version",
    ):
        assert key in d, f"Missing key: {key}"


# ── Auto-generated fields ─────────────────────────────────────────────────────

def test_event_id_is_auto_generated():
    e = _envelope()
    assert isinstance(e.event_id, str)
    assert len(e.event_id) == 36  # UUID4 canonical form


def test_two_envelopes_have_distinct_event_ids():
    e1 = _envelope()
    e2 = _envelope()
    assert e1.event_id != e2.event_id


def test_timestamp_is_utc_iso_string():
    e = _envelope()
    assert isinstance(e.timestamp, str)
    assert "T" in e.timestamp
    assert "+" in e.timestamp or e.timestamp.endswith("Z") or "+00:00" in e.timestamp


# ── Default values ────────────────────────────────────────────────────────────

def test_schema_version_defaults_to_1_0():
    e = _envelope()
    assert e.schema_version == "1.0"


def test_contains_pii_defaults_to_false():
    e = _envelope()
    assert e.contains_pii is False


def test_pdpa_classification_defaults_to_internal():
    e = _envelope()
    assert e.pdpa_classification == "internal"


def test_severity_defaults_to_info():
    e = _envelope()
    assert e.severity == "INFO"


def test_payload_defaults_to_empty_dict():
    e = _envelope()
    assert e.payload == {}


def test_metadata_defaults_to_empty_dict():
    e = _envelope()
    assert e.metadata == {}


# ── Frozen / immutability ─────────────────────────────────────────────────────

def test_envelope_is_frozen():
    e = _envelope()
    with pytest.raises((AttributeError, TypeError)):
        e.event_type = "MUTATED"  # type: ignore[misc]


# ── event_envelope_to_dict ────────────────────────────────────────────────────

def test_dict_is_json_serializable():
    e = _envelope(payload={"section_id": 42}, metadata={"source": "test"})
    d = event_envelope_to_dict(e)
    json.dumps(d)  # must not raise


def test_dict_values_match_envelope_fields():
    e = _envelope(
        event_type="SCHEDULE_PUBLISHED",
        domain="governance",
        actor_id=7,
        actor_role="admin",
        severity="WARNING",
    )
    d = event_envelope_to_dict(e)
    assert d["event_type"] == "SCHEDULE_PUBLISHED"
    assert d["domain"] == "governance"
    assert d["actor_id"] == 7
    assert d["actor_role"] == "admin"
    assert d["severity"] == "WARNING"


# ── sanitize_event_payload ────────────────────────────────────────────────────

def test_sanitize_redacts_pii_keys():
    payload = {"student_name": "Alice", "section_id": 42}
    result = sanitize_event_payload(payload)
    assert result["student_name"] == "[REDACTED]"
    assert result["section_id"] == 42


def test_sanitize_does_not_mutate_input():
    payload = {"email": "alice@example.com", "score": 95}
    original = dict(payload)
    sanitize_event_payload(payload)
    assert payload == original


def test_sanitize_non_pii_keys_unchanged():
    payload = {"course_id": "POL101", "room_id": 5}
    result = sanitize_event_payload(payload)
    assert result == payload


def test_sanitize_redacts_token():
    result = sanitize_event_payload({"token": "abc123"})
    assert result["token"] == "[REDACTED]"


def test_sanitize_empty_payload_returns_empty():
    assert sanitize_event_payload({}) == {}


def test_sanitize_case_insensitive_key_matching():
    result = sanitize_event_payload({"EMAIL": "test@test.com"})
    # EMAIL uppercased — check if lowercase match works
    # Our impl does key.lower() in _PII_KEYS, so "EMAIL".lower() == "email" → match
    assert result["EMAIL"] == "[REDACTED]"


# ── Payload passes through sanitizer in factory ───────────────────────────────

def test_factory_sanitizes_pii_in_payload():
    e = create_event_envelope(
        "TEST", "test",
        payload={"student_id": "630110001", "section_id": 42},
    )
    assert e.payload["student_id"] == "[REDACTED]"
    assert e.payload["section_id"] == 42


def test_factory_sanitizes_pii_in_metadata():
    e = create_event_envelope(
        "TEST", "test",
        metadata={"token": "secret123", "action": "view"},
    )
    assert e.metadata["token"] == "[REDACTED]"
    assert e.metadata["action"] == "view"


# ── Optional fields ───────────────────────────────────────────────────────────

def test_optional_fields_can_be_set():
    e = create_event_envelope(
        "SCHEDULE_LOCKED",
        "governance",
        causation_id="cause-uuid",
        aggregate_type="OptimizeSession",
        aggregate_id="42",
        retention_hint="7y",
        pdpa_classification="confidential",
        contains_pii=True,
    )
    assert e.causation_id == "cause-uuid"
    assert e.aggregate_type == "OptimizeSession"
    assert e.aggregate_id == "42"
    assert e.retention_hint == "7y"
    assert e.pdpa_classification == "confidential"
    assert e.contains_pii is True
