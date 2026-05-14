# Predictive Balancing Model

**Status:** Implemented — Phase 3C  
**Date:** 2026-05-14  
**File:** `backend/services/predictive_balancing_service.py`

---

## Purpose

Detect workload imbalance **before** the recheck solver runs. All heuristics
analyze an already-generated schedule and output structured risk signals without
invoking the CP-SAT solver, without randomness, and without any ML model.

---

## No-ML Contract

Every function in this service is:

- **Deterministic** — identical input always produces identical output
- **Stateless** — no training data, no weights, no model files
- **Threshold-driven** — all numeric thresholds are loaded from
  `policies.optimization_policy.STAFFING_RISK_THRESHOLDS` and
  `policies.optimization_policy.ROOM_UTILIZATION_THRESHOLDS`; nothing is
  hard-coded in the service itself

---

## Heuristics

### 1. Staff Load Profile (`compute_staff_load_profile`)

Counts total assignments per staff member and the busiest single day.
Classifies each staff member using thresholds from `STAFFING_RISK_THRESHOLDS`:

| Classification | Total Assignments |
|---|---|
| `balanced` | < `review_load` (default 5) |
| `review` | ≥ `review_load` AND < `high_risk_load` |
| `high_risk` | ≥ `high_risk_load` (default 7) |

Output includes `at_risk_count`, `high_risk_count`, `total_staff`, and per-staff
`max_single_day`.

### 2. Fragile Staffing Day Detection (`detect_fragile_staffing_days`)

A day is **fragile** when the count of **unique** invigilators across all exams
that day is below `min_staff_threshold` (default 2). A single invigilator
covering multiple exams is still counted once — the risk is the single point
of failure, not the number of exams.

### 3. Room Bottleneck Detection (`detect_room_bottlenecks`)

Flags rooms where `num_students / capacity ≥ utilization_threshold` (default
0.95). Rooms at 95%+ capacity have no buffer for last-minute enrollment changes
and should be reassigned to a larger venue before the exam date.

Rooms with `capacity ≤ 0` are skipped (data-quality guard).

### 4. Same-Day Overload Detection (`detect_repeated_same_person_burden`)

Flags staff assigned to **more than** `same_day_max` exams on the same calendar
date (default 2). Scheduling the same person to supervise 3+ exams in one day
is operationally unsustainable and creates a single point of failure if the
person is absent.

---

## Recommendation Pipeline (`recommend_rebalancing`)

Combines all four heuristics into a single prioritized recommendation list.
Each recommendation is a plain dict — never a class, never a solver call:

```python
{
    "staff_id": int | None,
    "severity": "HIGH_RISK" | "WARNING",
    "risk_type": "WORKLOAD_IMBALANCE" | "FRAGILE_STAFFING_DAY" | "SAME_DAY_OVERLOAD",
    "message": str,
    "action": "REDISTRIBUTE" | "MONITOR" | "ADD_BACKUP_STAFF",
}
```

Severity mapping:

| Risk | Severity | Action |
|---|---|---|
| `high_risk` staff | `HIGH_RISK` | `REDISTRIBUTE` |
| `review` staff | `WARNING` | `MONITOR` |
| Fragile day | `WARNING` | `ADD_BACKUP_STAFF` |
| Same-day overload | `WARNING` | `REDISTRIBUTE` |

---

## Threshold Sources

Thresholds are loaded at call time (lazy import), never duplicated:

```python
from policies.optimization_policy import STAFFING_RISK_THRESHOLDS
# balanced_load: 3, review_load: 5, high_risk_load: 7
```

Changing the policy file automatically changes all heuristic behavior — no
service edits needed.

---

## Integration Points

- **`recommend_rebalancing()` output → `recommendation_service.generate_recommendations()`** (Phase 3D): predictive signals feed directly into the AI recommendation skeleton
- **`compute_staff_load_profile()` → frontend dashboard**: at-risk counts can drive warning badges without any API changes
- **Upstream**: reads the same schedule entry dicts produced by `optimization_pipeline_observer_service.observe_optimization_result()`

---

## Test Coverage

22 tests: empty schedule, assignment counting, all three classifications,
high-risk/at-risk aggregate counts, max single-day tracking, None staff
filtering, fragile day threshold, unique-staff deduplication, room bottleneck
threshold, zero-capacity guard, same-day overload boundary, recommendation
severity routing, balanced-schedule produces no HIGH_RISK, required keys on
every recommendation.
