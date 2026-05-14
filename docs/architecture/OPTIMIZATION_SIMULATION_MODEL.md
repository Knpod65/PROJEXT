# Optimization Simulation Model

**Status:** Implemented — Phase 3B  
**Date:** 2026-05-14  
**Files:** `backend/services/optimization_simulation_service.py`, `backend/services/optimization_comparison_service.py`

---

## Purpose

Allow "compare before commit" — score a hypothetical alternative schedule
against the real one before any change is applied. No CP-SAT solver is
invoked. All transformations are deterministic deep-copies.

---

## Simulation Types

| Function | What It Models |
|---|---|
| `simulate_room_swap(schedule, index, new_room)` | Replacing one exam's room with a larger/smaller alternative |
| `simulate_staff_rebalance(schedule, max_load=3)` | Removing overloaded staff to expose the workload gap |
| `simulate_split_elimination(schedule)` | Collapsing all split-room arrangements to single-room |
| `simulate_distributor_fill(schedule, default)` | Filling all missing distributor slots with a placeholder |

All functions: **deep-copy the input — original is never mutated.**

---

## Scoring Pipeline

```python
from services.optimization_simulation_service import simulate_room_swap, score_simulation
from services.optimization_comparison_service import compare_quality_reports

# 1. Get current schedule entries (normalized dicts)
current_entries = [...]

# 2. Create alternative scenario
alternative_entries = simulate_room_swap(current_entries, 0, larger_room)

# 3. Score both
baseline_quality = score_simulation(current_entries)
alt_quality = score_simulation(alternative_entries)

# 4. Compare
diff = compare_quality_reports(baseline_quality, alt_quality)
# diff["overall_delta"] > 0 means alternative is better
```

---

## Scored Dimensions (9)

`fairness_score`, `room_efficiency_score`, `invigilator_balance_score`,
`distribution_balance_score`, `conflict_risk_score`,
`operational_complexity_score`, `document_readiness_score`,
`qr_readiness_score`, `governance_readiness_score`

---

## Comparison Output

```python
{
    "dimension_deltas": {
        "fairness_score": {"current": 75, "simulated": 82, "delta": 7, "improved": True},
        ...
    },
    "overall_delta": float,
    "alternative_is_better": bool,
    "baseline_band": str | None,
    "alternative_band": str | None,
    "improved_dimensions": [str, ...],
    "regressed_dimensions": [str, ...],
}
```

---

## Governance Comparison

```python
from services.optimization_comparison_service import compare_governance_decisions

diff = compare_governance_decisions(baseline_governance, alt_governance)
# diff["state_improved"] is True when alt has lower severity
```

Severity order: `AUTO_APPROVED` < `APPROVAL_REQUIRED` < `MANUAL_REVIEW_REQUIRED`
< `ESCALATION_REQUIRED` < `BLOCKED`

---

## No Persistence Required

Simulations are ephemeral — computed on-demand from the current schedule
payload. No new DB tables, no schema changes.

---

## Test Coverage

30 tests: room swap immutability, staff rebalance threshold, split elimination,
distributor fill, quality delta calculation, improved/regressed dimension lists,
governance state comparison, and all edge cases (empty schedule, missing dims).
