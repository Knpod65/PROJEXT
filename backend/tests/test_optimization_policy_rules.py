"""Tests for the optimization rule DSL and config."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.optimization_policy import OptimizationPolicyConfig
from policies.optimization_rules import (
    STANDARD_RULES,
    RuleResult,
    evaluate_rules,
    evaluate_schedule,
    rule_distributor_assigned,
    rule_fairness_threshold,
    rule_invigilator_minimum,
    rule_room_utilization_maximum,
    rule_room_utilization_minimum,
    rule_split_complexity,
)


# ── Test helpers ──────────────────────────────────────────────────────────

def _entry(**overrides):
    base = {
        "room": {"id": 1, "capacity": 30},
        "num_students": 20,
        "assigned_staff": [101, 102],
        "paper_distributor": "staff-dist-1",
        "split_count": 1,
        "course_id": "POL101",
        "section": "01",
    }
    base.update(overrides)
    return base


# ── OptimizationPolicyConfig ──────────────────────────────────────────────

def test_config_defaults():
    cfg = OptimizationPolicyConfig()
    assert cfg.rules_enforce_mode is True
    assert cfg.max_score_drop_before_escalation == 15.0
    assert cfg.penalty_ratio_review_threshold == 0.25
    assert 0.0 <= cfg.min_room_utilization_auto_approve <= 1.0
    assert cfg.quality_escalation_threshold == 55.0
    assert cfg.quality_review_threshold == 70.0


def test_config_env_override(monkeypatch):
    monkeypatch.setenv("OPT_RULES_ENFORCE", "false")
    monkeypatch.setenv("OPT_MAX_SCORE_DROP", "20.0")
    cfg = OptimizationPolicyConfig()
    assert cfg.rules_enforce_mode is False
    assert cfg.max_score_drop_before_escalation == 20.0


# ── RuleResult dataclass ──────────────────────────────────────────────────

def test_rule_result_is_immutable():
    r = RuleResult("TEST", True, "INFO", "ok")
    try:
        r.passed = False  # type: ignore[misc]
        assert False, "Should have raised"
    except Exception:
        pass


# ── rule_room_utilization_minimum ─────────────────────────────────────────

def test_room_util_min_passes_above_40pct():
    result = rule_room_utilization_minimum(_entry(num_students=15))
    assert result.passed
    assert result.severity == "INFO"


def test_room_util_min_fails_below_40pct():
    result = rule_room_utilization_minimum(_entry(num_students=5))
    assert not result.passed
    assert result.severity == "WARNING"
    assert result.constraint_code == "LOW_ROOM_UTILIZATION"
    assert result.score_impact < 0


def test_room_util_min_no_capacity_data():
    result = rule_room_utilization_minimum(_entry(room={}))
    assert result.passed  # no data = pass-through
    assert result.severity == "INFO"


# ── rule_room_utilization_maximum ─────────────────────────────────────────

def test_room_util_max_passes_within_capacity():
    result = rule_room_utilization_maximum(_entry(num_students=25))
    assert result.passed


def test_room_util_max_fails_over_capacity():
    result = rule_room_utilization_maximum(_entry(num_students=35))
    assert not result.passed
    assert result.severity == "HARD_FAIL"
    assert result.constraint_code == "ROOM_OVER_CAPACITY"
    assert result.score_impact <= -15


# ── rule_invigilator_minimum ──────────────────────────────────────────────

def test_invigilator_min_passes_with_staff():
    result = rule_invigilator_minimum(_entry())
    assert result.passed


def test_invigilator_min_fails_empty_staff():
    result = rule_invigilator_minimum(_entry(assigned_staff=[]))
    assert not result.passed
    assert result.severity == "HARD_FAIL"
    assert result.score_impact <= -15


def test_invigilator_min_ignores_none_staff():
    result = rule_invigilator_minimum(_entry(assigned_staff=[None, None]))
    assert not result.passed


# ── rule_distributor_assigned ─────────────────────────────────────────────

def test_distributor_passes_when_set():
    result = rule_distributor_assigned(_entry())
    assert result.passed


def test_distributor_fails_when_none():
    result = rule_distributor_assigned(_entry(paper_distributor=None))
    assert not result.passed
    assert result.severity == "WARNING"


def test_distributor_fails_when_empty_string():
    result = rule_distributor_assigned(_entry(paper_distributor=""))
    assert not result.passed


# ── rule_split_complexity ─────────────────────────────────────────────────

def test_split_complexity_passes_at_one():
    result = rule_split_complexity(_entry(split_count=1))
    assert result.passed


def test_split_complexity_suggestion_at_review_threshold():
    result = rule_split_complexity(_entry(split_count=2))
    assert not result.passed
    assert result.severity == "SUGGESTION"


def test_split_complexity_warning_at_high_risk():
    result = rule_split_complexity(_entry(split_count=4))
    assert not result.passed
    assert result.severity == "WARNING"


# ── rule_fairness_threshold ───────────────────────────────────────────────

def test_fairness_passes_balanced():
    result = rule_fairness_threshold(_entry(assigned_staff=[1, 2]))
    assert result.passed  # 2 <= 3 (balanced_load)


def test_fairness_suggestion_at_review():
    result = rule_fairness_threshold(_entry(assigned_staff=[1, 2, 3, 4, 5]))
    assert not result.passed
    assert result.severity == "SUGGESTION"


def test_fairness_warning_at_high_risk():
    result = rule_fairness_threshold(_entry(assigned_staff=list(range(7))))
    assert not result.passed
    assert result.severity == "WARNING"


# ── evaluate_rules ────────────────────────────────────────────────────────

def test_evaluate_rules_runs_all_standard_rules():
    results = evaluate_rules(_entry())
    assert len(results) == len(STANDARD_RULES)


def test_evaluate_rules_returns_rule_results():
    results = evaluate_rules(_entry())
    for r in results:
        assert isinstance(r, RuleResult)


# ── evaluate_schedule ─────────────────────────────────────────────────────

def test_evaluate_schedule_summary_keys():
    summary = evaluate_schedule([_entry()])
    assert "results" in summary
    assert "hard_fail_count" in summary
    assert "warning_count" in summary
    assert "suggestion_count" in summary
    assert "total_score_impact" in summary
    assert "passed_count" in summary
    assert "failed_count" in summary


def test_evaluate_schedule_detects_hard_fail():
    bad = _entry(assigned_staff=[], num_students=35)  # no staff + over capacity
    summary = evaluate_schedule([bad])
    assert summary["hard_fail_count"] >= 2


def test_evaluate_schedule_all_pass():
    good = _entry()
    summary = evaluate_schedule([good])
    assert summary["hard_fail_count"] == 0


def test_evaluate_schedule_score_impact_negative_on_failures():
    bad = _entry(assigned_staff=[], paper_distributor=None)
    summary = evaluate_schedule([bad])
    assert summary["total_score_impact"] < 0


def test_evaluate_schedule_multiple_entries():
    entries = [_entry(), _entry(assigned_staff=[])]
    summary = evaluate_schedule(entries)
    assert summary["hard_fail_count"] >= 1


def test_evaluate_schedule_empty():
    summary = evaluate_schedule([])
    assert summary["hard_fail_count"] == 0
    assert summary["results"] == []
