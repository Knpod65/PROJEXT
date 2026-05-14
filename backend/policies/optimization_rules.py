"""Declarative per-entry rule DSL for optimization governance.

Rules are pure Python callables: each accepts a normalized schedule-entry dict
and returns a RuleResult. They are composable, testable in isolation, and
additive — they do not change optimizer decisions.

Thresholds are read from policies.optimization_policy (never duplicated here).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class RuleResult:
    rule_id: str
    passed: bool
    severity: str        # "INFO" | "WARNING" | "HARD_FAIL"
    message: str
    constraint_code: str | None = None
    score_impact: float = 0.0


RuleFunc = Callable[[dict[str, Any]], RuleResult]


# ── Threshold accessors (lazy import to avoid circular deps) ────────────────

def _room_thresholds() -> dict[str, float]:
    from policies.optimization_policy import ROOM_UTILIZATION_THRESHOLDS
    return ROOM_UTILIZATION_THRESHOLDS


def _staffing_thresholds() -> dict[str, int]:
    from policies.optimization_policy import STAFFING_RISK_THRESHOLDS
    return STAFFING_RISK_THRESHOLDS


def _split_thresholds() -> dict[str, int]:
    from policies.optimization_policy import SPLIT_SEVERITY_THRESHOLDS
    return SPLIT_SEVERITY_THRESHOLDS


def _governance_thresholds() -> dict[str, float]:
    from policies.optimization_policy import get_optimization_governance_thresholds
    return get_optimization_governance_thresholds()


# ── Standard rules ──────────────────────────────────────────────────────────

def rule_room_utilization_minimum(entry: dict[str, Any]) -> RuleResult:
    """ROOM_UTIL_MIN — room utilization must meet the low threshold (≥ 40%)."""
    room = entry.get("room") or {}
    capacity = room.get("capacity") or 0
    students = entry.get("num_students") or 0
    if capacity <= 0:
        return RuleResult("ROOM_UTIL_MIN", True, "INFO", "No capacity data available.")
    utilization = students / capacity
    low = _room_thresholds().get("low", 0.40)
    passed = utilization >= low
    return RuleResult(
        "ROOM_UTIL_MIN",
        passed,
        "WARNING" if not passed else "INFO",
        f"Room utilization {utilization:.0%}" + ("" if passed else f" is below minimum {low:.0%}"),
        constraint_code="LOW_ROOM_UTILIZATION" if not passed else None,
        score_impact=0.0 if passed else -5.0,
    )


def rule_room_utilization_maximum(entry: dict[str, Any]) -> RuleResult:
    """ROOM_UTIL_MAX — room must not be over capacity (students ≤ capacity)."""
    room = entry.get("room") or {}
    capacity = room.get("capacity") or 0
    students = entry.get("num_students") or 0
    if capacity <= 0:
        return RuleResult("ROOM_UTIL_MAX", True, "INFO", "No capacity data available.")
    passed = students <= capacity
    return RuleResult(
        "ROOM_UTIL_MAX",
        passed,
        "HARD_FAIL" if not passed else "INFO",
        f"{students} students in room capacity {capacity}" + ("" if passed else " — OVER CAPACITY"),
        constraint_code="ROOM_OVER_CAPACITY" if not passed else None,
        score_impact=0.0 if passed else -20.0,
    )


def rule_invigilator_minimum(entry: dict[str, Any]) -> RuleResult:
    """INVIG_MIN — at least one invigilator must be assigned."""
    staff = [s for s in entry.get("assigned_staff", []) if s is not None]
    passed = len(staff) >= 1
    return RuleResult(
        "INVIG_MIN",
        passed,
        "HARD_FAIL" if not passed else "INFO",
        "At least one invigilator required." if not passed else f"{len(staff)} invigilator(s) assigned.",
        constraint_code="MISSING_INVIGILATOR" if not passed else None,
        score_impact=0.0 if passed else -20.0,
    )


def rule_distributor_assigned(entry: dict[str, Any]) -> RuleResult:
    """DIST_ASSIGNED — a paper distributor must be named."""
    passed = bool(entry.get("paper_distributor"))
    return RuleResult(
        "DIST_ASSIGNED",
        passed,
        "WARNING" if not passed else "INFO",
        "Paper distributor unassigned." if not passed else "Paper distributor assigned.",
        constraint_code="MISSING_DISTRIBUTION_STAFF" if not passed else None,
        score_impact=0.0 if passed else -8.0,
    )


def rule_split_complexity(entry: dict[str, Any]) -> RuleResult:
    """SPLIT_COMPLEXITY — split count above threshold requires review."""
    split_count = entry.get("split_count") or 1
    review_threshold = _split_thresholds().get("review_split_count", 2)
    high_risk_threshold = _split_thresholds().get("high_risk_split_count", 4)
    if split_count >= high_risk_threshold:
        return RuleResult(
            "SPLIT_COMPLEXITY",
            False,
            "WARNING",
            f"Split count {split_count} is high-risk (threshold: {high_risk_threshold}).",
            constraint_code="HIGH_SPLIT_COUNT",
            score_impact=-10.0,
        )
    if split_count >= review_threshold:
        return RuleResult(
            "SPLIT_COMPLEXITY",
            False,
            "SUGGESTION",
            f"Split count {split_count} warrants review (threshold: {review_threshold}).",
            constraint_code="SPLIT_COUNT_REVIEW",
            score_impact=-3.0,
        )
    return RuleResult("SPLIT_COMPLEXITY", True, "INFO", f"Split count {split_count} within limits.")


def rule_fairness_threshold(entry: dict[str, Any]) -> RuleResult:
    """FAIRNESS — staff load must not exceed the review threshold."""
    staff = [s for s in entry.get("assigned_staff", []) if s is not None]
    load = len(staff)
    review_load = _staffing_thresholds().get("review_load", 5)
    high_risk_load = _staffing_thresholds().get("high_risk_load", 7)
    if load >= high_risk_load:
        return RuleResult(
            "FAIRNESS",
            False,
            "WARNING",
            f"Staff load {load} is high-risk (threshold: {high_risk_load}).",
            constraint_code="OVERLOAD_HIGH_RISK",
            score_impact=-10.0,
        )
    if load >= review_load:
        return RuleResult(
            "FAIRNESS",
            False,
            "SUGGESTION",
            f"Staff load {load} approaching limit (threshold: {review_load}).",
            constraint_code="OVERLOAD_REVIEW",
            score_impact=-3.0,
        )
    return RuleResult("FAIRNESS", True, "INFO", f"Staff load {load} within balanced range.")


# ── Rule registry ───────────────────────────────────────────────────────────

STANDARD_RULES: tuple[RuleFunc, ...] = (
    rule_room_utilization_minimum,
    rule_room_utilization_maximum,
    rule_invigilator_minimum,
    rule_distributor_assigned,
    rule_split_complexity,
    rule_fairness_threshold,
)


# ── Evaluation helpers ──────────────────────────────────────────────────────

def evaluate_rules(
    entry: dict[str, Any],
    rules: Iterable[RuleFunc] = STANDARD_RULES,
) -> list[RuleResult]:
    """Run all rules against a single normalized schedule entry."""
    return [rule(entry) for rule in rules]


def evaluate_schedule(
    schedule: Iterable[dict[str, Any]],
    rules: Iterable[RuleFunc] = STANDARD_RULES,
) -> dict[str, Any]:
    """Run all rules against every entry in a schedule and return an aggregate summary."""
    rules_list = list(rules)
    all_results: list[dict[str, Any]] = []
    hard_fails = 0
    warnings = 0
    suggestions = 0

    for entry in schedule:
        for result in evaluate_rules(entry, rules_list):
            all_results.append({
                "rule_id": result.rule_id,
                "passed": result.passed,
                "severity": result.severity,
                "message": result.message,
                "constraint_code": result.constraint_code,
                "score_impact": result.score_impact,
            })
            if not result.passed:
                if result.severity == "HARD_FAIL":
                    hard_fails += 1
                elif result.severity == "WARNING":
                    warnings += 1
                elif result.severity == "SUGGESTION":
                    suggestions += 1

    return {
        "results": all_results,
        "hard_fail_count": hard_fails,
        "warning_count": warnings,
        "suggestion_count": suggestions,
        "total_score_impact": sum(r["score_impact"] for r in all_results),
        "passed_count": sum(1 for r in all_results if r["passed"]),
        "failed_count": sum(1 for r in all_results if not r["passed"]),
    }
