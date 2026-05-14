"""Tests for schedule_governance_policy.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from policies.schedule_governance_policy import (
    is_transition_allowed,
    get_transition_blockers,
    get_required_roles,
    requires_governance_review,
    requires_audit_annotation,
)


# ── is_transition_allowed ─────────────────────────────────────────────────────

def test_admin_can_publish():
    assert is_transition_allowed("APPROVED", "PUBLISHED", user_role="admin") is True


def test_non_admin_cannot_publish():
    assert is_transition_allowed("APPROVED", "PUBLISHED", user_role="esq_head") is False


def test_signer_can_move_to_governance_review():
    for role in ("admin", "esq_head", "secretary"):
        assert is_transition_allowed("RECHECKED", "GOVERNANCE_REVIEW", user_role=role) is True


def test_staff_cannot_trigger_any_lifecycle():
    assert is_transition_allowed("APPROVED", "PUBLISHED", user_role="staff") is False
    assert is_transition_allowed("LOCKED", "ARCHIVED", user_role="staff") is False


def test_governance_blocked_prevents_publication():
    assert is_transition_allowed(
        "APPROVED", "PUBLISHED",
        user_role="admin",
        governance_state="BLOCKED",
    ) is False


def test_governance_not_blocked_allows_publication():
    assert is_transition_allowed(
        "APPROVED", "PUBLISHED",
        user_role="admin",
        governance_state="AUTO_APPROVED",
    ) is True


def test_hard_fails_block_rechecked_to_approved():
    assert is_transition_allowed(
        "RECHECKED", "APPROVED",
        user_role="admin",
        hard_fail_count=3,
    ) is False


def test_zero_hard_fails_allows_rechecked_to_approved():
    assert is_transition_allowed(
        "RECHECKED", "APPROVED",
        user_role="admin",
        hard_fail_count=0,
    ) is True


def test_only_admin_can_rollback():
    assert is_transition_allowed("PUBLISHED", "ROLLED_BACK", user_role="admin") is True
    assert is_transition_allowed("PUBLISHED", "ROLLED_BACK", user_role="esq_head") is False


def test_unknown_edge_is_not_allowed():
    assert is_transition_allowed("DRAFT", "PUBLISHED", user_role="admin") is False


# ── get_transition_blockers ───────────────────────────────────────────────────

def test_blockers_empty_for_valid_transition():
    blockers = get_transition_blockers("APPROVED", "PUBLISHED", user_role="admin")
    assert blockers == []


def test_role_insufficient_blocker():
    blockers = get_transition_blockers("APPROVED", "PUBLISHED", user_role="secretary")
    codes = [b["code"] for b in blockers]
    assert "ROLE_INSUFFICIENT" in codes


def test_governance_blocked_blocker():
    blockers = get_transition_blockers(
        "APPROVED", "PUBLISHED", user_role="admin", governance_state="BLOCKED"
    )
    codes = [b["code"] for b in blockers]
    assert "GOVERNANCE_BLOCKED" in codes


def test_hard_fails_blocker():
    blockers = get_transition_blockers(
        "RECHECKED", "APPROVED", user_role="admin", hard_fail_count=2
    )
    codes = [b["code"] for b in blockers]
    assert "HARD_FAILS_PRESENT" in codes


def test_invalid_edge_blocker():
    blockers = get_transition_blockers("DRAFT", "ARCHIVED", user_role="admin")
    codes = [b["code"] for b in blockers]
    assert "INVALID_TRANSITION_EDGE" in codes


def test_all_blockers_have_required_keys():
    blockers = get_transition_blockers("APPROVED", "PUBLISHED", user_role="staff")
    for b in blockers:
        assert "code" in b
        assert "reason" in b
        assert "severity" in b
        assert "can_override" in b


# ── get_required_roles ────────────────────────────────────────────────────────

def test_required_roles_for_publish():
    roles = get_required_roles("APPROVED", "PUBLISHED")
    assert roles == ["admin"]


def test_required_roles_for_governance_review():
    roles = get_required_roles("RECHECKED", "GOVERNANCE_REVIEW")
    assert "admin" in roles
    assert "esq_head" in roles
    assert "secretary" in roles


def test_required_roles_unknown_edge_returns_empty():
    roles = get_required_roles("DRAFT", "PUBLISHED")
    assert roles == []


# ── requires_governance_review ────────────────────────────────────────────────

def test_requires_review_when_escalation_required():
    assert requires_governance_review(
        "RECHECKED", "APPROVED",
        governance_state="ESCALATION_REQUIRED",
        hard_fail_count=0,
    ) is True


def test_requires_review_when_hard_fails():
    assert requires_governance_review(
        "RECHECKED", "APPROVED",
        governance_state="AUTO_APPROVED",
        hard_fail_count=2,
    ) is True


def test_no_review_required_for_clean_state():
    assert requires_governance_review(
        "RECHECKED", "APPROVED",
        governance_state="AUTO_APPROVED",
        hard_fail_count=0,
    ) is False


# ── requires_audit_annotation ────────────────────────────────────────────────

def test_publish_requires_audit():
    assert requires_audit_annotation("APPROVED", "PUBLISHED") is True


def test_archive_requires_audit():
    assert requires_audit_annotation("LOCKED", "ARCHIVED") is True


def test_rollback_requires_audit():
    assert requires_audit_annotation("PUBLISHED", "ROLLED_BACK") is True


def test_optimized_to_rechecked_no_audit():
    assert requires_audit_annotation("OPTIMIZED", "RECHECKED") is False
