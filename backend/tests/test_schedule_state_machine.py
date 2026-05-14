"""Tests for schedule_state_machine.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.schedule_state_machine import (
    ScheduleState,
    ScheduleStateMachine,
    ScheduleTransitionError,
    ScheduleTransitionResult,
    schedule_state_machine,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sm() -> ScheduleStateMachine:
    return ScheduleStateMachine()


def _do(from_s, to_s, **kwargs):
    return _sm().transition(from_s, to_s, actor_id=kwargs.pop("actor_id", 1), **kwargs)


# ── can_transition ─────────────────────────────────────────────────────────────

def test_can_transition_valid_edge():
    sm = _sm()
    assert sm.can_transition("DRAFT", "OPTIMIZED") is True


def test_can_transition_invalid_edge():
    sm = _sm()
    assert sm.can_transition("DRAFT", "PUBLISHED") is False


def test_can_transition_unknown_state():
    sm = _sm()
    assert sm.can_transition("NONEXISTENT", "DRAFT") is False


# ── valid_next_states ─────────────────────────────────────────────────────────

def test_valid_next_states_draft():
    sm = _sm()
    assert sm.valid_next_states("DRAFT") == ["OPTIMIZED"]


def test_valid_next_states_archived_is_empty():
    sm = _sm()
    assert sm.valid_next_states("ARCHIVED") == []


def test_valid_next_states_unknown_returns_empty():
    sm = _sm()
    assert sm.valid_next_states("GARBAGE") == []


# ── is_terminal ───────────────────────────────────────────────────────────────

def test_archived_is_terminal():
    assert _sm().is_terminal("ARCHIVED") is True


def test_draft_not_terminal():
    assert _sm().is_terminal("DRAFT") is False


def test_locked_not_terminal():
    assert _sm().is_terminal("LOCKED") is False


def test_unknown_state_not_terminal():
    assert _sm().is_terminal("INVALID") is False


# ── valid transitions ─────────────────────────────────────────────────────────

def test_draft_to_optimized():
    r = _do("DRAFT", "OPTIMIZED")
    assert r.success is True
    assert r.to_state == "OPTIMIZED"


def test_optimized_to_rechecked():
    r = _do("OPTIMIZED", "RECHECKED")
    assert r.success is True


def test_rechecked_to_governance_review():
    r = _do("RECHECKED", "GOVERNANCE_REVIEW")
    assert r.success is True


def test_rechecked_to_approved_no_hard_fails():
    r = _do("RECHECKED", "APPROVED", hard_fail_count=0)
    assert r.success is True


def test_governance_review_to_approved():
    r = _do("GOVERNANCE_REVIEW", "APPROVED")
    assert r.success is True


def test_approved_to_published_clean_governance():
    r = _do("APPROVED", "PUBLISHED", governance_state="AUTO_APPROVED")
    assert r.success is True


def test_published_to_locked():
    r = _do("PUBLISHED", "LOCKED")
    assert r.success is True


def test_locked_to_archived_with_actor():
    r = _do("LOCKED", "ARCHIVED", actor_id=42)
    assert r.success is True


def test_rolled_back_to_draft():
    r = _do("ROLLED_BACK", "DRAFT", reason="reset after review")
    assert r.success is True


def test_optimized_reset_to_draft():
    r = _do("OPTIMIZED", "DRAFT")
    assert r.success is True


# ── rollback path ─────────────────────────────────────────────────────────────

def test_any_to_rolled_back_with_reason():
    r = _do("PUBLISHED", "ROLLED_BACK", reason="critical error found")
    assert r.success is True
    assert r.reason == "critical error found"


def test_rollback_without_reason_raises():
    with pytest.raises(ScheduleTransitionError, match="rollback_reason"):
        _do("APPROVED", "ROLLED_BACK", reason=None)


def test_rollback_with_empty_reason_raises():
    with pytest.raises(ScheduleTransitionError, match="rollback_reason"):
        _do("PUBLISHED", "ROLLED_BACK", reason="  ")


# ── guard: hard fails block RECHECKED → APPROVED ─────────────────────────────

def test_rechecked_to_approved_blocked_with_hard_fails():
    with pytest.raises(ScheduleTransitionError, match="hard fail"):
        _do("RECHECKED", "APPROVED", hard_fail_count=2)


def test_rechecked_to_approved_allowed_zero_hard_fails():
    r = _do("RECHECKED", "APPROVED", hard_fail_count=0)
    assert r.success is True


# ── guard: BLOCKED governance blocks APPROVED → PUBLISHED ────────────────────

def test_approved_to_published_blocked_when_blocked_governance():
    with pytest.raises(ScheduleTransitionError, match="BLOCKED"):
        _do("APPROVED", "PUBLISHED", governance_state="BLOCKED")


def test_approved_to_published_allowed_when_not_blocked():
    r = _do("APPROVED", "PUBLISHED", governance_state="APPROVAL_REQUIRED")
    assert r.success is True


# ── guard: LOCKED → ARCHIVED requires actor ───────────────────────────────────

def test_locked_to_archived_requires_actor():
    with pytest.raises(ScheduleTransitionError, match="actor_id"):
        _sm().transition("LOCKED", "ARCHIVED", actor_id=None)


# ── invalid transitions ───────────────────────────────────────────────────────

def test_invalid_transition_raises():
    with pytest.raises(ScheduleTransitionError, match="Invalid transition"):
        _do("DRAFT", "PUBLISHED")


def test_archived_has_no_exits():
    with pytest.raises(ScheduleTransitionError):
        _do("ARCHIVED", "DRAFT")


def test_unknown_from_state_raises():
    with pytest.raises(ScheduleTransitionError, match="Unknown from_state"):
        _do("GARBAGE", "DRAFT")


def test_unknown_to_state_raises():
    with pytest.raises(ScheduleTransitionError, match="Unknown to_state"):
        _do("DRAFT", "GARBAGE")


# ── result structure ──────────────────────────────────────────────────────────

def test_result_is_frozen():
    r = _do("DRAFT", "OPTIMIZED")
    with pytest.raises(Exception):
        r.success = False  # type: ignore


def test_audit_metadata_always_populated():
    r = _do("DRAFT", "OPTIMIZED", actor_id=5)
    assert isinstance(r.audit_metadata, dict)
    assert r.audit_metadata["from_state"] == "DRAFT"
    assert r.audit_metadata["to_state"] == "OPTIMIZED"
    assert r.audit_metadata["actor_id"] == 5


def test_timestamp_is_iso():
    r = _do("DRAFT", "OPTIMIZED")
    assert "T" in r.timestamp  # ISO 8601


# ── module singleton ──────────────────────────────────────────────────────────

def test_module_singleton_works():
    r = schedule_state_machine.transition("DRAFT", "OPTIMIZED", actor_id=1)
    assert r.success is True


# ── all 9 states have ScheduleState enum values ───────────────────────────────

def test_all_nine_states_defined():
    states = {s.value for s in ScheduleState}
    expected = {
        "DRAFT", "OPTIMIZED", "RECHECKED", "GOVERNANCE_REVIEW",
        "APPROVED", "PUBLISHED", "LOCKED", "ARCHIVED", "ROLLED_BACK",
    }
    assert states == expected
