"""Policy configuration for optimization governance and review thresholds."""
from __future__ import annotations

from typing import Any, Dict


DEFAULT_OPTIMIZATION_GOVERNANCE_THRESHOLDS: dict[str, float] = {
    "hard_fail_block": 1,
    "warning_approval_required": 1,
    "fairness_review_threshold": 72,
    "room_efficiency_review_threshold": 68,
    "staffing_fragility_threshold": 70,
    "split_complexity_threshold": 55,
    "quality_escalation_threshold": 55,
    "quality_review_threshold": 70,
    "conflict_escalation_threshold": 60,
}

ROOM_UTILIZATION_THRESHOLDS: dict[str, float] = {
    "low": 0.40,
    "moderate": 0.60,
    "target": 0.80,
}

SPLIT_SEVERITY_THRESHOLDS: dict[str, int] = {
    "review_split_count": 2,
    "high_risk_split_count": 4,
}

STAFFING_RISK_THRESHOLDS: dict[str, int] = {
    "balanced_load": 3,
    "review_load": 5,
    "high_risk_load": 7,
}


def get_optimization_governance_thresholds(overrides: Dict[str, float] | None = None) -> dict[str, float]:
    merged = dict(DEFAULT_OPTIMIZATION_GOVERNANCE_THRESHOLDS)
    merged.update(overrides or {})
    return merged


def build_optimization_policy_snapshot(overrides: Dict[str, float] | None = None) -> dict[str, Any]:
    return {
        "governance_thresholds": get_optimization_governance_thresholds(overrides),
        "room_utilization_thresholds": dict(ROOM_UTILIZATION_THRESHOLDS),
        "split_severity_thresholds": dict(SPLIT_SEVERITY_THRESHOLDS),
        "staffing_risk_thresholds": dict(STAFFING_RISK_THRESHOLDS),
    }
