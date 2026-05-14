"""Tests for optimization_report_builder.py (additive analytics sections)."""
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.optimization_report_builder import build_optimization_report


# ── Observer stub factory ─────────────────────────────────────────────────────

def _make_observer(
    *,
    governance_state="AUTO_APPROVED",
    quality_band="EXCELLENT",
    overall_score=92,
    fairness_score=88,
    room_efficiency_score=85,
    invigilator_balance_score=80,
    operational_complexity_score=90,
    conflict_risk_score=85,
    governance_readiness_score=88,
    hard_fail_count=0,
    warning_count=0,
    avg_confidence=75,
    issues=None,
    checked_schedule_count=5,
):
    quality = {
        "overall_score": overall_score,
        "quality_band": quality_band,
        "fairness_score": fairness_score,
        "room_efficiency_score": room_efficiency_score,
        "invigilator_balance_score": invigilator_balance_score,
        "operational_complexity_score": operational_complexity_score,
        "conflict_risk_score": conflict_risk_score,
        "governance_readiness_score": governance_readiness_score,
    }
    governance = {
        "governance_state": governance_state,
        "review_priority": "LOW",
        "escalation_reason": None,
    }
    return {
        "quality_summary": quality,
        "recheck_summary": {
            "hard_fail_count": hard_fail_count,
            "warning_count": warning_count,
            "fragile_day_count": 0,
        },
        "issues": issues or [],
        "governance": governance,
        "explanation_summary": {
            "per_entry": [{"confidence": avg_confidence, "confidence_level": "MEDIUM"}],
            "average_confidence": avg_confidence,
            "confidence_levels": ["MEDIUM"],
            "categories_seen": [],
        },
        "checked_schedule_count": checked_schedule_count,
    }


def _make_schedule(**kwargs):
    s = MagicMock()
    s.exam_date = kwargs.get("exam_date", "2026-01-10")
    s.exam_time = kwargs.get("exam_time", "09:00")
    s.room_id = kwargs.get("room_id", 1)
    s.room = kwargs.get("room", MagicMock())
    s.supervisions = kwargs.get("supervisions", [MagicMock()])
    s.section = kwargs.get("section", MagicMock())
    s.section_id = kwargs.get("section_id", 10)
    s.rejected_room_candidates = kwargs.get("rejected_room_candidates", [])
    s.rejected_staff_candidates = kwargs.get("rejected_staff_candidates", [])
    return s


def _build_report(**kwargs):
    observer = _make_observer(**{k: v for k, v in kwargs.items() if k in {
        "governance_state", "quality_band", "overall_score", "fairness_score",
        "room_efficiency_score", "invigilator_balance_score", "operational_complexity_score",
        "conflict_risk_score", "governance_readiness_score", "hard_fail_count",
        "warning_count", "avg_confidence", "issues", "checked_schedule_count",
    }})
    schedules = kwargs.get("schedules", [_make_schedule()])
    with patch(
        "services.optimization_report_builder.observe_optimization_result",
        return_value=observer,
    ):
        return build_optimization_report(
            period=MagicMock(),
            schedules=schedules,
        )


# ── Existing keys are intact ──────────────────────────────────────────────────

def test_existing_keys_present():
    r = _build_report()
    for key in ("executive_summary", "issue_summary", "severity_summary",
                "quality_breakdown", "governance", "explanation_summary", "raw_observer"):
        assert key in r, f"Missing existing key: {key}"


# ── New additive keys present ─────────────────────────────────────────────────

def test_all_new_keys_present():
    r = _build_report()
    for key in (
        "risk_matrix", "rejected_candidate_analytics", "invigilator_overload_summary",
        "fairness_summary", "traceability_completeness_score",
        "quality_band_summary", "optimization_confidence_score",
    ):
        assert key in r, f"Missing new key: {key}"


# ── risk_matrix ───────────────────────────────────────────────────────────────

def test_risk_matrix_is_list():
    r = _build_report()
    assert isinstance(r["risk_matrix"], list)


def test_risk_matrix_entry_has_required_keys():
    r = _build_report()
    assert len(r["risk_matrix"]) > 0
    entry = r["risk_matrix"][0]
    assert {"dimension", "score", "risk_level", "threshold"} <= set(entry.keys())


def test_risk_matrix_low_score_gives_high_risk():
    r = _build_report(conflict_risk_score=30)
    entry = next(e for e in r["risk_matrix"] if e["dimension"] == "conflict_risk")
    assert entry["risk_level"] == "HIGH"


def test_risk_matrix_high_score_gives_low_risk():
    r = _build_report(fairness_score=95)
    entry = next(e for e in r["risk_matrix"] if e["dimension"] == "fairness")
    assert entry["risk_level"] == "LOW"


# ── rejected_candidate_analytics ─────────────────────────────────────────────

def test_rejected_candidate_analytics_keys():
    r = _build_report()
    ra = r["rejected_candidate_analytics"]
    assert {"total_room_rejections", "total_staff_rejections", "top_rejection_reasons"} <= set(ra.keys())


def test_rejected_candidate_analytics_counts_rooms():
    s = _make_schedule(
        rejected_room_candidates=[{"reason": "OVERCAPACITY"}, {"reason": "OVERCAPACITY"}],
    )
    r = _build_report(schedules=[s])
    assert r["rejected_candidate_analytics"]["total_room_rejections"] == 2


def test_rejected_candidate_analytics_counts_staff():
    s = _make_schedule(rejected_staff_candidates=[{"reason": "UNAVAILABLE"}])
    r = _build_report(schedules=[s])
    assert r["rejected_candidate_analytics"]["total_staff_rejections"] == 1


def test_rejected_candidate_analytics_empty_schedule():
    r = _build_report(schedules=[])
    ra = r["rejected_candidate_analytics"]
    assert ra["total_room_rejections"] == 0
    assert ra["total_staff_rejections"] == 0
    assert ra["top_rejection_reasons"] == []


def test_rejected_candidate_analytics_top_reasons_sorted():
    s = _make_schedule(
        rejected_room_candidates=[
            {"reason": "A"}, {"reason": "A"}, {"reason": "B"},
        ],
    )
    r = _build_report(schedules=[s])
    top = r["rejected_candidate_analytics"]["top_rejection_reasons"]
    assert top[0]["reason"] == "A"
    assert top[0]["count"] == 2


# ── quality_band_summary ──────────────────────────────────────────────────────

def test_quality_band_summary_auto_approved():
    r = _build_report(governance_state="AUTO_APPROVED")
    qbs = r["quality_band_summary"]
    assert qbs["can_auto_approve"] is True
    assert qbs["requires_review"] is False


def test_quality_band_summary_approval_required():
    r = _build_report(governance_state="APPROVAL_REQUIRED", quality_band="ACCEPTABLE", overall_score=72)
    qbs = r["quality_band_summary"]
    assert qbs["can_auto_approve"] is False
    assert qbs["requires_review"] is True


def test_quality_band_summary_has_band_and_score():
    r = _build_report(quality_band="GOOD", overall_score=82)
    qbs = r["quality_band_summary"]
    assert qbs["band"] == "GOOD"
    assert qbs["score"] == 82.0


# ── traceability_completeness_score ──────────────────────────────────────────

def test_traceability_score_is_float():
    r = _build_report()
    assert isinstance(r["traceability_completeness_score"], float)


def test_traceability_score_range():
    r = _build_report()
    score = r["traceability_completeness_score"]
    assert 0.0 <= score <= 100.0


def test_traceability_score_empty_schedule():
    r = _build_report(schedules=[])
    # With empty schedules but governance and explanation present, still gets some bonus
    assert r["traceability_completeness_score"] >= 0.0


# ── optimization_confidence_score ────────────────────────────────────────────

def test_confidence_score_matches_avg_confidence():
    r = _build_report(avg_confidence=80)
    assert r["optimization_confidence_score"] == 80.0


def test_confidence_score_zero_when_none():
    observer = _make_observer()
    observer["explanation_summary"]["average_confidence"] = None
    with patch("services.optimization_report_builder.observe_optimization_result", return_value=observer):
        r = build_optimization_report(period=MagicMock(), schedules=[_make_schedule()])
    assert r["optimization_confidence_score"] == 0.0


# ── fairness_summary ─────────────────────────────────────────────────────────

def test_fairness_summary_keys():
    r = _build_report()
    fs = r["fairness_summary"]
    assert {"fairness_score", "imbalanced_sections", "balance_verdict"} <= set(fs.keys())


def test_fairness_summary_balanced_verdict():
    r = _build_report(fairness_score=95, invigilator_balance_score=90)
    assert r["fairness_summary"]["balance_verdict"] == "BALANCED"


def test_fairness_summary_needs_rebalancing():
    r = _build_report(fairness_score=60, invigilator_balance_score=60)
    assert r["fairness_summary"]["balance_verdict"] == "NEEDS_REBALANCING"
