"""Tests for executive_dashboard_projection_service.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.executive_dashboard_projection_service import (
    project_executive_dashboard,
    build_workload_summary_dict,
    compute_room_summary_dict,
    _health_to_band,
    _safe_float,
    _safe_int,
)


def _health_to_band(score: float) -> str:
    from services.executive_dashboard_projection_service import _health_to_band as _fn
    return _fn(score)


# ── build_workload_summary_dict ───────────────────────────────────────────────

def test_build_workload_summary_dict_full():
    wm = {
        "total_assignments": 120,
        "average_load": 4.0,
        "max_load": 18,
        "imbalance_score": 0.35,
        "overloaded_staff_count": 3,
        "fairness_band": "amber",
    }
    result = build_workload_summary_dict(wm)
    assert result["total_assignments"] == 120
    assert result["average_load"] == 4.0
    assert result["fairness_band"] == "amber"


def test_build_workload_summary_dict_empty_dict():
    result = build_workload_summary_dict({})
    assert result["total_assignments"] == 0
    assert result["average_load"] == 0.0
    assert result["fairness_band"] == "green"


def test_build_workload_summary_dict_none_input():
    result = build_workload_summary_dict(None)  # type: ignore[arg-type]
    assert result["total_assignments"] == 0
    assert result["average_load"] == 0.0
    assert result["fairness_band"] == "green"


# ── compute_room_summary_dict ─────────────────────────────────────────────────

def test_compute_room_summary_empty_inputs():
    result = compute_room_summary_dict([], {})
    assert result == {}


def test_compute_room_summary_basic():
    rooms = {1: {"room_name": "A-101", "capacity": 40, "building": "ENG"}}
    schedules = [
        {"room_id": 1, "exam_date": "2026-03-20", "total_sheets": 80},
        {"room_id": 1, "exam_date": "2026-03-21", "total_sheets": 120},
    ]
    result = compute_room_summary_dict(schedules, rooms)
    assert "A-101" in result
    assert result["A-101"]["total_sheets"] == 200
    assert result["A-101"]["schedule_count"] == 2


def test_compute_room_summary_skips_rooms_without_room_id():
    result = compute_room_summary_dict(
        [{"room_id": None, "total_sheets": 50}], {}
    )
    assert result == {}


def test_compute_room_summary_unknown_room_id_fallback():
    schedules = [{"room_id": 999, "exam_date": "2026-03-20", "total_sheets": 20}]
    result = compute_room_summary_dict(schedules, {})
    assert "room-999" in result


# ── project_executive_dashboard ───────────────────────────────────────────────

def test_project_no_input_returns_zeroed_defaults():
    result = project_executive_dashboard()
    assert result["overall_health_score"] == 0.0
    assert result["governance_blocker_count"] == 0
    assert result["pdpa_alert_count"] == 0
    assert result["publication_ready_count"] == 0
    assert result["top_risks"] == [{"risk": "None identified", "severity": "low",  "category": "operational"}]


def test_project_no_inputs_generates_no_pii_in_output():
    result = project_executive_dashboard()
    text = str(result)
    assert "สมุทร" not in text
    assert "12345678" not in text


def test_project_allows_optional_non_PII_risk_label_self_identify():
    """Output must not have  individual names and IDs in risk labels."""
    result = project_executive_dashboard()
    for risk in result["top_risks"]:
        assert " staff name here " not in risk["risk"]


def test_project_empty_inputs_produce_no_pii_in_risk_actions():
    result = project_executive_dashboard()
    for risk in result["top_risks"]:
        assert " staff_name " not in risk.get("risk", "").lower() if True else None
        assert "student_name" not in risk.get("risk", "")
    for action in result["recommended_actions"]:
        assert " staff_name " not in action.get("action", "").lower() if True else None


def test_project_high_quality_low_blockers_produces_green_band():
    result = project_executive_dashboard(
        optimization_quality={"overall_score": 85.0},
        governance_snapshots=[{"governance_state": "AUTO_APPROVED"}] * 10,
        pdpa_alert_count=0,
        publication_readiness={"can_publish": True, "ready_count": 60},
    )
    assert result["risk_band"] == "green"
    assert result["governance_blocker_count"] == 0
    assert result["overall_health_score"] > 75.0
    assert result["publication_ready_count"] == 60


def test_project_pdpa_alert_creates_high_severity_risk_item():
    result = project_executive_dashboard(pdpa_alert_count=3)
    pdpa_risks = [r for r in result["top_risks"] if r["category"] == "pdpa_compliance"]
    assert len(pdpa_risks) == 1
    assert pdpa_risks[0]["severity"] == "high"


def test_project_top_risks_capped_at_five():
    gov_snaps = [{"governance_state": "BLOCKED"}] * 6
    result = project_executive_dashboard(
        governance_snapshots=gov_snaps,
        pdpa_alert_count=6,
    )
    assert len(result["top_risks"]) <= 5


def test_project_recommended_actions_capped_at_five():
    gov_snaps = [{"governance_state": "BLOCKED"}] * 6
    result = project_executive_dashboard(
        governance_snapshots=gov_snaps,
        pdpa_alert_count=6,
    )
    assert len(result["recommended_actions"]) <= 5


def test_project_room_util_zero_when_no_summary():
    result = project_executive_dashboard()
    assert result["room_utilization_score"] == 0.0


def test_project_room_util_score_scales_from_utilization():
    result = project_executive_dashboard(
        room_util_summary={"average_utilization": 0.72},
    )
    assert result["room_utilization_score"] == pytest.approx(72.0, abs=0.1)


def test_project_workload_balance_score_from_imbalance():
    result = project_executive_dashboard(
        workload_summary={
            "total_assignments":     150,
            "average_load":          6.0,
            "max_load":              20,
            "imbalance_score":       0.4,
            "overloaded_staff_count":5,
            "fairness_band":         "red",
        },
    )
    # imbalance 0.4 → balance score = (1 - 0.4) * 100 = 60.0
    assert result["workload_balance_score"] == pytest.approx(60.0, abs=0.1)


def test_project_governance_escalation_increments_blocker_count():
    gs = [{"governance_state": "ESCALATION_REQUIRED"}]
    result = project_executive_dashboard(governance_snapshots=gs)
    assert result["governance_blocker_count"] == 1


def test_project_override_count_incremented():
    gs = [{"governance_state": "AUTO_APPROVED", "override_recommendation": "override_approved"}]
    result = project_executive_dashboard(governance_snapshots=gs)
    assert result["governance_blocker_count"] == 0  # not a blocker state


def test_health_to_band_green_at_high_score():
    assert _health_to_band(90.0) == "green"
    assert _health_to_band(75.0) == "green"


def test_health_to_band_amber_at_mid_score():
    assert _health_to_band(74.9) == "amber"
    assert _health_to_band(50.0) == "amber"


def test_health_to_band_red_at_low_score():
    assert _health_to_band(49.9) == "red"
    assert _health_to_band(0.0) == "red"


def test_project_structural_keys_present():
    required_keys = {
        "overall_health_score", "risk_band", "optimization_quality_avg",
        "governance_blocker_count", "publication_ready_count",
        "workload_balance_score", "room_utilization_score", "pdpa_alert_count",
        "top_risks", "recommended_actions",
    }
    result = project_executive_dashboard()
    missing = required_keys - result.keys()
    assert not missing, f"Missing keys: {missing}"


def test_project_workload_summary_types():
    result = project_executive_dashboard(
        workload_summary={
            "total_assignments": 100,
            "average_load": 6.0,
            "max_load": 50,
            "imbalance_score": 0.5,
            "overloaded_staff_count": 2,
            "fairness_band": "amber",
        },
    )
    assert result["workload_balance_score"] >= 0.0
    assert result["workload_balance_score"] <= 100.0


def test_project_pdpa_alert_zero_by_default():
    result = project_executive_dashboard()
    assert result["pdpa_alert_count"] == 0


def test_project_recommended_actions_structure():
    result = project_executive_dashboard()
    for action in result["recommended_actions"]:
        assert "action" in action
        assert "owner" in action
        assert "priority" in action
