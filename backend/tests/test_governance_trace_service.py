"""Tests for governance_trace_service.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.governance_trace_service import build_governance_trace


# ── Helpers ───────────────────────────────────────────────────────────────────

def _gov(state="AUTO_APPROVED", priority="LOW"):
    return {
        "governance_state": state,
        "review_priority": priority,
        "approval_reasoning": "Test reasoning.",
    }


def _session(**overrides):
    base = {
        "created_at": "2026-05-01T08:00:00+00:00",
        "updated_at": "2026-05-10T12:00:00+00:00",
        "status": "locked",
        "sig1_at": None, "sig2_at": None, "sig3_at": None, "sig4_at": None,
        "sig1_user_id": None, "sig2_user_id": None, "sig3_user_id": None, "sig4_user_id": None,
        "sig1r2_at": None, "sig2r2_at": None, "sig3r2_at": None, "sig4r2_at": None,
        "sig1r2_user_id": None, "sig2r2_user_id": None, "sig3r2_user_id": None, "sig4r2_user_id": None,
    }
    base.update(overrides)
    return base


# ── Basic structure ───────────────────────────────────────────────────────────

def test_returns_list():
    events = build_governance_trace(session_dict=_session(), governance_decision=_gov())
    assert isinstance(events, list)


def test_each_event_has_required_keys():
    events = build_governance_trace(session_dict=_session(), governance_decision=_gov())
    for e in events:
        for key in ("type", "timestamp", "actor", "details", "severity"):
            assert key in e, f"Missing key '{key}' in event {e}"


def test_session_created_event_present():
    events = build_governance_trace(session_dict=_session(), governance_decision=_gov())
    types = [e["type"] for e in events]
    assert "SESSION_CREATED" in types


def test_governance_decision_event_present():
    events = build_governance_trace(session_dict=_session(), governance_decision=_gov())
    types = [e["type"] for e in events]
    assert "GOVERNANCE_DECISION" in types


# ── Signature events ──────────────────────────────────────────────────────────

def test_round1_signatures_included_when_set():
    s = _session(
        sig1_at="2026-05-02T09:00:00+00:00", sig1_user_id=10,
        sig2_at="2026-05-02T10:00:00+00:00", sig2_user_id=11,
    )
    events = build_governance_trace(session_dict=s, governance_decision=_gov())
    types = [e["type"] for e in events]
    assert "SIG_ROUND1_SIGNER1" in types
    assert "SIG_ROUND1_SIGNER2" in types
    assert "SIG_ROUND1_SIGNER3" not in types  # None was skipped


def test_round2_signatures_included_when_set():
    s = _session(
        sig1r2_at="2026-05-05T09:00:00+00:00", sig1r2_user_id=20,
    )
    events = build_governance_trace(session_dict=s, governance_decision=_gov())
    types = [e["type"] for e in events]
    assert "SIG_ROUND2_SIGNER1" in types
    assert "SIG_ROUND2_SIGNER2" not in types


def test_all_signatures_all_eight():
    s = _session(
        sig1_at="2026-05-02T09:00:00", sig1_user_id=1,
        sig2_at="2026-05-02T10:00:00", sig2_user_id=2,
        sig3_at="2026-05-02T11:00:00", sig3_user_id=3,
        sig4_at="2026-05-02T12:00:00", sig4_user_id=4,
        sig1r2_at="2026-05-08T09:00:00", sig1r2_user_id=5,
        sig2r2_at="2026-05-08T10:00:00", sig2r2_user_id=6,
        sig3r2_at="2026-05-08T11:00:00", sig3r2_user_id=7,
        sig4r2_at="2026-05-08T12:00:00", sig4r2_user_id=8,
    )
    events = build_governance_trace(session_dict=s, governance_decision=_gov())
    types = [e["type"] for e in events]
    for i in range(1, 5):
        assert f"SIG_ROUND1_SIGNER{i}" in types
        assert f"SIG_ROUND2_SIGNER{i}" in types


# ── Hard-fail recheck issues ──────────────────────────────────────────────────

def test_hard_fail_issues_produce_recheck_blocker():
    issues = [
        {"severity": "HARD_FAIL", "code": "ROOM_CONFLICT", "message": "Room double-booked."},
        {"severity": "WARNING", "code": "STAFF_OVERLOAD", "message": "Staff overloaded."},
    ]
    events = build_governance_trace(
        session_dict=_session(),
        governance_decision=_gov(),
        recheck_issues=issues,
    )
    types = [e["type"] for e in events]
    assert "RECHECK_BLOCKER" in types
    # Only HARD_FAIL becomes a RECHECK_BLOCKER (not WARNING)
    blocker_count = types.count("RECHECK_BLOCKER")
    assert blocker_count == 1


def test_no_hard_fails_no_recheck_blocker():
    issues = [{"severity": "WARNING", "code": "X", "message": "minor"}]
    events = build_governance_trace(
        session_dict=_session(),
        governance_decision=_gov(),
        recheck_issues=issues,
    )
    types = [e["type"] for e in events]
    assert "RECHECK_BLOCKER" not in types


# ── Quality snapshot ──────────────────────────────────────────────────────────

def test_quality_snapshot_produces_event():
    events = build_governance_trace(
        session_dict=_session(),
        governance_decision=_gov(),
        quality_snapshot={"overall_score": 82, "quality_band": "GOOD"},
    )
    types = [e["type"] for e in events]
    assert "QUALITY_ASSESSED" in types


def test_no_quality_snapshot_no_event():
    events = build_governance_trace(session_dict=_session(), governance_decision=_gov())
    types = [e["type"] for e in events]
    assert "QUALITY_ASSESSED" not in types


# ── Sorting ───────────────────────────────────────────────────────────────────

def test_events_with_timestamps_sorted_before_none():
    s = _session(sig1_at="2026-05-02T09:00:00+00:00", sig1_user_id=1)
    events = build_governance_trace(session_dict=s, governance_decision=_gov())
    timestamped = [e for e in events if e["timestamp"] is not None]
    null_ts = [e for e in events if e["timestamp"] is None]
    if timestamped and null_ts:
        last_ts_idx = max(events.index(e) for e in timestamped)
        first_null_idx = min(events.index(e) for e in null_ts)
        assert last_ts_idx < first_null_idx


# ── Governance severity ───────────────────────────────────────────────────────

def test_blocked_governance_produces_hard_fail_severity():
    events = build_governance_trace(
        session_dict=_session(),
        governance_decision=_gov(state="BLOCKED"),
    )
    gov_events = [e for e in events if e["type"] == "GOVERNANCE_DECISION"]
    assert gov_events[0]["severity"] == "HARD_FAIL"


def test_auto_approved_governance_produces_info_severity():
    events = build_governance_trace(
        session_dict=_session(),
        governance_decision=_gov(state="AUTO_APPROVED"),
    )
    gov_events = [e for e in events if e["type"] == "GOVERNANCE_DECISION"]
    assert gov_events[0]["severity"] == "INFO"
