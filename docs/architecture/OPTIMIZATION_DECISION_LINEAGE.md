# Optimization Decision Lineage
## Replay-ready Decision Lineage Foundation

---

## 1. Purpose

Decision lineage reconstructs how an optimization result was produced from a sequence of native trace events and post-hoc linked events.

It is designed to support:
- audit review
- governance review
- replay of candidate and constraint history
- rejected-alternative inspection
- future trace explorer APIs and UI

---

## 2. Core Service

`backend/services/optimization_trace_replay_service.py` provides pure replay helpers:
- `build_decision_lineage(trace_events)`
- `summarize_decision_lineage(trace_events)`
- `group_trace_events_by_entity(trace_events)`
- `find_rejected_alternatives(trace_events, entity_id=None)`
- `build_trace_timeline(trace_events)`

Rules:
- pure logic only
- no DB access
- no optimizer mutation
- works with trace-event dicts and `EventEnvelope` dicts
- normalizes and sorts by timestamp
- strips sensitive metadata keys during replay

---

## 3. Accepted Inputs

The replay service accepts either:
- native trace event dictionaries from `OptimizationTraceContext`
- event-envelope dictionaries that wrap a trace payload

Normalized fields:
- `trace_event_id`
- `trace_id`
- `session_id`
- `event_type`
- `stage`
- `entity_type`
- `entity_id`
- `candidate_type`
- `candidate_id`
- `constraint_code`
- `reason_code`
- `severity`
- `score_delta`
- `source`
- `message`
- `metadata`
- `timestamp`

---

## 4. Lineage Model

`build_decision_lineage(...)` returns:

```json
{
  "lineage": [
    {
      "entity_key": "section:101",
      "entity_type": "section",
      "entity_id": 101,
      "events": [],
      "rejected_alternatives": [],
      "final_selection": {}
    }
  ],
  "summary": {}
}
```

Each lineage item groups events by `entity_type:entity_id`.

Within one grouped lineage item, the replay model can expose:
- candidate generation
- candidate rejection
- candidate acceptance
- triggered constraints
- penalties
- final schedule acceptance

---

## 5. Summary Model

`summarize_decision_lineage(...)` returns:

```json
{
  "candidate_generated_count": 0,
  "candidate_rejected_count": 0,
  "candidate_accepted_count": 0,
  "constraint_triggered_count": 0,
  "penalty_count": 0,
  "selection_count": 0,
  "highest_severity": "INFO",
  "trace_source_breakdown": {}
}
```

This summary is intended for:
- report rollups
- audit dashboards
- governance triage
- completeness and maturity scoring

---

## 6. Current Coverage in D2

Replay-ready now:
- room selection lineage
- timeslot selection lineage
- boundary supervisor selection lineage
- single-room split lineage
- fairness penalty lineage
- fallback detection lineage
- final schedule selection lineage
- recheck issue linkage carried back into the same trace timeline

Partly available:
- rejected alternatives when explicitly emitted by adapters or future instrumentation
- post-hoc issues linked as `POST_HOC_TRACE`

Still deferred:
- deep CP-SAT branch history
- model-level infeasibility explanations
- full rejected-candidate history from every pruned solver branch
- multi-room split exploration lineage beyond the current boundary-safe instrumentation

---

## 7. Native and Post-hoc Interplay

D2 keeps both layers on purpose.

Native lineage provides:
- boundary-time decisions
- source attribution
- tradeoff acceptance
- explicit final-selection events

Post-hoc lineage still provides:
- recheck findings
- governance concerns
- quality/explainability overlays

The replay service can combine both as long as the events are normalized into the supported trace shape.

---

## 8. Safety Rules

Replay output must remain:
- PDPA-safe
- JSON-safe
- stable for API/report consumers
- additive to existing report behavior

Sensitive metadata keys are stripped during normalization and replay.

---

## 9. Future Extensions

Recommended next steps:
- persist sanitized event envelopes for cross-run replay
- add lineage filtering by section, room, staff, or trace source
- expose rejected alternatives in governance APIs
- build a frontend trace explorer with entity timeline and tradeoff drill-down
