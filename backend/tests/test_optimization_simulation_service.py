"""Tests for optimization simulation and comparison services."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.optimization_comparison_service import (
    compare_governance_decisions,
    compare_quality_reports,
)
from services.optimization_simulation_service import (
    simulate_distributor_fill,
    simulate_room_swap,
    simulate_split_elimination,
    simulate_staff_rebalance,
)


# ── Test helpers ──────────────────────────────────────────────────────────

def _entry(**kw):
    base = {
        "section_id": 1,
        "course_id": "POL101",
        "room": {"id": 1, "capacity": 30},
        "num_students": 20,
        "assigned_staff": [101, 102],
        "paper_distributor": "dist-1",
        "split_count": 1,
        "exam_date": "2026-10-01",
        "exam_time": "09:00",
    }
    base.update(kw)
    return base


def _quality(**kw):
    base = {
        "overall_score": 80.0,
        "quality_band": "GOOD",
        "fairness_score": 75.0,
        "room_efficiency_score": 82.0,
        "invigilator_balance_score": 78.0,
        "distribution_balance_score": 80.0,
        "conflict_risk_score": 90.0,
        "operational_complexity_score": 85.0,
        "document_readiness_score": 70.0,
    }
    base.update(kw)
    return base


# ── simulate_room_swap ────────────────────────────────────────────────────

def test_room_swap_returns_new_list():
    schedule = [_entry()]
    result = simulate_room_swap(schedule, 0, {"id": 99, "capacity": 60})
    assert result is not schedule


def test_room_swap_does_not_mutate_original():
    schedule = [_entry()]
    simulate_room_swap(schedule, 0, {"id": 99, "capacity": 60})
    assert schedule[0]["room"]["id"] == 1


def test_room_swap_changes_target_entry():
    schedule = [_entry(), _entry(room={"id": 2, "capacity": 25})]
    result = simulate_room_swap(schedule, 0, {"id": 99, "capacity": 60})
    assert result[0]["room"]["id"] == 99
    assert result[1]["room"]["id"] == 2  # untouched


def test_room_swap_copies_new_room_fields():
    schedule = [_entry()]
    new_room = {"id": 55, "capacity": 40, "building": "B"}
    result = simulate_room_swap(schedule, 0, new_room)
    assert result[0]["room"]["building"] == "B"


# ── simulate_staff_rebalance ──────────────────────────────────────────────

def test_staff_rebalance_does_not_mutate_original():
    schedule = [_entry(assigned_staff=[101]) for _ in range(5)]
    simulate_staff_rebalance(schedule, max_load_per_staff=3)
    # original entries still have staff
    assert 101 in schedule[0]["assigned_staff"]


def test_staff_rebalance_removes_overloaded_staff():
    schedule = [_entry(assigned_staff=[101]) for _ in range(5)]
    result = simulate_staff_rebalance(schedule, max_load_per_staff=3)
    for entry in result:
        assert 101 not in entry["assigned_staff"]


def test_staff_rebalance_keeps_balanced_staff():
    schedule = [_entry(assigned_staff=[101, 102]), _entry(assigned_staff=[102])]
    result = simulate_staff_rebalance(schedule, max_load_per_staff=3)
    # 101 appears 1 time, 102 appears 2 times — both within limit
    assert 101 in result[0]["assigned_staff"]
    assert 102 in result[0]["assigned_staff"]


def test_staff_rebalance_handles_none_staff():
    schedule = [_entry(assigned_staff=[None, 101])]
    result = simulate_staff_rebalance(schedule, max_load_per_staff=3)
    assert result is not schedule


def test_staff_rebalance_empty_schedule():
    result = simulate_staff_rebalance([], max_load_per_staff=3)
    assert result == []


# ── simulate_split_elimination ────────────────────────────────────────────

def test_split_elimination_sets_all_to_one():
    schedule = [_entry(split_count=3), _entry(split_count=2)]
    result = simulate_split_elimination(schedule)
    for entry in result:
        assert entry["split_count"] == 1


def test_split_elimination_does_not_mutate_original():
    schedule = [_entry(split_count=4)]
    simulate_split_elimination(schedule)
    assert schedule[0]["split_count"] == 4


# ── simulate_distributor_fill ─────────────────────────────────────────────

def test_distributor_fill_assigns_default_when_missing():
    schedule = [_entry(paper_distributor=None), _entry()]
    result = simulate_distributor_fill(schedule, default_distributor="TBD")
    assert result[0]["paper_distributor"] == "TBD"
    assert result[1]["paper_distributor"] == "dist-1"  # preserved


def test_distributor_fill_does_not_mutate_original():
    schedule = [_entry(paper_distributor=None)]
    simulate_distributor_fill(schedule)
    assert schedule[0]["paper_distributor"] is None


# ── compare_quality_reports ───────────────────────────────────────────────

def test_compare_quality_reports_returns_overall_delta():
    diff = compare_quality_reports(_quality(overall_score=80), _quality(overall_score=85))
    assert diff["overall_delta"] == 5.0


def test_compare_quality_reports_alternative_is_better_true():
    diff = compare_quality_reports(_quality(overall_score=70), _quality(overall_score=80))
    assert diff["alternative_is_better"] is True


def test_compare_quality_reports_alternative_is_better_false():
    diff = compare_quality_reports(_quality(overall_score=80), _quality(overall_score=70))
    assert diff["alternative_is_better"] is False


def test_compare_quality_reports_dimension_deltas():
    diff = compare_quality_reports(
        _quality(fairness_score=70), _quality(fairness_score=80)
    )
    assert "fairness_score" in diff["dimension_deltas"]
    assert diff["dimension_deltas"]["fairness_score"]["delta"] == 10.0
    assert diff["dimension_deltas"]["fairness_score"]["improved"] is True


def test_compare_quality_reports_improved_and_regressed_lists():
    diff = compare_quality_reports(
        _quality(fairness_score=70, room_efficiency_score=90),
        _quality(fairness_score=80, room_efficiency_score=80),
    )
    assert "fairness_score" in diff["improved_dimensions"]
    assert "room_efficiency_score" in diff["regressed_dimensions"]


def test_compare_quality_reports_missing_dimension_skipped():
    baseline = {"overall_score": 80.0, "quality_band": "GOOD"}
    alt = {"overall_score": 85.0, "quality_band": "GOOD"}
    diff = compare_quality_reports(baseline, alt)
    assert diff["dimension_deltas"] == {}
    assert diff["overall_delta"] == 5.0


def test_compare_quality_reports_bands_returned():
    diff = compare_quality_reports(
        _quality(quality_band="GOOD"),
        _quality(quality_band="EXCELLENT"),
    )
    assert diff["baseline_band"] == "GOOD"
    assert diff["alternative_band"] == "EXCELLENT"


# ── compare_governance_decisions ─────────────────────────────────────────

def _gov(state="AUTO_APPROVED", priority="LOW"):
    return {"governance_state": state, "review_priority": priority}


def test_compare_governance_state_improved():
    diff = compare_governance_decisions(_gov("BLOCKED"), _gov("APPROVAL_REQUIRED"))
    assert diff["state_improved"] is True


def test_compare_governance_state_regressed():
    diff = compare_governance_decisions(_gov("AUTO_APPROVED"), _gov("BLOCKED"))
    assert diff["state_improved"] is False


def test_compare_governance_same_state():
    diff = compare_governance_decisions(_gov("AUTO_APPROVED"), _gov("AUTO_APPROVED"))
    assert diff["state_improved"] is False


def test_compare_governance_keys():
    diff = compare_governance_decisions(_gov("BLOCKED"), _gov("AUTO_APPROVED"))
    assert "baseline_state" in diff
    assert "alternative_state" in diff
    assert "baseline_priority" in diff
    assert "alternative_priority" in diff
