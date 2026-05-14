# Optimization Native Trace Engine
## D2 Solver-native Optimization Trace Engine

---

## 1. Purpose

D2 adds a native, additive trace layer around the existing EMS optimizer without rewriting the optimization algorithm, changing API compatibility, or persisting new database records.

The native trace engine answers:
- which candidate was generated or accepted
- which constraint or policy contributed
- which tradeoff or penalty was accepted
- which final schedule selection was emitted
- which recheck/governance issue was linked after generation

---

## 2. Current Native Coverage

Native now:
- in-memory trace collection via `backend/services/optimization_trace_context.py`
- candidate trace adapters for room, staff, timeslot, and split decisions
- constraint trace adapters for hard, soft, capacity, staffing, room conflict, student conflict, fairness, document readiness, and QR readiness checks
- selection trace adapters for room, staff, distribution, split, and final schedule selections
- observer/report integration through `optimization_pipeline_observer_service.py` and `optimization_report_builder.py`
- optimizer-boundary instrumentation in `backend/routers/schedule.py`
- replay-ready event normalization in `optimization_trace_replay_service.py`

Post-hoc remains:
- explanation generation in `optimization_explanation_service.py`
- quality scoring in `optimization_quality_service.py`
- full recheck issue generation in `optimization_recheck_service.py`
- governance assessment in `optimization_governance_service.py`

Deferred:
- direct OR-Tools internal branch exploration
- per-constraint CP-SAT infeasibility proofs
- full rejected-alternative capture from deep solver search
- persistent trace storage
- frontend trace explorer UI

---

## 3. Trace Components

### OptimizationTraceContext

`OptimizationTraceContext` is a pure in-memory collector with:
- `trace_id`
- `session_id`
- `events`
- `add_event(...)`
- `add_candidate_generated(...)`
- `add_candidate_rejected(...)`
- `add_candidate_accepted(...)`
- `add_constraint_triggered(...)`
- `add_penalty_applied(...)`
- `add_tradeoff_chosen(...)`
- `add_final_selection(...)`
- `to_dict()`
- `to_event_envelopes()`

Design rules:
- no DB writes
- JSON-safe payloads
- deterministic IDs and timestamps where practical
- PDPA masking before the event leaves the collector

### Adapters

Candidate adapter:
- `trace_room_candidate(...)`
- `trace_staff_candidate(...)`
- `trace_timeslot_candidate(...)`
- `trace_split_candidate(...)`
- `trace_rejected_candidate(...)`
- `trace_accepted_candidate(...)`

Constraint adapter:
- `trace_hard_constraint(...)`
- `trace_soft_constraint(...)`
- `trace_capacity_constraint(...)`
- `trace_staffing_constraint(...)`
- `trace_room_conflict_constraint(...)`
- `trace_student_conflict_constraint(...)`
- `trace_fairness_constraint(...)`
- `trace_document_readiness_constraint(...)`
- `trace_qr_readiness_constraint(...)`

Selection adapter:
- `trace_room_selection(...)`
- `trace_staff_selection(...)`
- `trace_distribution_selection(...)`
- `trace_split_selection(...)`
- `trace_final_schedule_selection(...)`

---

## 4. Trace Event Schema

Every native trace event is emitted in the following shape:

| Field | Meaning |
|---|---|
| `trace_event_id` | Stable per-event identifier |
| `trace_id` | Groups one optimization trace stream |
| `session_id` | Optimization session key |
| `event_type` | Candidate, constraint, penalty, tradeoff, or final selection |
| `stage` | Lifecycle stage such as `CANDIDATE`, `CONSTRAINT`, `SELECTION`, `FINAL_SELECTION` |
| `entity_type` | Usually `section`, `schedule_entry`, or `optimization_run` |
| `entity_id` | Stable entity identifier |
| `candidate_type` | `ROOM`, `STAFF`, `TIMESLOT`, `SPLIT`, `SCHEDULE`, or related type |
| `candidate_id` | Candidate identifier within the entity scope |
| `constraint_code` | Normalized constraint identifier |
| `reason_code` | Normalized reason or rejection code |
| `severity` | `INFO`, `SUGGESTION`, `WARNING`, `HIGH_RISK`, or `HARD_FAIL` |
| `score_delta` | Optional additive scoring impact |
| `source` | Trace origin |
| `message` | Human-readable explanation |
| `metadata` | PDPA-safe structured details |
| `timestamp` | ISO timestamp |

Allowed `source` values:
- `SOLVER_TRACE`
- `POLICY_RULE`
- `INPUT_CONSTRAINT`
- `POST_HOC_TRACE`
- `FALLBACK_HEURISTIC`

Core `event_type` values:
- `CANDIDATE_GENERATED`
- `CANDIDATE_REJECTED`
- `CANDIDATE_ACCEPTED`
- `CONSTRAINT_TRIGGERED`
- `PENALTY_APPLIED`
- `TRADEOFF_CHOSEN`
- `FINAL_SELECTION_ACCEPTED`

---

## 5. Candidate, Constraint, and Selection Schemas

### Candidate trace metadata

Candidate events may include:
- `capacity`
- `assigned_count`
- `utilization_ratio`
- `building`
- `floor`
- `room_type`
- `staff_current_load`
- `staff_role`
- `time_slot`
- `reason_code`

Supported reason codes currently include:
- `CAPACITY_TOO_LOW`
- `ROOM_UNAVAILABLE`
- `ROOM_ALREADY_ASSIGNED`
- `WALKING_DISTANCE_PENALTY`
- `BUILDING_SPREAD_PENALTY`
- `STAFF_OVERLOAD`
- `STAFF_UNAVAILABLE`
- `STAFF_ALREADY_ASSIGNED`
- `TIMESLOT_CONFLICT`
- `SPLIT_REQUIRED`
- `SPLIT_TOO_MANY_ROOMS`
- `FAIRNESS_PENALTY`
- `FALLBACK_USED`

### Constraint payload

Constraint adapters normalize into:

```json
{
  "constraint_code": "ROOM_CAPACITY",
  "constraint_type": "HARD",
  "passed": true,
  "severity": "INFO",
  "entity_type": "section",
  "entity_id": 101,
  "reason_code": "ROOM_CAPACITY_CONFIRMED",
  "score_delta": null,
  "metadata": {}
}
```

Constraint types:
- `HARD`
- `SOFT`
- `GOVERNANCE`

Severity rules:
- hard fail becomes `HARD_FAIL`
- soft fail becomes `WARNING` unless explicitly lowered
- passed checks can stay `INFO`

### Selection payload

Selection events capture:
- selected candidate
- accepted reason
- tradeoffs accepted
- contributing constraints
- quality impact
- governance relevance
- confidence level

---

## 6. Boundary Instrumentation

The safest non-invasive optimizer boundary is currently `backend/routers/schedule.py`.

Native instrumentation now records:
- selected timeslot at the schedule creation boundary
- selected room at the schedule creation boundary
- single-room split decisions
- post-room supervisor assignment decisions
- fairness penalty/tradeoff decisions
- final schedule selection acceptance
- greedy fallback usage
- post-hoc recheck issue linkage back into the same trace stream

What D2 deliberately does not change:
- solver objective
- room assignment rules
- staff assignment behavior
- response compatibility
- authentication or session behavior
- database schema

---

## 7. Traceability Completeness Score

`traceability_completeness_score` is additive and non-breaking.

Scoring model:
- 25 points when candidate traces exist
- 25 points when constraint traces exist
- 25 points when selection traces exist
- 25 points when final-selection traces exist
- 20 points fallback when only post-hoc context exists

Current D2 interpretation:
- boundary-instrumented runs can reach high completeness without requiring deep solver internals
- fully black-box or legacy post-hoc runs stay lower but remain compatible

---

## 8. Report Surface

Observer and report payloads now include:
- `native_trace_summary`
- `native_trace_events`
- `traceability_completeness_score`
- `trace_source_breakdown`

These fields are additive and optional. Existing report consumers remain compatible when native trace is absent.

---

## 9. Deferred Deep Solver Work

Still deferred on purpose:
- native trace from every CP-SAT candidate rejection during model search
- explicit conflict-set capture from solver internals
- deep split-room alternative enumeration
- persisted cross-run trace history
- user-facing lineage explorer

These are D2 deferrals, not regressions.

---

## 10. Future Direction

Recommended future work after D2:
- persist sanitized trace envelopes in a trace store
- expose trace replay/lineage over a read-only API
- add a frontend decision-lineage explorer
- deepen instrumentation into solver internals only where low-risk and measurable
