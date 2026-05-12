# Governed Optimization Pipeline
## EMS Academic Operations Platform

**Status:** Implemented in read-only observer form and ready for further governance hardening.
**Scope:** FastAPI backend only. No optimizer decision changes, no DB schema changes.

---

## 1. Purpose

The optimization pipeline now has a governed observation layer that reviews generated schedules after the solver finishes. The goal is to make optimization explainable, reviewable, and auditable without changing room allocation behavior or API contracts.

The pipeline currently combines:

- `optimization_explanation_service.py`
- `optimization_quality_service.py`
- `optimization_recheck_service.py`
- `optimization_pipeline_observer_service.py`
- `optimization_governance_service.py`
- `optimization_report_builder.py`

---

## 2. Pipeline Stages

1. **Generation**
   - The optimizer produces schedules as it does today.
   - No allocation decision is altered by the observer layer.

2. **Observation**
   - The observer consumes the generated schedule only.
   - It normalizes entries into safe frontend-facing structures.

3. **Explainability**
   - Each entry is explained using room, staff, distribution, split, timeslot, conflict, and fairness factors.
   - Explanations are post-hoc and heuristic unless a real solver trace exists.

4. **Quality Scoring**
   - The schedule is scored across fairness, efficiency, conflict risk, document readiness, QR readiness, and governance readiness.

5. **Recheck Validation**
   - The schedule is validated against the recheck taxonomy.
   - Issues are grouped into hard fail, warning, info, and suggestion severities.

6. **Governance Decision**
   - A governance state is derived from the recheck summary and quality snapshot.
   - The state drives human review and override workflows.

7. **Report Assembly**
   - Structured payloads are assembled for dashboards and future export layers.

---

## 3. Current Governance States

- `AUTO_APPROVED`
- `APPROVAL_REQUIRED`
- `MANUAL_REVIEW_REQUIRED`
- `BLOCKED`

Current rules are intentionally conservative:

- `FAIL` from recheck maps to `BLOCKED`
- `PASS_WITH_WARNINGS` maps to `APPROVAL_REQUIRED`
- severe workload imbalance or fairness concerns can escalate to `MANUAL_REVIEW_REQUIRED`
- low governance readiness also escalates to `MANUAL_REVIEW_REQUIRED`

---

## 4. Read-Only Contract

The observer must not:

- mutate the schedule
- alter optimizer assignments
- change room selection logic
- change invigilator assignment logic
- change database state

The observer may:

- attach summary payloads
- compute quality metrics
- compute explanation payloads
- compute governance metadata
- prepare report structures

---

## 5. Frontend-Facing Payload Areas

The observer and report builder expose these normalized sections:

- `quality_summary`
- `explanation_summary`
- `recheck_summary`
- `governance`
- `issues`
- `warning_issues`

These are designed so the frontend can render badges, summary panels, explanation drawers, and review queues without guessing backend semantics.

---

## 6. Deferred Scope

Not implemented yet:

- persistence of audit events
- PDF rendering
- Excel export
- route rewrites
- solver trace ingestion
- policy table expansion
- multi-faculty governance branching

---

## 7. Future Hooks

Planned extension points:

- solver-trace ingestion when the optimizer exposes trace metadata
- approval workflow event emission
- override event auditing
- simulation and what-if scoring
- multi-faculty policy profiles
