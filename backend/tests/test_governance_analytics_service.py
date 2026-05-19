"""Tests for governance_analytics_service.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.governance_analytics_service import (
    compute_governance_analytics,
    _empty_result,
)


# ── Empty inputs ──────────────────────────────────────────────────────────────

def test_empty_inputs_all_zeroed():
    r = compute_governance_analytics([], [])
    assert r["governance_health_score"] == 0.0
    assert r["blocker_count"] == 0
    assert r["escalation_rate"] == 0.0
    assert r["manual_review_rate"] == 0.0
    assert r["top_governance_risks"] == []


def test_empty_report_period_info_defaults_to_empty():
    r = compute_governance_analytics([], [])
    assert r["period_info"] == {}


def test_empty_report_requires_no_structure_errors():
    r = compute_governance_analytics([], [])
    required = {
        "governance_health_score", "average_approval_cycle_hours",
        "blocker_count", "override_count", "rollback_count",
        "escalation_rate", "manual_review_rate", "publication_success_rate",
        "top_governance_risks", "period_info",
    }
    missing = required - r.keys()
    assert not missing


# ── All auto-approved ─────────────────────────────────────────────────────────

def test_all_auto_approved_health_score_max():
    decisions = [
        {"governance_state": "AUTO_APPROVED"} for _ in range(5)
    ]
    r = compute_governance_analytics(decisions, [])
    assert r["governance_health_score"] == 100.0
    assert r["blocker_count"] == 0
    assert r["escalation_rate"] == 0.0


# ── Half blocked ──────────────────────────────────────────────────────────────

def test_half_blocked_correct_blocker_count():
    decisions = (
        [{"governance_state": "BLOCKED"}] * 3
        + [{"governance_state": "AUTO_APPROVED"}] * 3
    )
    r = compute_governance_analytics(decisions, [])
    assert r["blocker_count"] == 3
    assert r["governance_health_score"] == 50.0


# ── Override, rollback counts ─────────────────────────────────────────────────

def test_override_count_incremented():
    decisions = [
        {"governance_state": "AUTO_APPROVED",
         "override_recommendation": "override_approved"},
    ]
    r = compute_governance_analytics(decisions, [])
    assert r["override_count"] == 1
    assert r["blocker_count"] == 0


def test_rollback_count_incremented():
    decisions = [
        {"governance_state": "ROLLBACK_REQUIRED"},
    ]
    r = compute_governance_analytics(decisions, [])
    assert r["rollback_count"] == 1


# ── Manual review rate ────────────────────────────────────────────────────────

_MANUAL_ACTIONS = frozenset({"sensitive_data_access", "admin_override", "rollback"})


def test_manual_review_rate_manual_actions_present():
    decisions = [{"governance_state": "AUTO_APPROVED"}]
    audit = [
        {"action": "sensitive_data_access", "http_status": 200},
        {"action": "normal_query", "http_status": 200},
    ]
    r = compute_governance_analytics(decisions, audit)
    assert r["manual_review_rate"] == pytest.approx(0.5, abs=0.001)


def test_manual_review_rate_zero_when_no_manual_actions():
    decisions = [{"governance_state": "AUTO_APPROVED"}]
    audit = [{"action": "normal_query", "http_status": 200}] * 5
    r = compute_governance_analytics(decisions, audit)
    assert r["manual_review_rate"] == 0.0


# ── Publication success rate ──────────────────────────────────────────────────

def test_publication_success_rate_with_mixed_states():
    decisions = [
        {"governance_state": "AUTO_APPROVED", "can_publish": True},
        {"governance_state": "AUTO_APPROVED", "can_publish": True},
        {"governance_state": "BLOCKED",       "can_publish": False},
        {"governance_state": "AUTO_APPROVED", "can_publish": True},
    ]
    r = compute_governance_analytics(decisions, [])
    assert r["publication_success_rate"] == pytest.approx(3 / 4, abs=0.001)


def test_publication_success_rate_empty_governance_returns_zero():
    r = compute_governance_analytics([], [{"action": "some_action"}])
    assert r["publication_success_rate"] == 0.0


# ── Top governance risks ───────────────────────────────────────────────────────

def test_top_governance_risks_high_severity_first():
    decisions = [
        {"governance_state": "BLOCKED", "severity": "high",
         "escalation_reason": "hard_constraint_violation"},
        {"governance_state": "AUTO_APPROVED"},
        {"governance_state": "AUTO_APPROVED"},
    ]
    r = compute_governance_analytics(decisions, [])
    assert len(r["top_governance_risks"]) <= 5
    top = r["top_governance_risks"][0]
    assert top["severity"] == "high"
    assert top["count"] == 1


def test_top_governance_risks_aggregated_count():
    decisions = (
        [{"governance_state": "BLOCKED", "severity": "high",
          "escalation_reason": "hard_constraint_violation"}] * 3
        + [{"governance_state": "ESCALATION_REQUIRED", "severity": "high",
            "escalation_reason": "hard_constraint_violation"}] * 2
    )
    r = compute_governance_analytics(decisions, [])
    assert len(r["top_governance_risks"]) == 1
    assert r["top_governance_risks"][0]["count"] == 5


# ── Missing timestamps — cycle time gracefully returns 0.0 ─────────────────────

def test_missing_timestamps_cycle_time_zero():
    decisions = [
        {"governance_state": "AUTO_APPROVED", "submitted_at": None,
         "approved_at": None},
    ]
    r = compute_governance_analytics(decisions, [])
    assert r["average_approval_cycle_hours"] == 0.0


# ── Cycles computed from timestamps ──────────────────────────────────────────

def test_cycle_time_computed_from_timestamps():
    decisions = [
        {
            "governance_state": "AUTO_APPROVED",
            "submitted_at": "2026-03-20T09:00:00+07:00",
            "approved_at":  "2026-03-20T14:00:00+07:00",
        }
    ]
    r = compute_governance_analytics(decisions, [])
    assert r["average_approval_cycle_hours"] == pytest.approx(5.0, abs=0.1)


# ── Period info passthrough ───────────────────────────────────────────────────

def test_period_info_preserved_when_provided():
    pi = {"academic_year": "2568", "semester": "2"}
    r = compute_governance_analytics([{"state": "ok"}], [], period_info=pi)
    assert r["period_info"] == pi


# ── Output shape ─────────────────────────────────────────────────────────────

def test_output_containing_all_required_keys():
    r = compute_governance_analytics([], [])
    required_keys = {
        "governance_health_score", "average_approval_cycle_hours",
        "blocker_count", "override_count", "rollback_count",
        "escalation_rate", "manual_review_rate", "publication_success_rate",
        "top_governance_risks", "period_info",
    }
    missing = required_keys - r.keys()
    assert not missing, f"Missing keys: {missing}"
