"""Tests for executive_dashboard_projection_service.py"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.executive_dashboard_projection_service import (
    build_workload_summary_dict,
    compute_room_summary_dict,
    project_executive_dashboard,
)


# ── build_workload_summary_dict ───────────────────────────────────────────────

def test_empty_workload_returns_defaults():
    summary = build_workload_summary_dict(None)
    assert summary["total_assignments"] == 0
    assert summary["average_load"] == 0.0
    assert summary["overloaded_staff_count"] == 0
    assert summary["fairness_band"] == "green"


def test_empty_per_staff_load_returns_defaults():
    summary = build_workload_summary_dict({"per_staff_load": []})
    assert summary["fairness_band"] == "green"
    assert summary["imbalance_score"] == 0.0


def test_balanced_loads_green_band():
    workload = {
        "per_staff_load": [
            {"user_id": i, "staff_name": f"Staff {i}", "total_load": 5.0}
            for i in range(10)
        ]
    }
    summary = build_workload_summary_dict(workload)
    assert summary["fairness_band"] == "green"
    assert summary["average_load"] == 5.0
    assert summary["overloaded_staff_count"] == 0


def test_spiked_load_red_band():
    base = [{"user_id": i, "staff_name": f"S{i}", "total_load": 4.0} for i in range(5)]
    base.append({"user_id": 5, "staff_name": "S5", "total_load": 50.0})
    summary = build_workload_summary_dict({"per_staff_load": base})
    assert summary["overloaded_staff_count"] >= 1
    assert summary["fairness_band"] == "red"


def test_max_load_is_highest():
    workload = {
        "per_staff_load": [
            {"user_id": 1, "staff_name": "S1", "total_load": 3.0},
            {"user_id": 2, "staff_name": "S2", "total_load": 10.0},
            {"user_id": 3, "staff_name": "S3", "total_load": 7.0},
        ]
    }
    summary = build_workload_summary_dict(workload)
    assert summary["max_load"] == 10


def test_overload_pct_calculated():
    base = [{"user_id": i, "staff_name": f"S{i}", "total_load": 10.0} for i in range(6)]
    base[-1]["total_load"] = 30.0
    summary = build_workload_summary_dict({"per_staff_load": base})
    risks = summary["top_overload_risks"]
    assert len(risks) >= 1
    assert risks[0]["current_load"] == 30


def test_empty_dict_workload_map_returns_defaults():
    summary = build_workload_summary_dict({})
    assert summary["total_assignments"] == 0
    assert summary["fairness_band"] == "green"


# ── compute_room_summary_dict ─────────────────────────────────────────────────

def test_empty_rooms_and_schedules():
    result = compute_room_summary_dict(None, None)
    assert result == {}


def test_empty_schedules_no_room_entries():
    rooms = [{"room_name": "A101", "building": "ENG", "capacity": 50}]
    result = compute_room_summary_dict([], rooms)
    assert "A101" not in result


def test_schedules_keyed_by_room_name():
    rooms = [{"room_name": "A101", "building": "ENG", "capacity": 50}]
    schedules = [
        {"room_name": "A101", "exam_date": "2026-01-10", "exam_time": "09:00",
         "sections_count": 1, "students_count": 30},
    ]
    result = compute_room_summary_dict(schedules, rooms)
    assert "A101" in result
    assert result["A101"]["building"] == "ENG"
    assert result["A101"]["slot_count"] == 1


def test_utilization_calculation():
    rooms = [{"room_name": "B202", "building": "SCI", "capacity": 100}]
    schedules = [
        {"room_name": "B202", "exam_date": "2026-01-10", "exam_time": "09:00",
         "sections_count": 1, "students_count": 40},
    ]
    result = compute_room_summary_dict(schedules, rooms)
    assert result["B202"]["avg_utilization"] == pytest.approx(0.4)


def test_multiple_slots_in_same_room():
    rooms = [{"room_name": "C303", "building": "MED", "capacity": 60}]
    schedules = [
        {"room_name": "C303", "exam_date": "2026-01-10", "exam_time": "09:00",
         "sections_count": 1, "students_count": 30},
        {"room_name": "C303", "exam_date": "2026-01-10", "exam_time": "13:00",
         "sections_count": 1, "students_count": 30},
    ]
    result = compute_room_summary_dict(schedules, rooms)
    assert result["C303"]["slot_count"] == 2
    assert result["C303"]["avg_utilization"] == pytest.approx(0.5)


# ── project_executive_dashboard ────────────────────────────────────────────────

def test_empty_inputs_returns_red_band():
    result = project_executive_dashboard()
    assert result["risk_band"] == "red"
    assert result["overall_health_score"] == 0.0
    assert result["top_risks"] == []
    assert result["recommended_actions"] == []


def test_high_quality_auto_approved_governance_above_amber():
    """High quality + auto-approved governance must show >= amber (no drop to red)."""
    quality = {
        "overall_score": 90,
        "quality_band": "EXCELLENT",
        "risk_level": "LOW",
        "future_operational_risks": [],
        "fairness_instability_warnings": [],
        "staffing_fragility_warnings": [],
        "overloaded_day_warnings": [],
        "risk_summary": "low risk summary",
    }
    governance_snaps = [{"governance_state": "AUTO_APPROVED"}] * 5
    result = project_executive_dashboard(
        optimization_quality=quality,
        governance_snapshots=governance_snaps,
    )
    assert result["overall_health_score"] >= 50.0
    assert result["governance_blocker_count"] == 0
    assert result["top_risks"] == []


def test_mixed_quality_and_escalations_amber_or_worse():
    """Partial quality + ESCALATION snapshots → amber or red (never to green)."""
    quality = {
        "overall_score": 55,
        "quality_band": "GOOD",
        "risk_level": "MEDIUM",
        "future_operational_risks": [],
        "fairness_instability_warnings": [],
        "staffing_fragility_warnings": [],
        "overloaded_day_warnings": [],
        "risk_summary": "medium risk summary",
    }
    governance_snaps = [
        {"governance_state": "ESCALATION_REQUIRED"},
        {"governance_state": "AUTO_APPROVED"},
    ]
    result = project_executive_dashboard(
        optimization_quality=quality,
        governance_snapshots=governance_snaps,
    )
    assert result["risk_band"] in ("amber", "red")
    assert result["governance_blocker_count"] == 0


def test_low_quality_blocked_governance_red_or_critical_band():
    """Low quality + BLOCKED governance must not show green."""
    quality = {
        "overall_score": 20,
        "quality_band": "ACCEPTABLE",
        "risk_level": "HIGH",
        "future_operational_risks": [],
        "fairness_instability_warnings": [],
        "staffing_fragility_warnings": [],
        "overloaded_day_warnings": [],
        "risk_summary": "high risk summary",
    }
    governance_snaps = [{"governance_state": "BLOCKED"}] * 2
    result = project_executive_dashboard(
        optimization_quality=quality,
        governance_snapshots=governance_snaps,
    )
    assert result["risk_band"] != "green"
    assert result["governance_blocker_count"] >= 1


def test_blockers_generate_governance_risk():
    quality = {
        "overall_score": 50,
        "quality_band": "GOOD",
        "risk_level": "LOW",
        "future_operational_risks": [],
        "fairness_instability_warnings": [],
        "staffing_fragility_warnings": [],
        "overloaded_day_warnings": [],
        "risk_summary": "medium risk summary",
    }
    governance_snaps = [{"governance_state": "BLOCKED"}]
    result = project_executive_dashboard(
        optimization_quality=quality,
        governance_snapshots=governance_snaps,
    )
    blocker_risks = [r for r in result["top_risks"] if r.get("category") == "governance"]
    assert any("blocker" in r["risk"].lower() for r in blocker_risks)


def test_workload_overload_generates_risk_and_action():
    """Mixed load (avg ~11.7, some items at 30+) triggers overload detection."""
    loads = [{"user_id": i, "staff_name": f"S{i}", "total_load": float(load)}
             for i, load in enumerate([10, 10, 10, 10, 10, 10, 10, 35, 35, 35])]
    workloads = {"per_staff_load": loads}
    quality = {
        "overall_score": 80,
        "quality_band": "GOOD",
        "risk_level": "LOW",
        "future_operational_risks": [],
        "fairness_instability_warnings": [],
        "staffing_fragility_warnings": [],
        "overloaded_day_warnings": [],
        "risk_summary": "low risk summary",
    }
    result = project_executive_dashboard(
        workload_map=workloads,
        optimization_quality=quality,
    )
    assert result["overloaded_staff_count"] > 0
    risks = [r for r in result["top_risks"] if r.get("category") == "workload"]
    assert any("overload" in r["risk"].lower() for r in risks)


def test_top_risks_capped_at_5():
    quality = {
        "overall_score": 20,
        "quality_band": "ACCEPTABLE",
        "risk_level": "HIGH",
        "future_operational_risks": [],
        "fairness_instability_warnings": [],
        "staffing_fragility_warnings": [],
        "overloaded_day_warnings": [],
        "risk_summary": "high risk summary",
    }
    workloads = {
        "per_staff_load": [
            {"user_id": i, "staff_name": f"S{i}", "total_load": 30.0}
            for i in range(10)
        ]
    }
    governance_snaps = [{"governance_state": "BLOCKED"}] * 10
    audit_logs = [{"action": f"pdpa_event_{i}"} for i in range(20)]
    result = project_executive_dashboard(
        optimization_quality=quality,
        governance_snapshots=governance_snaps,
        workload_map=workloads,
        audit_logs_recent=audit_logs,
    )
    assert len(result["top_risks"]) <= 5
    assert len(result["recommended_actions"]) <= 5


def test_has_all_required_keys():
    result = project_executive_dashboard()
    required = {
        "overall_health_score", "risk_band", "optimization_quality_avg",
        "governance_blocker_count", "publication_ready_count",
        "workload_balance_score", "room_utilization_score", "pdpa_alert_count",
        "top_risks", "recommended_actions",
    }
    assert required.issubset(result.keys())


def test_pdpa_alerts_from_audit_logs():
    audit_logs = [{"action": f"pdpa_event_{i}"} for i in range(5)]
    result = project_executive_dashboard(
        optimization_quality={
            "overall_score": 80, "quality_band": "GOOD", "risk_level": "LOW",
            "future_operational_risks": [], "fairness_instability_warnings": [],
            "staffing_fragility_warnings": [], "overloaded_day_warnings": [],
            "risk_summary": "",
        },
        audit_logs_recent=audit_logs,
    )
    assert result["pdpa_alert_count"] == 5


def test_publication_ready_count_integer():
    result = project_executive_dashboard(
        optimization_quality={"overall_score": 70, "quality_band": "GOOD", "risk_level": "LOW",
            "future_operational_risks": [], "fairness_instability_warnings": [],
            "staffing_fragility_warnings": [], "overloaded_day_warnings": [],
            "risk_summary": "low risk summary"},
        governance_snapshots=[{"governance_state": "AUTO_APPROVED"}],
    )
    assert isinstance(result["publication_ready_count"], int)
