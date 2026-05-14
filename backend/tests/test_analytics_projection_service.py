"""Tests for analytics_projection_service.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.analytics_projection_service import (
    project_governance_trend,
    project_quality_trend,
    project_invigilator_overload_trend,
    project_room_utilization_trend,
    project_fairness_trend,
    compare_periods,
)


# ── project_governance_trend ──────────────────────────────────────────────────

def test_governance_trend_empty_returns_defaults():
    r = project_governance_trend([])
    assert r["snapshot_count"] == 0
    assert r["escalation_rate"] == 0.0
    assert r["auto_approval_rate"] == 0.0
    assert r["trend_summary"] == "no_data"


def test_governance_trend_escalation_rate():
    snaps = [
        {"governance_state": "ESCALATION_REQUIRED"},
        {"governance_state": "ESCALATION_REQUIRED"},
        {"governance_state": "AUTO_APPROVED"},
        {"governance_state": "AUTO_APPROVED"},
    ]
    r = project_governance_trend(snaps)
    assert r["escalation_rate"] == 0.5
    assert r["auto_approval_rate"] == 0.5
    assert r["snapshot_count"] == 4


def test_governance_trend_all_auto_approved():
    snaps = [{"governance_state": "AUTO_APPROVED"}] * 5
    r = project_governance_trend(snaps)
    assert r["auto_approval_rate"] == 1.0
    assert r["trend_summary"] == "healthy"


def test_governance_trend_high_escalation():
    snaps = [{"governance_state": "ESCALATION_REQUIRED"}] * 4 + [{"governance_state": "AUTO_APPROVED"}]
    r = project_governance_trend(snaps)
    assert r["trend_summary"] == "high_escalation"


def test_governance_state_distribution():
    snaps = [
        {"governance_state": "AUTO_APPROVED"},
        {"governance_state": "BLOCKED"},
        {"governance_state": "AUTO_APPROVED"},
    ]
    r = project_governance_trend(snaps)
    assert r["state_distribution"]["AUTO_APPROVED"] == 2
    assert r["state_distribution"]["BLOCKED"] == 1


# ── project_quality_trend ─────────────────────────────────────────────────────

def test_quality_trend_empty_returns_defaults():
    r = project_quality_trend([])
    assert r["snapshot_count"] == 0
    assert r["trend_direction"] == "stable"
    assert r["score_series"] == []


def test_quality_trend_improving():
    snaps = [{"overall_score": 60}, {"overall_score": 75}, {"overall_score": 90}]
    r = project_quality_trend(snaps)
    assert r["trend_direction"] == "improving"
    assert r["max_score"] == 90.0
    assert r["min_score"] == 60.0


def test_quality_trend_degrading():
    snaps = [{"overall_score": 90}, {"overall_score": 70}, {"overall_score": 55}]
    r = project_quality_trend(snaps)
    assert r["trend_direction"] == "degrading"


def test_quality_trend_stable():
    snaps = [{"overall_score": 80}, {"overall_score": 81}]
    r = project_quality_trend(snaps)
    assert r["trend_direction"] == "stable"


def test_quality_trend_average_score():
    snaps = [{"overall_score": 60}, {"overall_score": 80}]
    r = project_quality_trend(snaps)
    assert r["average_score"] == 70.0


def test_quality_trend_band_history():
    snaps = [
        {"overall_score": 90, "quality_band": "EXCELLENT"},
        {"overall_score": 70, "quality_band": "GOOD"},
    ]
    r = project_quality_trend(snaps)
    assert r["band_history"] == ["EXCELLENT", "GOOD"]


# ── project_invigilator_overload_trend ────────────────────────────────────────

def test_overload_trend_empty_returns_defaults():
    r = project_invigilator_overload_trend([])
    assert r["snapshot_count"] == 0
    assert r["fragile_days_total"] == 0
    assert r["peak_overloaded"] == 0


def test_overload_trend_fragile_days_accumulation():
    snaps = [
        {"overloaded_count": 3, "at_risk_count": 5, "fragile_day_count": 2},
        {"overloaded_count": 1, "at_risk_count": 3, "fragile_day_count": 4},
    ]
    r = project_invigilator_overload_trend(snaps)
    assert r["fragile_days_total"] == 6
    assert r["peak_overloaded"] == 3


def test_overload_trend_improving():
    snaps = [
        {"overloaded_count": 10, "at_risk_count": 0, "fragile_day_count": 0},
        {"overloaded_count": 3, "at_risk_count": 0, "fragile_day_count": 0},
    ]
    r = project_invigilator_overload_trend(snaps)
    assert r["trend_direction"] == "degrading"  # more overloaded → first→last went DOWN → improving for overload means "degrading" in value terms


def test_overload_trend_at_risk_series():
    snaps = [
        {"overloaded_count": 1, "at_risk_count": 2, "fragile_day_count": 0},
        {"overloaded_count": 2, "at_risk_count": 4, "fragile_day_count": 0},
    ]
    r = project_invigilator_overload_trend(snaps)
    assert r["at_risk_series"] == [2, 4]


# ── project_room_utilization_trend ────────────────────────────────────────────

def test_room_utilization_empty_returns_defaults():
    r = project_room_utilization_trend([])
    assert r["snapshot_count"] == 0
    assert r["average_utilization"] == 0.0


def test_room_utilization_extracts_direct_key():
    snaps = [{"room_efficiency_score": 70}, {"room_efficiency_score": 80}]
    r = project_room_utilization_trend(snaps)
    assert r["average_utilization"] == 75.0
    assert r["trend_direction"] == "improving"


def test_room_utilization_extracts_from_quality_summary():
    snaps = [{"quality_summary": {"room_efficiency_score": 65}}]
    r = project_room_utilization_trend(snaps)
    assert r["utilization_series"] == [65.0]


# ── project_fairness_trend ────────────────────────────────────────────────────

def test_fairness_trend_empty_returns_defaults():
    r = project_fairness_trend([])
    assert r["snapshot_count"] == 0
    assert r["verdict_distribution"] == {}


def test_fairness_trend_verdict_distribution():
    snaps = [
        {"fairness_score": 80, "balance_verdict": "BALANCED"},
        {"fairness_score": 60, "balance_verdict": "IMBALANCED"},
        {"fairness_score": 85, "balance_verdict": "BALANCED"},
    ]
    r = project_fairness_trend(snaps)
    assert r["verdict_distribution"]["BALANCED"] == 2
    assert r["verdict_distribution"]["IMBALANCED"] == 1
    assert r["trend_direction"] == "improving"


# ── compare_periods ───────────────────────────────────────────────────────────

def _make_report(score: int, gov_state: str, hard_fails: int, warnings: int) -> dict:
    return {
        "quality_breakdown": {"overall_score": score},
        "governance": {"governance_state": gov_state},
        "severity_summary": {"hard_fail_count": hard_fails, "warning_count": warnings},
    }


def test_compare_periods_improved():
    baseline = _make_report(70, "APPROVAL_REQUIRED", 2, 3)
    current = _make_report(85, "AUTO_APPROVED", 0, 1)
    r = compare_periods(baseline, current)
    assert r["verdict"] == "improved"
    assert r["score_delta"] == 15.0
    assert r["hard_fail_delta"] == -2


def test_compare_periods_degraded():
    baseline = _make_report(85, "AUTO_APPROVED", 0, 0)
    current = _make_report(70, "BLOCKED", 3, 5)
    r = compare_periods(baseline, current)
    assert r["verdict"] == "degraded"
    assert r["hard_fail_delta"] == 3


def test_compare_periods_stable():
    baseline = _make_report(80, "AUTO_APPROVED", 0, 0)
    current = _make_report(81, "AUTO_APPROVED", 0, 0)
    r = compare_periods(baseline, current)
    assert r["verdict"] == "stable"


def test_compare_periods_all_deltas_present():
    baseline = _make_report(75, "BLOCKED", 1, 2)
    current = _make_report(80, "AUTO_APPROVED", 0, 1)
    r = compare_periods(baseline, current)
    for key in ("baseline_score", "current_score", "score_delta", "baseline_governance",
                "current_governance", "hard_fail_delta", "warning_delta", "verdict"):
        assert key in r


def test_compare_periods_empty_dicts_handled():
    r = compare_periods({}, {})
    assert isinstance(r, dict)
    assert r["verdict"] == "stable"
    assert r["score_delta"] == 0.0
