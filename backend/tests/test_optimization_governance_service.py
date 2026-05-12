"""Tests for optimization governance hardening."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.optimization_governance_service import (
    analyze_override_safety,
    determine_governance_state,
)
from policies.optimization_policy import (
    ROOM_UTILIZATION_THRESHOLDS,
    SPLIT_SEVERITY_THRESHOLDS,
    STAFFING_RISK_THRESHOLDS,
    get_optimization_governance_thresholds,
)


def _quality(**overrides):
    payload = {
        "overall_score": 88,
        "quality_band": "GOOD",
        "risk_level": "LOW",
        "fairness_score": 90,
        "room_efficiency_score": 88,
        "invigilator_balance_score": 87,
        "distribution_balance_score": 86,
        "conflict_risk_score": 95,
        "operational_complexity_score": 90,
        "document_readiness_score": 95,
    }
    payload.update(overrides)
    return payload


def _summary(**overrides):
    payload = {
        "hard_fail_count": 0,
        "hard_error_count": 0,
        "warning_count": 0,
        "manual_review_required": False,
    }
    payload.update(overrides)
    return payload


def test_blocked_when_hard_fail_exists():
    result = determine_governance_state(_summary(hard_fail_count=1, hard_error_count=1), _quality(), [])
    assert result["governance_state"] == "BLOCKED"
    assert result["review_priority"] == "CRITICAL"
    assert "Hard validation failures" in result["approval_reasoning"]


def test_escalation_required_for_high_risk_quality():
    result = determine_governance_state(
        _summary(),
        _quality(quality_band="HIGH_RISK", conflict_risk_score=45, overall_score=40),
        [],
    )
    assert result["governance_state"] == "ESCALATION_REQUIRED"
    assert result["review_priority"] == "HIGH"
    assert result["escalation_reason"]


def test_manual_review_required_for_low_fairness():
    thresholds = get_optimization_governance_thresholds()
    result = determine_governance_state(
        _summary(),
        _quality(fairness_score=thresholds["fairness_review_threshold"] - 5),
        [],
    )
    assert result["governance_state"] == "MANUAL_REVIEW_REQUIRED"
    assert "manual governance review" in result["approval_reasoning"]


def test_approval_required_for_warning_only_case():
    result = determine_governance_state(_summary(warning_count=2), _quality(quality_band="ACCEPTABLE"), [])
    assert result["governance_state"] == "APPROVAL_REQUIRED"
    assert result["review_priority"] == "NORMAL"


def test_override_safety_marks_high_risk_when_hard_fail_persists():
    result = analyze_override_safety(
        _summary(hard_fail_count=2),
        _quality(quality_band="HIGH_RISK", overall_score=48, document_readiness_score=40),
        [{"code": "ROOM_CAPACITY_EXCEEDED"}],
    )
    assert result["override_severity"] == "HIGH_RISK"
    assert result["requires_escalation"] is True
    assert "ROOM_CAPACITY_EXCEEDED" in result["violated_constraints"]


def test_override_safety_can_be_safe_for_clean_schedule():
    result = analyze_override_safety(_summary(), _quality(), [])
    assert result["override_severity"] == "SAFE"
    assert result["requires_escalation"] is False


def test_governance_reasoning_keeps_compatibility_reason_field():
    result = determine_governance_state(_summary(), _quality(), [])
    assert result["governance_state"] == "AUTO_APPROVED"
    assert result["reason"] == result["approval_reasoning"]


def test_policy_thresholds_are_exposed_for_governance_consumers():
    thresholds = get_optimization_governance_thresholds()
    assert thresholds["hard_fail_block"] == 1
    assert ROOM_UTILIZATION_THRESHOLDS["target"] == 0.80
    assert SPLIT_SEVERITY_THRESHOLDS["high_risk_split_count"] == 4
    assert STAFFING_RISK_THRESHOLDS["high_risk_load"] == 7
