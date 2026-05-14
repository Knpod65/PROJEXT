"""Tests for schedule_transition_service.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.schedule_transition_service import attempt_transition


# ── Helpers ───────────────────────────────────────────────────────────────────

def _attempt(from_s, to_s, *, role="admin", gov="AUTO_APPROVED", fails=0, reason=None, actor_id=1):
    return attempt_transition(
        from_state=from_s,
        to_state=to_s,
        user_role=role,
        governance_state=gov,
        hard_fail_count=fails,
        reason=reason,
        actor_id=actor_id,
    )


# ── Allowed paths ─────────────────────────────────────────────────────────────

def test_admin_approved_to_published_clean():
    r = _attempt("APPROVED", "PUBLISHED")
    assert r["allowed"] is True
    assert r["state_machine_result"] is not None


def test_admin_optimized_to_rechecked():
    r = _attempt("OPTIMIZED", "RECHECKED")
    assert r["allowed"] is True


def test_admin_rechecked_to_approved_no_fails():
    r = _attempt("RECHECKED", "APPROVED", fails=0)
    assert r["allowed"] is True


def test_transition_type_publication():
    r = _attempt("APPROVED", "PUBLISHED")
    assert r["transition_type"] == "publication"


def test_transition_type_rollback():
    r = _attempt("PUBLISHED", "ROLLED_BACK", reason="error found")
    assert r["transition_type"] == "rollback"


def test_transition_type_archival():
    r = _attempt("LOCKED", "ARCHIVED", actor_id=1)
    assert r["transition_type"] == "archival"


def test_audit_required_for_publication():
    r = _attempt("APPROVED", "PUBLISHED")
    assert r["audit_required"] is True


def test_audit_not_required_for_recheck():
    r = _attempt("OPTIMIZED", "RECHECKED")
    assert r["audit_required"] is False


# ── Role-blocked paths ────────────────────────────────────────────────────────

def test_esq_head_cannot_publish():
    r = _attempt("APPROVED", "PUBLISHED", role="esq_head")
    assert r["allowed"] is False
    codes = [b["code"] for b in r["blockers"]]
    assert "ROLE_INSUFFICIENT" in codes


def test_staff_cannot_trigger_any_transition():
    r = _attempt("OPTIMIZED", "RECHECKED", role="staff")
    assert r["allowed"] is False


# ── Governance-blocked paths ──────────────────────────────────────────────────

def test_blocked_governance_prevents_publication():
    r = _attempt("APPROVED", "PUBLISHED", gov="BLOCKED")
    assert r["allowed"] is False
    codes = [b["code"] for b in r["blockers"]]
    assert "GOVERNANCE_BLOCKED" in codes


def test_non_blocked_governance_allows_publication():
    r = _attempt("APPROVED", "PUBLISHED", gov="APPROVAL_REQUIRED")
    assert r["allowed"] is True


# ── Hard-fail blocked paths ───────────────────────────────────────────────────

def test_hard_fails_block_rechecked_to_approved():
    r = _attempt("RECHECKED", "APPROVED", fails=2)
    assert r["allowed"] is False
    codes = [b["code"] for b in r["blockers"]]
    assert "HARD_FAILS_PRESENT" in codes


# ── State machine guard triggered ────────────────────────────────────────────

def test_rollback_without_reason_blocked_by_state_machine():
    r = _attempt("PUBLISHED", "ROLLED_BACK", reason=None)
    assert r["allowed"] is False
    codes = [b["code"] for b in r["blockers"]]
    assert "STATE_MACHINE_GUARD" in codes


def test_rollback_with_reason_allowed():
    r = _attempt("PUBLISHED", "ROLLED_BACK", reason="critical error")
    assert r["allowed"] is True


# ── Invalid edge ──────────────────────────────────────────────────────────────

def test_invalid_edge_is_not_allowed():
    r = _attempt("DRAFT", "PUBLISHED", role="admin")
    assert r["allowed"] is False
    codes = [b["code"] for b in r["blockers"]]
    assert "INVALID_TRANSITION_EDGE" in codes


# ── Return structure ──────────────────────────────────────────────────────────

def test_all_keys_present_on_allowed():
    r = _attempt("APPROVED", "PUBLISHED")
    for key in ("allowed", "target_state", "transition_type", "blockers", "warnings",
                "required_actions", "audit_required", "requires_emergency_override",
                "state_machine_result"):
        assert key in r


def test_all_keys_present_on_blocked():
    r = _attempt("APPROVED", "PUBLISHED", role="staff")
    for key in ("allowed", "target_state", "transition_type", "blockers", "warnings",
                "required_actions", "audit_required", "requires_emergency_override",
                "state_machine_result"):
        assert key in r


def test_blockers_is_list():
    r = _attempt("APPROVED", "PUBLISHED", role="staff")
    assert isinstance(r["blockers"], list)
