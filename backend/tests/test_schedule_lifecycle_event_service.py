"""Tests for schedule_lifecycle_event_service.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.schedule_lifecycle_event_service import (
    build_publication_event,
    build_rollback_event,
    build_archive_event,
    build_reopen_event,
    build_governance_override_event,
)

_REQUIRED_KEYS = {"event_type", "actor_id", "session_id", "derived_schedule_state",
                  "governance_state", "timestamp", "reason", "risk_snapshot", "quality_snapshot"}


# ── build_publication_event ───────────────────────────────────────────────────

def test_publication_event_type():
    e = build_publication_event(
        actor_id=1, session_id=5,
        derived_schedule_state="APPROVED",
        governance_state="AUTO_APPROVED",
        risk_score=20.0,
    )
    assert e["event_type"] == "SCHEDULE_PUBLISHED"


def test_publication_event_has_required_keys():
    e = build_publication_event(
        actor_id=1, session_id=5,
        derived_schedule_state="APPROVED",
        governance_state="AUTO_APPROVED",
        risk_score=20.0,
    )
    assert _REQUIRED_KEYS.issubset(e.keys())


def test_publication_event_risk_snapshot():
    e = build_publication_event(
        actor_id=1, session_id=5,
        derived_schedule_state="APPROVED",
        governance_state="AUTO_APPROVED",
        risk_score=35.5,
    )
    assert e["risk_snapshot"]["risk_score"] == 35.5


def test_publication_event_timestamp_is_iso():
    e = build_publication_event(
        actor_id=None, session_id=None,
        derived_schedule_state="APPROVED",
        governance_state="",
        risk_score=50.0,
    )
    assert "T" in e["timestamp"]


# ── build_rollback_event ──────────────────────────────────────────────────────

def test_rollback_event_type():
    e = build_rollback_event(
        actor_id=2, session_id=3,
        derived_schedule_state="PUBLISHED",
        reason="critical error discovered",
    )
    assert e["event_type"] == "SCHEDULE_ROLLED_BACK"


def test_rollback_event_requires_reason():
    with pytest.raises(ValueError, match="non-empty reason"):
        build_rollback_event(
            actor_id=1, session_id=1,
            derived_schedule_state="PUBLISHED",
            reason="",
        )


def test_rollback_event_strips_whitespace():
    e = build_rollback_event(
        actor_id=1, session_id=1,
        derived_schedule_state="PUBLISHED",
        reason="  trimmed reason  ",
    )
    assert e["reason"] == "trimmed reason"


# ── build_archive_event ───────────────────────────────────────────────────────

def test_archive_event_type():
    e = build_archive_event(actor_id=1, session_id=7, derived_schedule_state="LOCKED")
    assert e["event_type"] == "SCHEDULE_ARCHIVED"
    assert e["derived_schedule_state"] == "LOCKED"


# ── build_reopen_event ────────────────────────────────────────────────────────

def test_reopen_event_type():
    e = build_reopen_event(
        actor_id=1, session_id=2,
        derived_schedule_state="LOCKED",
        reason="correction required",
    )
    assert e["event_type"] == "SCHEDULE_REOPENED"


def test_reopen_event_requires_reason():
    with pytest.raises(ValueError, match="non-empty reason"):
        build_reopen_event(
            actor_id=1, session_id=1,
            derived_schedule_state="LOCKED",
            reason="  ",
        )


# ── build_governance_override_event ──────────────────────────────────────────

def test_override_event_type():
    e = build_governance_override_event(
        actor_id=1, session_id=3,
        blockers_overridden=["GOVERNANCE_BLOCKED"],
        reason="board directive",
        governance_state="BLOCKED",
    )
    assert e["event_type"] == "GOVERNANCE_OVERRIDE_APPLIED"
    assert e["blockers_overridden"] == ["GOVERNANCE_BLOCKED"]


def test_override_event_requires_reason():
    with pytest.raises(ValueError, match="non-empty reason"):
        build_governance_override_event(
            actor_id=1, session_id=1,
            blockers_overridden=["GOVERNANCE_BLOCKED"],
            reason="",
            governance_state="BLOCKED",
        )


def test_override_event_requires_blockers():
    with pytest.raises(ValueError, match="at least one blocker"):
        build_governance_override_event(
            actor_id=1, session_id=1,
            blockers_overridden=[],
            reason="valid reason",
            governance_state="BLOCKED",
        )
