# AI Recommendation Layer

**Status:** Skeleton implemented — Phase 3D  
**Date:** 2026-05-14  
**File:** `backend/services/recommendation_service.py`

---

## Purpose

Aggregate quality signals, governance state, and predictive balancing heuristics
into a **prioritized, structured recommendation list** that a human scheduling
officer reviews and approves before any action is taken.

This layer is **advisory only**. It never mutates state.

---

## Architecture Contract (Non-Negotiable Rules)

| Rule | Enforcement |
|---|---|
| AI must NOT auto-publish or commit any schedule | `generate_recommendations()` has no DB access, no mutation |
| Every recommendation requires human approval | Callers must present output to an authorized user before acting |
| Every recommendation must cite rule / reason / source | Required keys in every output dict |
| No PII in recommendation payloads | Service reads aggregate counts from `predictive_balancing_service`; no student/staff personal data flows through |
| No governance bypass | Governance state drives the highest-priority recommendations, not a post-filter |
| Output must be auditable | Structured dicts only — no free-text blobs, no opaque objects |

---

## Input

```python
generate_recommendations(
    quality_report: dict,        # compute_quality_report() output
    governance_decision: dict,   # compute_governance_decision() output
    schedule: list[dict],        # normalized schedule entries
    *,
    context: dict | None = None, # audit metadata only (session_id, actor_id)
)
```

`context` is metadata for audit logging — it is **never** used to change
recommendation logic. Same inputs always produce same outputs.

---

## Output

```python
[
    {
        "priority": int,      # 1 = highest urgency; sorted ascending
        "category": str,      # GOVERNANCE_RESOLUTION | QUALITY_IMPROVEMENT | ...
        "action": str,        # human-readable imperative
        "message": str,       # explanation for the scheduling officer
        "source": str,        # which service produced this
        "rule": str | None,   # rule identifier for audit
        "reason": str | None, # why this rule fired
    },
    ...
]
```

List is always sorted ascending by `priority` before return.

---

## Recommendation Categories

| Constant | Value | Source |
|---|---|---|
| `CATEGORY_GOVERNANCE` | `GOVERNANCE_RESOLUTION` | governance state |
| `CATEGORY_QUALITY` | `QUALITY_IMPROVEMENT` | overall/dimension score |
| `CATEGORY_WORKLOAD` | `WORKLOAD_BALANCE` | predictive heuristics |
| `CATEGORY_STAFFING` | `STAFFING_RISK` | predictive heuristics |
| `CATEGORY_ROOM` | `ROOM_OPTIMIZATION` | predictive heuristics |

---

## Priority Scheme

| Priority | Trigger |
|---|---|
| 1 | BLOCKED governance state |
| 2 | ESCALATION_REQUIRED state OR critically low quality score (< 55) OR HIGH_RISK staff |
| 3 | MANUAL_REVIEW_REQUIRED state |
| 4 | APPROVAL_REQUIRED state |
| 5 | Quality score in review band (55–70) |
| 6 | Low room-efficiency or invigilator-balance scores |
| 7 | WARNING-level predictive heuristics |
| 10 | (no governance rec — AUTO_APPROVED) |

---

## Signal Sources

### Governance Signals

Governance state drives the highest-priority recommendations. A BLOCKED schedule
always surfaces as priority 1 regardless of quality scores.

State severity order (policy-defined):
`AUTO_APPROVED` < `APPROVAL_REQUIRED` < `MANUAL_REVIEW_REQUIRED`
< `ESCALATION_REQUIRED` < `BLOCKED`

### Quality Signals

Overall score thresholds (from `config/optimization_policy.py`):
- `< 55.0` → critical, trigger re-optimization
- `55.0–70.0` → review band, investigate before publishing
- `≥ 70.0` → acceptable, no quality recommendation

Per-dimension thresholds trigger `IMPROVE_DIMENSION` recommendations:
- `room_efficiency_score < 60` → `ROOM_EFFICIENCY_LOW`
- `invigilator_balance_score < 65` → `INVIGILATOR_BALANCE_LOW`
- `fairness_score < 65` → `FAIRNESS_LOW`

### Predictive Balancing Signals

Delegates to `predictive_balancing_service.recommend_rebalancing()` (Phase 3C).
`HIGH_RISK` severity maps to priority 2; `WARNING` maps to priority 7.

---

## Human-Approval Gate

```
generate_recommendations() → [list of recs]
         ↓
 Scheduling officer review UI
         ↓
 Officer selects approved actions
         ↓
 System executes only approved actions
```

Callers are responsible for the review step. This service provides the input to
that step — it does not control or skip it.

---

## Upstream Dependencies

| Dependency | Purpose |
|---|---|
| `optimization_quality_service.compute_quality_report()` | Quality score input |
| `optimization_governance_service.compute_governance_decision()` | Governance state input |
| `predictive_balancing_service.recommend_rebalancing()` | Workload/staffing signals |

---

## Extension Points (Future)

The skeleton is structured so that future signal sources can be added without
changing the function signature:

1. Add a new `_recommendations_from_*()` function
2. Call it inside `generate_recommendations()` and extend its result list
3. Use existing category/source constants or add new ones at module top

No architectural changes required — the output shape is stable.

---

## Test Coverage

21 tests: return type, required keys, priority sort order, all four governance
states, quality score thresholds (< 55, 55–70, ≥ 70), missing overall score,
per-dimension low scores, predictive high-risk integration, fragile day staffing
rec, empty schedule, context parameter isolation.
