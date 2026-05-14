# Optimization Policy DSL

**Status:** Implemented — Phase 2B  
**Date:** 2026-05-14  
**Files:** `backend/policies/optimization_rules.py`, `backend/config/optimization_policy.py`

---

## Purpose

Move governance thresholds and rules out of ad-hoc service code into a
declarative, testable rule registry. Rules are pure Python callables — no DB
access, no FastAPI imports, no side effects.

---

## Rule Format

```python
@dataclass(frozen=True)
class RuleResult:
    rule_id: str          # e.g. "ROOM_UTIL_MIN"
    passed: bool
    severity: str         # "INFO" | "SUGGESTION" | "WARNING" | "HARD_FAIL"
    message: str
    constraint_code: str | None  # e.g. "ROOM_OVER_CAPACITY"
    score_impact: float   # 0.0 (passed) or negative (failed)
```

---

## Standard Rules (6)

| Rule ID | Check | Severity on Fail |
|---|---|---|
| `ROOM_UTIL_MIN` | Utilization ≥ 40% (ROOM_UTILIZATION_THRESHOLDS["low"]) | WARNING |
| `ROOM_UTIL_MAX` | Students ≤ room capacity | HARD_FAIL |
| `INVIG_MIN` | At least one invigilator assigned | HARD_FAIL |
| `DIST_ASSIGNED` | Paper distributor is set | WARNING |
| `SPLIT_COMPLEXITY` | Split count within review/high-risk thresholds | SUGGESTION / WARNING |
| `FAIRNESS` | Staff assignment load within balanced/review/high-risk | SUGGESTION / WARNING |

---

## Threshold Sources

All threshold values are **imported from** `policies.optimization_policy` — never duplicated:

| Threshold dict | Rule using it |
|---|---|
| `ROOM_UTILIZATION_THRESHOLDS["low"]` (0.40) | `ROOM_UTIL_MIN` |
| `SPLIT_SEVERITY_THRESHOLDS["review_split_count"]` (2) | `SPLIT_COMPLEXITY` |
| `SPLIT_SEVERITY_THRESHOLDS["high_risk_split_count"]` (4) | `SPLIT_COMPLEXITY` |
| `STAFFING_RISK_THRESHOLDS["balanced_load"]` (3) | `FAIRNESS` |
| `STAFFING_RISK_THRESHOLDS["review_load"]` (5) | `FAIRNESS` |
| `STAFFING_RISK_THRESHOLDS["high_risk_load"]` (7) | `FAIRNESS` |

---

## API

```python
# Run all standard rules against one normalized schedule entry dict
results: list[RuleResult] = evaluate_rules(entry)

# Run all rules against an entire schedule and get an aggregate summary
summary: dict = evaluate_schedule(schedule)
# {results, hard_fail_count, warning_count, suggestion_count,
#  total_score_impact, passed_count, failed_count}

# Custom rule set
results = evaluate_rules(entry, rules=[rule_invigilator_minimum, rule_distributor_assigned])
```

---

## Config Layer (`config/optimization_policy.py`)

Typed, env-backed config for rule enforcement mode:

| Variable | Default | Meaning |
|---|---|---|
| `OPT_RULES_ENFORCE` | `true` | HARD_FAIL blocks release when True |
| `OPT_MAX_SCORE_DROP` | `15.0` | Score drop that triggers auto-escalation |
| `OPT_PENALTY_RATIO_REVIEW` | `0.25` | Penalty/score ratio requiring review |
| `OPT_MIN_ROOM_UTIL` | `0.40` | Minimum auto-approve utilization |
| `OPT_QUALITY_ESCALATION` | `55.0` | Score below which governance escalates |
| `OPT_QUALITY_REVIEW` | `70.0` | Score below which review is required |

---

## Adding New Rules

1. Write a function `rule_<name>(entry: dict) -> RuleResult` in `optimization_rules.py`.
2. Import thresholds from `policies.optimization_policy` (never hardcode).
3. Add to `STANDARD_RULES` tuple.
4. Add at least 2 tests to `tests/test_optimization_policy_rules.py`.
5. Document in this file.

---

## Test Coverage

37 tests covering all 6 rules (pass and fail cases), evaluate_rules, evaluate_schedule
(empty, single, multi-entry, score impact), RuleResult immutability, and config defaults.
