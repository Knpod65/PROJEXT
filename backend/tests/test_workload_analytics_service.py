"""Tests for workload_analytics_service.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.workload_analytics_service import (
    compute_workload_analytics,
    build_workload_summary_dict,
)


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
    r = build_workload_summary_dict(wm)
    assert r["total_assignments"] == 120
    assert r["average_load"] == 4.0
    assert r["fairness_band"] == "amber"


def test_build_workload_summary_dict_empty_dict():
    r = build_workload_summary_dict({})
    assert r["total_assignments"] == 0
    assert r["average_load"] == 0.0
    assert r["fairness_band"] == "green"


def test_build_workload_summary_dict_none_input():
    r = build_workload_summary_dict(None)  # type: ignore[arg-type]
    assert r["total_assignments"] == 0
    assert r["average_load"] == 0.0
    assert r["fairness_band"] == "green"


# ── compute_workload_analytics — empty inputs ─────────────────────────────────

def test_empty_inputs_returns_zeroed_defaults():
    r = compute_workload_analytics([], [])
    assert r["total_assignments"] == 0
    assert r["average_load"] == 0.0
    assert r["max_load"] == 0
    assert r["imbalance_score"] == 0.0
    assert r["overloaded_staff_count"] == 0
    assert r["fairness_band"] == "green"
    assert r["top_overload_risks"] == []


def test_empty_inputs_fairness_band_green():
    r = compute_workload_analytics([], [])
    assert r["fairness_band"] == "green"


# ── compute_workload_analytics — balanced loads ───────────────────────────────

def test_balanced_loads_green_fairness():
    staff = [{"user_id": i, "staff_name": f"Staff {i}",
               "department": "ESQ", "total_load": 4.0} for i in range(10)]
    detail = []
    r = compute_workload_analytics(staff, detail)
    assert r["fairness_band"] == "green"
    assert r["imbalance_score"] < 0.2
    assert r["overloaded_staff_count"] == 0


def test_balanced_loads_no_overload_risks():
    staff = [{"user_id": i, "staff_name": f"Staff {i}",
               "department": "ESQ", "total_load": 4.0} for i in range(10)]
    r = compute_workload_analytics(staff, [])
    assert r["top_overload_risks"] == []


def test_balanced_loads_sum_correct():
    staff = [{"user_id": i, "staff_name": f"Staff {i}",
               "department": "ESQ", "total_load": 4.0} for i in range(10)]
    r = compute_workload_analytics(staff, [])
    assert r["total_assignments"] == 40.0
    assert r["max_load"] == 4
    assert r["overloaded_staff_count"] == 0


# ── compute_workload_analytics — spiked load ──────────────────────────────────

def test_spiked_load_produces_red_fairness_or_at_least_overloaded():
    staff = [
        {"user_id": 1, "staff_name": "Staff 1", "department": "ESQ", "total_load": 6.0},
        {"user_id": 2, "staff_name": "Staff 2", "department": "ESQ", "total_load": 6.0},
        {"user_id": 3, "staff_name": "Staff 3", "department": "ESQ", "total_load": 6.0},
        {"user_id": 4, "staff_name": "Staff 4", "department": "ESQ", "total_load": 18.0},
    ]
    r = compute_workload_analytics(staff, [])
    # fairness is red due to high std_dev relative to mean
    # or overloaded_staff_count > 0
    assert r["fairness_band"] in ("amber", "red")
    assert r["overloaded_staff_count"] >= 1


def test_spiked_load_top_overload_risks_present():
    staff = [
        {"user_id": 1, "staff_name": "Staff 1", "department": "ESQ", "total_load": 6.0},
        {"user_id": 9, "staff_name": "Staff 9", "department": "ESQ", "total_load": 18.0},
    ]
    r = compute_workload_analytics(staff, [])
    assert len(r["top_overload_risks"]) >= 1
    assert r["top_overload_risks"][0]["user_id"] == 9
    assert r["top_overload_risks"][0]["current_load"] == 18


# ── repeated burden detection ─────────────────────────────────────────────────

def test_repeated_burden_detected():
    staff = [{"user_id": 1, "staff_name": "S1", "department": "ESQ", "total_load": 5.0}]
    duty = [
        {"user_id": 1, "duty_type": "invigilation", "date": "2026-03-20", "workload_count": 3},
        {"user_id": 1, "duty_type": "invigilation", "date": "2026-03-20", "workload_count": 2},
        {"user_id": 1, "duty_type": "invigilation", "date": "2026-03-21", "workload_count": 4},
    ]
    r = compute_workload_analytics(staff, duty)
    burden_ids = {b["user_id"] for b in r["repeated_burden_detection"]}
    assert 1 in burden_ids


def test_no_repeated_burden_when_single_assignment_per_day():
    staff = [{"user_id": 1, "staff_name": "S1", "department": "ESQ", "total_load": 5.0}]
    duty = [
        {"user_id": 1, "duty_type": "invigilation", "date": "2026-03-20", "workload_count": 3},
        {"user_id": 1, "duty_type": "invigilation", "date": "2026-03-21", "workload_count": 4},
    ]
    r = compute_workload_analytics(staff, duty)
    assert r["repeated_burden_detection"] == []


# ── per-role / per-department summaries ──────────────────────────────────────

def test_per_role_summary_counts_duties():
    staff = [{"user_id": 1, "staff_name": "S1", "department": "ESQ", "total_load": 5.0}]
    duty = [
        {"user_id": 1, "duty_type": "invigilation", "date": "2026-03-20", "workload_count": 3},
        {"user_id": 1, "duty_type": "paper_distribution", "date": "2026-03-20", "workload_count": 2},
    ]
    r = compute_workload_analytics(staff, duty)
    assert "invigilation" in r["per_role_summary"]
    assert r["per_role_summary"]["invigilation"]["count"] == 1
    assert r["per_role_summary"]["invigilation"]["total_workload"] == 3.0
    assert r["per_role_summary"]["paper_distribution"]["count"] == 1
    assert r["per_role_summary"]["paper_distribution"]["total_workload"] == 2.0


def test_per_department_summary_counts_staff():
    staff = [
        {"user_id": 1, "staff_name": "S1", "department": "ESQ", "total_load": 5.0},
        {"user_id": 2, "staff_name": "S2", "department": "ESQ", "total_load": 3.0},
        {"user_id": 3, "staff_name": "S3", "department": "DBA", "total_load": 2.0},
    ]
    r = compute_workload_analytics(staff, [])
    assert r["per_department_summary"]["ESQ"]["count"] == 2
    assert r["per_department_summary"]["ESQ"]["total_workload"] == 8.0
    assert r["per_department_summary"]["DBA"]["count"] == 1
    assert r["per_department_summary"]["DBA"]["total_workload"] == 2.0


# ── output shape ──────────────────────────────────────────────────────────────

def test_output_has_required_keys():
    r = compute_workload_analytics([], [])
    required = {
        "total_assignments", "average_load", "max_load", "imbalance_score",
        "overloaded_staff_count", "fairness_band", "top_overload_risks",
        "per_role_summary", "per_department_summary",
        "repeated_burden_detection", "period_info",
    }
    missing = required - r.keys()
    assert not missing, f"Missing keys: {missing}"


def test_period_info_defaults_to_empty_dict():
    r = compute_workload_analytics([], [])
    assert r["period_info"] == {}


def test_period_info_reflects_input():
    pi = {"academic_year": "2568", "semester": "2", "exam_type": "final"}
    r = compute_workload_analytics([], [], period_info=pi)
    assert r["period_info"] == pi
