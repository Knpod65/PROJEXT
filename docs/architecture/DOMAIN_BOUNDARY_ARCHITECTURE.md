# Domain Boundary Architecture
## EMS Academic Operations Platform — Domain Stabilization Phase
**Date:** 2026-05-14

---

## 1. Overview

The EMS backend is organized into 8 **logical enterprise domains**. These are not microservices — they are architectural groupings within a single FastAPI application. Each domain owns a coherent set of responsibilities with clearly defined inbound and outbound interfaces.

No files are moved. The domain map is the authoritative guide for **where new code belongs**.

---

## 2. Domain Map

### 2.1 `optimization`

**Responsibility:** Post-hoc analysis of CP-SAT-generated schedules. Read-only. Never re-invokes the solver.

| File | Role |
|------|------|
| `services/optimization_pipeline_observer_service.py` | Orchestrator: calls recheck, explanation, quality, governance → unified payload |
| `services/optimization_report_builder.py` | Orchestrator: wraps observer payload + 7 analytics keys |
| `services/optimization_recheck_service.py` | Binary validation → RecheckIssue list |
| `services/optimization_explanation_service.py` | 7-factor explanation → DecisionExplanation per entry |
| `services/optimization_quality_service.py` | 12-dimension scoring → quality report |
| `services/optimization_simulation_service.py` | Deep-copy scenario simulation |
| `services/optimization_comparison_service.py` | Quality report diff / delta analytics |

**Stable interface:** `observe_optimization_result()` and `build_optimization_report()` are the public entry points for all downstream consumers.

### 2.2 `governance`

**Responsibility:** Authority gate — determines approval state, override safety, escalation paths.

| File | Role |
|------|------|
| `services/optimization_governance_service.py` | `determine_governance_state()` — the single authority on GovernanceState |
| `services/transaction_audit_service.py` | `execute_with_audit()` — mutation + audit + event in one atomic call |
| `services/optimization_trace_service.py` | Wraps analysis outputs into PII-stripped TraceEvent dicts |

**Stable interface:** `determine_governance_state(recheck_summary, quality_report, issues)` returns the authoritative governance decision.

### 2.3 `tracing`

**Responsibility:** Structured, immutable audit records for every optimization decision.

| File | Role |
|------|------|
| `services/optimization_candidate_trace_service.py` | CandidateTrace per accepted/rejected candidate |
| `services/optimization_constraint_trace_service.py` | ConstraintTrace per recheck issue |
| `services/optimization_decision_log_service.py` | DecisionLogEntry per section allocation |
| `policies/optimization_trace_policy.py` | TraceEventType enum, TraceEvent dataclass, strip_pii() |

**Invariant:** All trace objects are frozen dataclasses. PII is always stripped before creation.

### 2.4 `workflow`

**Responsibility:** Edit locks, signing lifecycle, user helpers, workload reporting.

| File | Role |
|------|------|
| `services/workflow_lock_service.py` | TTL-based optimistic edit lock |
| `services/workflow_signing_service.py` | Two-round signing state machine (draft/confirming/confirmed/swap_open/swap_confirming/locked) |
| `services/workflow_user_service.py` | format_user_dict(), build_external_workflow_issues() |
| `services/workflow_reporting_service.py` | build_staff_workload_report() |

**Note:** The signing state machine tracks WHO has signed off. The `schedule_state_machine` (scheduling domain) tracks the SCHEDULE's lifecycle from generation to archival. These are distinct.

### 2.5 `audit`

**Responsibility:** Event emission, event routing, audit trail persistence.

| File | Role |
|------|------|
| `services/audit_service.py` | Semantic audit wrapper: audit_mutation(), audit_export() |
| `services/audit_event_service.py` | Coupled audit + event emission |
| `services/event_service.py` | InMemoryEventBus singleton, emit() |
| `services/event_dispatcher_service.py` | EventDispatcher: type-based routing over the bus |
| `events/domain_event.py` | DomainEvent frozen dataclass |
| `events/base_event.py` | EventDomain, EventSeverity enums |
| `events/audit_events.py` | AuditEventType enum (14 values) |
| `events/governance_events.py` | GovernanceEventType enum (11 values) |
| `events/optimization_events.py` | OptimizationEventType enum (15 values) |
| `event_handlers/` | Typed side-effect consumers (registered on startup) |

**Invariant:** Domain events are emitted AFTER DB commit (best-effort). They never block mutations.

### 2.6 `publication`

**Responsibility:** Publication lifecycle decisions — readiness, risk scoring, rollback safety, override authority.

| File | Role |
|------|------|
| `services/publication_governance_service.py` | Readiness assessment, rollback safety, publish audit payload |

**Stable interface:** `assess_publication_readiness(quality_report, governance, recheck_summary, schedule_state)` is the entry point.

### 2.7 `scheduling`

**Responsibility:** Schedule lifecycle state management — from generation to archival.

| File | Role |
|------|------|
| `services/schedule_state_machine.py` | 9-state lifecycle machine (DRAFT→OPTIMIZED→…→ARCHIVED) |

**Key rule:** No DB calls. Pure logic. Callers own persistence.

### 2.8 `analytics`

**Responsibility:** Read-only historical projection and cross-period comparison.

| File | Role |
|------|------|
| `services/analytics_projection_service.py` | Governance trends, quality trends, overload trends, period comparison |

**Key rule:** Input is pre-loaded dicts (no DB queries inside the service).

---

## 3. Dependency Graph

```
Optimization Sources (generated ExamSchedule ORM objects)
  │
  ▼
[optimization domain]
  pipeline_observer_service
    ├─→ recheck_service         (leaf)
    ├─→ explanation_service     (leaf)
    ├─→ quality_service         (leaf)
    └─→ governance_service      (leaf)
  report_builder
    └─→ pipeline_observer_service
  simulation_service
    └─→ quality_service
  comparison_service
    (pure arithmetic diff)
  │
  ├─→ [tracing domain]
  │     candidate_trace_service
  │     constraint_trace_service
  │     decision_log_service
  │
  ├─→ [governance domain]
  │     optimization_trace_service (wraps observer/recheck/explanation/governance payloads)
  │     transaction_audit_service  (mutations + audit + event)
  │
  └─→ [publication domain]
        publication_governance_service
          (consumes quality_report, governance, recheck_summary)

[workflow domain]
  signing_service   → [audit domain] (emits events)
  lock_service      → [audit domain]

[audit domain]
  event_bus ← all domains emit events here
  event_dispatcher ← routes to [event_handlers]

[analytics domain]
  analytics_projection_service ← consumes pre-loaded report dicts
```

---

## 4. Where New Code Belongs

| Adding a new... | Put it in |
|-----------------|-----------|
| Optimization analyzer (read-only, post-hoc) | `services/optimization_*` — optimization domain |
| Governance gate or override rule | `services/optimization_governance_service.py` or `services/publication_governance_service.py` |
| Audit trace object | `services/optimization_*_trace_service.py` — tracing domain |
| Workflow signing rule | `services/workflow_signing_service.py` — workflow domain |
| Edit lock rule | `services/workflow_lock_service.py` — workflow domain |
| Domain event type | `events/{domain}_events.py` — audit domain |
| Event consumer / side effect | `event_handlers/{domain}_handler.py` — audit domain |
| Publication lifecycle rule | `services/publication_governance_service.py` — publication domain |
| Schedule lifecycle transition | `services/schedule_state_machine.py` — scheduling domain |
| Historical trend analysis | `services/analytics_projection_service.py` — analytics domain |
| API endpoint | `routers/optimize_workflow.py` (workflow/governance) or appropriate domain router |
| TypedDict payload contract | `contracts/{domain}_contracts.py` |

---

## 5. Stability Rules

1. **Optimization services are READ-ONLY.** Never add a write path to any `optimization_*.py` service.
2. **Governance authority is singular.** `determine_governance_state()` is the only place GovernanceState is set. Do not compute governance in routers or report builders.
3. **Events are best-effort.** Never let event emission block a DB commit or raise to the caller.
4. **State machines own no DB.** `schedule_state_machine.py` and `workflow_signing_service.py` return results; callers commit.
5. **Trace objects are immutable.** All trace dataclasses are frozen. Never mutate after creation.
6. **PII is stripped at the tracing boundary.** `strip_pii()` must be called before any trace object enters the audit domain.
