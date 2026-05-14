"""Tests for executive_risk_service.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.executive_risk_service import compute_executive_risk_report


# ── Helpers ───────────────────────────────────────────────────────────────────

def _gov(state="AUTO_APPROVED"):
    return {"governance_state": state}


def _recheck(hard_fails=0, warnings=0):
    return {"hard_fail_count": hard_fails, "warning_count": warnings}


def _readiness(risk_score=20.0, blockers=None):
    return {"risk_score": risk_score, "blockers": blockers or []}


def _quality(**overrides):
    base = {
        "overall_score": 85,
        "quality_band": "GOOD",
        "risk_level": "LOW",
        "warnings": [],
        "future_operational_risks": [],
        "fairness_instability_warnings": [],
        "staffing_fragility_warnings": [],
        "overloaded_day_warnings": [],
        "risk_summary": "",
    }
    base.update(overrides)
    return base


def _report(**kwargs):
    return compute_executive_risk_report(
        quality_report=kwargs.get("quality", _quality()),
        governance=kwargs.get("gov", _gov()),
        recheck_summary=kwargs.get("recheck", _recheck()),
        readiness_dict=kwargs.get("readiness", _readiness()),
    )


# ── All keys present ──────────────────────────────────────────────────────────

def test_all_keys_present():
    r = _report()
    for key in (
        "overall_risk_band", "publishability_score", "governance_health",
        "critical_blockers", "operational_risks", "pdpa_risks",
        "fairness_risks", "staffing_risks", "overloaded_day_risks",
        "quality_snapshot", "risk_summary", "hard_fail_count", "warning_count",
    ):
        assert key in r, f"Missing key: {key}"


def test_quality_snapshot_keys():
    r = _report()
    for key in ("overall_score", "quality_band", "risk_level"):
        assert key in r["quality_snapshot"]


# ── Risk band — CRITICAL ──────────────────────────────────────────────────────

def test_critical_band_on_blocked_governance():
    r = _report(gov=_gov("BLOCKED"), recheck=_recheck(hard_fails=0))
    assert r["overall_risk_band"] == "CRITICAL"


def test_critical_band_on_hard_fails():
    r = _report(gov=_gov("AUTO_APPROVED"), recheck=_recheck(hard_fails=2))
    assert r["overall_risk_band"] == "CRITICAL"


def test_critical_band_both_blocked_and_fails():
    r = _report(gov=_gov("BLOCKED"), recheck=_recheck(hard_fails=3))
    assert r["overall_risk_band"] == "CRITICAL"


# ── Risk band — HIGH ──────────────────────────────────────────────────────────

def test_high_band_on_high_risk_score():
    r = _report(readiness=_readiness(risk_score=75.0))
    assert r["overall_risk_band"] == "HIGH"


def test_high_band_on_escalation_required():
    r = _report(gov=_gov("ESCALATION_REQUIRED"), readiness=_readiness(risk_score=30.0))
    assert r["overall_risk_band"] == "HIGH"


def test_high_band_on_manual_review_required():
    r = _report(gov=_gov("MANUAL_REVIEW_REQUIRED"), readiness=_readiness(risk_score=30.0))
    assert r["overall_risk_band"] == "HIGH"


# ── Risk band — MEDIUM ────────────────────────────────────────────────────────

def test_medium_band_on_moderate_risk_score():
    r = _report(readiness=_readiness(risk_score=50.0))
    assert r["overall_risk_band"] == "MEDIUM"


def test_medium_band_on_many_warnings():
    r = _report(readiness=_readiness(risk_score=10.0), recheck=_recheck(warnings=4))
    assert r["overall_risk_band"] == "MEDIUM"


# ── Risk band — LOW ───────────────────────────────────────────────────────────

def test_low_band_clean_state():
    r = _report(
        gov=_gov("AUTO_APPROVED"),
        recheck=_recheck(hard_fails=0, warnings=1),
        readiness=_readiness(risk_score=10.0),
    )
    assert r["overall_risk_band"] == "LOW"


# ── Governance health ─────────────────────────────────────────────────────────

def test_governance_health_healthy():
    r = _report(gov=_gov("AUTO_APPROVED"))
    assert r["governance_health"] == "HEALTHY"


def test_governance_health_blocked():
    r = _report(gov=_gov("BLOCKED"))
    assert r["governance_health"] == "BLOCKED"


def test_governance_health_review_required_escalation():
    r = _report(gov=_gov("ESCALATION_REQUIRED"))
    assert r["governance_health"] == "REVIEW_REQUIRED"


def test_governance_health_review_required_approval():
    r = _report(gov=_gov("APPROVAL_REQUIRED"))
    assert r["governance_health"] == "REVIEW_REQUIRED"


# ── Publishability score ──────────────────────────────────────────────────────

def test_publishability_score_computed():
    r = _report(readiness=_readiness(risk_score=30.0))
    assert r["publishability_score"] == pytest.approx(70.0)


def test_publishability_score_floored_at_zero():
    r = _report(readiness=_readiness(risk_score=150.0))
    assert r["publishability_score"] == 0.0


# ── Critical blockers ─────────────────────────────────────────────────────────

def test_critical_blockers_only_hard_fail():
    blockers = [
        {"severity": "HARD_FAIL", "code": "ROOM_CONFLICT"},
        {"severity": "WARNING", "code": "STAFF_OVERLOAD"},
    ]
    r = _report(readiness=_readiness(blockers=blockers))
    assert len(r["critical_blockers"]) == 1
    assert r["critical_blockers"][0]["code"] == "ROOM_CONFLICT"


def test_critical_blockers_empty_when_no_hard_fails():
    blockers = [{"severity": "WARNING", "code": "X"}]
    r = _report(readiness=_readiness(blockers=blockers))
    assert r["critical_blockers"] == []


# ── PDPA risk filtering ───────────────────────────────────────────────────────

def test_pdpa_risks_filtered_from_warnings():
    q = _quality(warnings=[
        "Potential PII exposure in column X",
        "Staff overloaded on Monday",
        "PDPA compliance gap detected",
        "data protection rules may apply",
    ])
    r = _report(quality=q)
    assert len(r["pdpa_risks"]) == 3
    assert len(r["other_warnings"] if "other_warnings" in r else []) == 0


def test_non_pdpa_warnings_not_in_pdpa_risks():
    q = _quality(warnings=["Staff overloaded on Monday"])
    r = _report(quality=q)
    assert r["pdpa_risks"] == []


# ── Passthrough lists ─────────────────────────────────────────────────────────

def test_operational_risks_passed_through():
    q = _quality(future_operational_risks=["Risk A", "Risk B"])
    r = _report(quality=q)
    assert r["operational_risks"] == ["Risk A", "Risk B"]


def test_fairness_risks_passed_through():
    q = _quality(fairness_instability_warnings=["Fairness issue"])
    r = _report(quality=q)
    assert r["fairness_risks"] == ["Fairness issue"]


def test_staffing_risks_passed_through():
    q = _quality(staffing_fragility_warnings=["Staff risk"])
    r = _report(quality=q)
    assert r["staffing_risks"] == ["Staff risk"]


def test_overloaded_day_risks_passed_through():
    q = _quality(overloaded_day_warnings=["Monday overloaded"])
    r = _report(quality=q)
    assert r["overloaded_day_risks"] == ["Monday overloaded"]


# ── Counts ────────────────────────────────────────────────────────────────────

def test_hard_fail_count_in_result():
    r = _report(recheck=_recheck(hard_fails=3))
    assert r["hard_fail_count"] == 3


def test_warning_count_in_result():
    r = _report(recheck=_recheck(warnings=5))
    assert r["warning_count"] == 5


# ── Empty quality report ──────────────────────────────────────────────────────

def test_empty_quality_report_does_not_raise():
    r = compute_executive_risk_report(
        quality_report={},
        governance=_gov(),
        recheck_summary=_recheck(),
        readiness_dict=_readiness(),
    )
    assert "overall_risk_band" in r
    assert r["operational_risks"] == []
    assert r["fairness_risks"] == []


# ── hard_error_count alias ────────────────────────────────────────────────────

def test_hard_error_count_alias_accepted():
    r = compute_executive_risk_report(
        quality_report=_quality(),
        governance=_gov(),
        recheck_summary={"hard_error_count": 2, "warning_count": 0},
        readiness_dict=_readiness(),
    )
    assert r["hard_fail_count"] == 2
    assert r["overall_risk_band"] == "CRITICAL"
