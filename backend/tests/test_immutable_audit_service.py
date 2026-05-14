"""Tests for services/immutable_audit_service.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.immutable_audit_service import build_immutable_audit_event


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build(**kwargs) -> dict:
    defaults = {
        "action": "SCHEDULE_PUBLISHED",
        "actor_id": 1,
        "actor_role": "admin",
        "resource_type": "OptimizeSession",
        "resource_id": 42,
    }
    defaults.update(kwargs)
    return build_immutable_audit_event(**defaults)


# ── All required keys ─────────────────────────────────────────────────────────

def test_all_required_keys_present():
    r = _build()
    for key in (
        "audit_event_id", "action", "actor_id", "actor_role",
        "resource_type", "resource_id", "before_hash", "after_hash",
        "before_snapshot", "after_snapshot", "reason", "metadata",
        "timestamp", "immutable", "schema_version",
    ):
        assert key in r, f"Missing key: {key}"


def test_immutable_is_always_true():
    r = _build()
    assert r["immutable"] is True


def test_schema_version_is_1_0():
    r = _build()
    assert r["schema_version"] == "1.0"


# ── Auto-generated fields ─────────────────────────────────────────────────────

def test_audit_event_id_is_nonempty_string():
    r = _build()
    assert isinstance(r["audit_event_id"], str)
    assert len(r["audit_event_id"]) == 36


def test_timestamp_is_utc_iso():
    r = _build()
    assert "T" in r["timestamp"]
    assert "+" in r["timestamp"] or r["timestamp"].endswith("Z")


# ── Hashing ───────────────────────────────────────────────────────────────────

def test_before_hash_present_when_snapshot_provided():
    r = _build(before_snapshot={"status": "APPROVED"})
    assert isinstance(r["before_hash"], str)
    assert len(r["before_hash"]) == 64  # SHA-256 hex


def test_after_hash_present_when_snapshot_provided():
    r = _build(after_snapshot={"status": "PUBLISHED"})
    assert isinstance(r["after_hash"], str)
    assert len(r["after_hash"]) == 64


def test_hashes_are_none_when_no_snapshots():
    r = _build()
    assert r["before_hash"] is None
    assert r["after_hash"] is None


def test_hashes_are_deterministic():
    snap = {"status": "APPROVED", "session_id": 42}
    r1 = _build(before_snapshot=snap)
    r2 = _build(before_snapshot=snap)
    assert r1["before_hash"] == r2["before_hash"]


def test_different_inputs_produce_different_hashes():
    r1 = _build(before_snapshot={"status": "APPROVED"})
    r2 = _build(before_snapshot={"status": "LOCKED"})
    assert r1["before_hash"] != r2["before_hash"]


# ── PII sanitization ──────────────────────────────────────────────────────────

def test_pii_keys_sanitized_in_before_snapshot():
    r = _build(before_snapshot={"email": "alice@example.com", "status": "APPROVED"})
    assert r["before_snapshot"]["email"] == "[REDACTED]"
    assert r["before_snapshot"]["status"] == "APPROVED"


def test_pii_keys_sanitized_in_after_snapshot():
    r = _build(after_snapshot={"token": "abc123", "score": 95})
    assert r["after_snapshot"]["token"] == "[REDACTED]"
    assert r["after_snapshot"]["score"] == 95


def test_input_dict_not_mutated():
    snap = {"email": "test@test.com", "status": "APPROVED"}
    original = dict(snap)
    _build(before_snapshot=snap)
    assert snap == original


# ── resource_id conversion ────────────────────────────────────────────────────

def test_resource_id_int_converted_to_string():
    r = _build(resource_id=99)
    assert r["resource_id"] == "99"


def test_resource_id_none_becomes_unknown():
    r = _build(resource_id=None)
    assert r["resource_id"] == "unknown"


def test_resource_id_string_stays_string():
    r = _build(resource_id="sess-42")
    assert r["resource_id"] == "sess-42"


# ── Optional fields ───────────────────────────────────────────────────────────

def test_metadata_defaults_to_empty_dict():
    r = _build()
    assert r["metadata"] == {}


def test_metadata_passed_through():
    r = _build(metadata={"source": "workflow", "env": "prod"})
    assert r["metadata"]["source"] == "workflow"


def test_reason_defaults_to_none():
    r = _build()
    assert r["reason"] is None


def test_reason_passed_through():
    r = _build(reason="Approved by department head.")
    assert r["reason"] == "Approved by department head."
