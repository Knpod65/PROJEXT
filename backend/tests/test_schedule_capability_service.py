"""Tests for schedule_capability_service.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.schedule_capability_service import compute_schedule_capabilities


# ── Helpers ───────────────────────────────────────────────────────────────────

def _caps(
    *,
    derived="APPROVED",
    governance="AUTO_APPROVED",
    session_status="locked",
    user_role="admin",
    can_publish=True,
    risk_score=20.0,
    hard_fail_count=0,
    blocker_codes=None,
):
    return compute_schedule_capabilities(
        derived_schedule_state=derived,
        governance_state=governance,
        session_status=session_status,
        user_role=user_role,
        can_publish=can_publish,
        risk_score=risk_score,
        hard_fail_count=hard_fail_count,
        blocker_codes=blocker_codes or [],
    )


# ── can_publish ───────────────────────────────────────────────────────────────

def test_admin_approved_clean_can_publish():
    r = _caps(derived="APPROVED", governance="AUTO_APPROVED", can_publish=True)
    assert r["can_publish"] is True


def test_non_admin_cannot_publish():
    for role in ("esq_head", "secretary", "staff", "teacher", "student"):
        r = _caps(user_role=role, derived="APPROVED", can_publish=True)
        assert r["can_publish"] is False


def test_wrong_state_cannot_publish():
    r = _caps(derived="GOVERNANCE_REVIEW", can_publish=True)
    assert r["can_publish"] is False


def test_readiness_false_blocks_publish():
    r = _caps(derived="APPROVED", can_publish=False, hard_fail_count=2, blocker_codes=["HARD_FAILURES_PRESENT"])
    assert r["can_publish"] is False
    assert "resolve_hard_failures" in r["required_actions"]


def test_governance_blocked_blocks_publish():
    r = _caps(derived="APPROVED", governance="BLOCKED", can_publish=False, blocker_codes=["GOVERNANCE_BLOCKED"])
    assert r["can_publish"] is False
    assert "resolve_governance_block" in r["required_actions"]


# ── can_finalize ──────────────────────────────────────────────────────────────

def test_signer_in_confirming_can_finalize():
    for role in ("admin", "esq_head", "secretary"):
        r = _caps(user_role=role, session_status="confirming")
        assert r["can_finalize"] is True, f"Expected can_finalize for {role}"


def test_signer_in_swap_confirming_can_finalize():
    r = _caps(user_role="esq_head", session_status="swap_confirming")
    assert r["can_finalize"] is True


def test_non_signer_cannot_finalize():
    for role in ("dept_supervisor", "staff", "teacher"):
        r = _caps(user_role=role, session_status="confirming")
        assert r["can_finalize"] is False


def test_signer_not_in_signing_state_cannot_finalize():
    r = _caps(user_role="esq_head", session_status="confirmed")
    assert r["can_finalize"] is False


# ── can_rollback ──────────────────────────────────────────────────────────────

def test_admin_can_rollback_from_published():
    r = _caps(derived="PUBLISHED")
    assert r["can_rollback"] is True


def test_non_admin_cannot_rollback():
    r = _caps(user_role="esq_head", derived="PUBLISHED")
    assert r["can_rollback"] is False


def test_cannot_rollback_from_archived():
    r = _caps(derived="ARCHIVED")
    assert r["can_rollback"] is False


def test_cannot_rollback_from_draft():
    r = _caps(derived="DRAFT")
    assert r["can_rollback"] is False


# ── can_edit ─────────────────────────────────────────────────────────────────

def test_admin_can_edit_approved():
    r = _caps(derived="APPROVED")
    assert r["can_edit"] is True


def test_dept_supervisor_can_edit_approved():
    r = _caps(user_role="dept_supervisor", derived="APPROVED")
    assert r["can_edit"] is True


def test_nobody_can_edit_locked():
    for role in ("admin", "esq_head", "dept_supervisor", "teacher"):
        r = _caps(user_role=role, derived="LOCKED")
        assert r["can_edit"] is False


def test_staff_cannot_edit():
    r = _caps(user_role="staff", derived="APPROVED")
    assert r["can_edit"] is False


# ── can_open_swap_window ──────────────────────────────────────────────────────

def test_admin_confirmed_can_open_swap():
    r = _caps(session_status="confirmed")
    assert r["can_open_swap_window"] is True


def test_admin_non_confirmed_cannot_open_swap():
    r = _caps(session_status="draft")
    assert r["can_open_swap_window"] is False


def test_non_admin_cannot_open_swap():
    r = _caps(user_role="esq_head", session_status="confirmed")
    assert r["can_open_swap_window"] is False


# ── can_regenerate ────────────────────────────────────────────────────────────

def test_admin_in_optimized_can_regenerate():
    r = _caps(derived="OPTIMIZED")
    assert r["can_regenerate"] is True


def test_admin_in_approved_cannot_regenerate():
    r = _caps(derived="APPROVED")
    assert r["can_regenerate"] is False


# ── can_archive / can_reopen / can_unpublish ──────────────────────────────────

def test_admin_can_archive_locked():
    r = _caps(derived="LOCKED")
    assert r["can_archive"] is True


def test_admin_can_reopen_locked():
    r = _caps(derived="LOCKED")
    assert r["can_reopen"] is True


def test_admin_can_unpublish_published():
    r = _caps(derived="PUBLISHED")
    assert r["can_unpublish"] is True


# ── return structure ──────────────────────────────────────────────────────────

def test_all_keys_present():
    r = _caps()
    for key in (
        "can_publish", "can_unpublish", "can_archive", "can_reopen",
        "can_rollback", "can_edit", "can_regenerate", "can_open_swap_window",
        "can_finalize", "blocking_reasons", "warnings", "required_actions",
    ):
        assert key in r, f"Missing key: {key}"


def test_blocking_reasons_are_list():
    r = _caps(user_role="staff", derived="APPROVED")
    assert isinstance(r["blocking_reasons"], list)


def test_escalation_warning_emitted():
    r = _caps(governance="ESCALATION_REQUIRED")
    assert any("escalation" in w.lower() for w in r["warnings"])
    assert "complete_escalation_review" in r["required_actions"]
