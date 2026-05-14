# Optimization Native Traceability

**Status:** Implemented — Phase 1  
**Date:** 2026-05-14  
**Files:** `backend/policies/optimization_trace_policy.py`, `backend/services/optimization_trace_service.py`

---

## Purpose

EMS previously produced post-hoc explanations after a schedule was generated.
This module adds a **trace layer** that wraps existing service outputs (observer,
recheck, explanation, governance) into a canonical set of typed trace events.

Traces are **additive and read-only** — they never modify optimizer decisions.

---

## Trace Event Types (17)

| Event Type | When Produced |
|---|---|
| `OPTIMIZATION_STARTED` | Entry to observer payload wrapping |
| `CANDIDATE_GENERATED` | Reserved for future native solver instrumentation |
| `CANDIDATE_REJECTED` | Reserved for future native solver instrumentation |
| `CANDIDATE_SCORED` | Explanation factor category: TIMESLOT_SELECTION |
| `CONSTRAINT_APPLIED` | Recheck issue or CONFLICT_AVOIDANCE factor |
| `PENALTY_APPLIED` | Explanation factor: FAIRNESS_BALANCING |
| `ROOM_SELECTED` | Explanation factor: ROOM_SELECTION |
| `STAFF_SELECTED` | Explanation factor: STAFF_ASSIGNMENT |
| `DISTRIBUTOR_SELECTED` | Explanation factor: DISTRIBUTION_ASSIGNMENT |
| `SPLIT_DECISION_MADE` | Explanation factor: SPLIT_DECISION |
| `FALLBACK_USED` | Reserved — emitted when optimizer falls back to greedy |
| `FINAL_SELECTION_ACCEPTED` | Per schedule entry in observer payload |
| `RECHECK_STARTED` | Opening of recheck issue list |
| `RECHECK_COMPLETED` | Closing of recheck issue list |
| `GOVERNANCE_DECISION_CREATED` | Governance decision payload wrap |

---

## Trace Source Taxonomy

| Source | Meaning |
|---|---|
| `POST_HOC_TRACE` | Derived from existing service output after the fact |
| `POLICY_RULE` | Produced by a named, auditable policy rule |
| `SOLVER_TRACE` | Reserved — native CP-SAT solver instrumentation (future) |

When native solver trace is unavailable, `source = POST_HOC_TRACE`.
When produced by a named rule (e.g., recheck issue code), `source = POLICY_RULE`.

---

## Trace Event Shape

```python
{
    "event_type":      str,          # TraceEventType value
    "entity_type":     str | None,   # "schedule_entry", "period", etc.
    "entity_id":       Any,          # section_id, period_id, etc.
    "constraint_code": str | None,   # e.g. "LOW_UTILIZATION"
    "reason_code":     str | None,   # e.g. "OVER_CAPACITY"
    "score_delta":     float | None, # impact on quality score (negative = penalty)
    "severity":        str,          # "INFO" | "WARNING" | "HIGH_RISK"
    "source":          str,          # TraceSource value
    "metadata":        dict,         # safe key/value payload (PII-stripped)
    "timestamp":       str,          # ISO 8601 UTC
}
```

---

## PII Policy

The following keys are **permanently blocked** from appearing in any trace
metadata field. `strip_pii()` must be called before any metadata is
serialized, transmitted, or logged.

Blocked keys: `student_id`, `student_ids`, `student_name`, `student_names`,
`teacher_name`, `email`, `mobile`

These are enforced by `policies.optimization_trace_policy.strip_pii()` which
is called unconditionally inside `build_trace_event()`.

---

## Service API

```python
# Build one trace event from scratch
build_trace_event(event_type, *, entity_type, entity_id, constraint_code,
                  reason_code, score_delta, severity, source, metadata)

# Wrap observe_optimization_result() output
trace_from_observer_payload(observer_payload, *, session_id=None)

# Wrap a list of RecheckIssue dicts (from asdict(issue))
trace_from_recheck_issues(issues)

# Wrap explain_schedule() per-entry output
trace_from_explanation_factors(per_entry_explanations)

# Wrap determine_governance_state() output
trace_governance_decision(governance_payload)
```

---

## Additive Safety Guarantee

- No optimizer files (`routers/schedule.py`, `routers/optimize_workflow.py`) are imported or modified.
- Trace functions only read dicts returned by other services — they never write to DB, never call the solver, never modify schedules.
- All 15 tests pass with no DB connection required.

---

## Future: Native Solver Traceability

When the CP-SAT solver is instrumented natively (e.g., via OR-Tools callback hooks), `source` should be set to `SOLVER_TRACE` and the native decision point data placed in `metadata`. The `build_trace_event()` factory accepts this without any API change.
