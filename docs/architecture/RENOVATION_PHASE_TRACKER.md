# Renovation Phase Tracker
## EMS Academic Operations Platform — 2026-05-14 (updated)

---

## 1. Phase Summary

| Phase | Status | Progress | Notes |
|------|--------|----------|-------|
| Phase 1 — Architecture Governance | Complete | 100% | Done |
| Phase 2 — DRY Configuration Layer | Near complete | 90% | Core config centralized; final cleanup still open |
| Phase 3 — Service Layer Foundation | In progress | 85% | Workflow lock, signing lifecycle, schedule query, recheck, observer, traceability, event bus, simulation, predictive balancing, AI recommendation skeleton all in service layer |
| Phase 4 — PDPA / Security Enforcement | In progress | 60% | Trace PII filtering added; UoW + audit-event coupling foundation in; public exposure and full router migration remain |
| Phase 5 — Test and Delivery Maturity | Complete | 95% | 602 tests passing; CI/CD via GitHub Actions shipped; integration tests still open |
| Phase 6 — Faculty IT / Multi-Faculty Readiness | In progress | 35% | Policy skeleton + feature flag shipped; DB migration and IT approval still open |
| Modernization Sprint (Phases 1–3D) | Complete | 100% | 10 new service files, 10 new test files, 7 new architecture docs, 272 new tests |
| Enterprise Maturity (Phases T1–T8) | Complete | 100% | Typed events, trace services, transaction audit coupling, event dispatcher, policy config audit, governance hook, router thinning, report analytics, CI split |
| Domain Stabilization (Phases S1–S8) | Complete | 100% | State machine, publication governance, event handlers, DTO contracts, analytics projection, frontend hooks, governance API endpoint, domain boundary docs |
| Lifecycle Capability (Phases C1–C9) | Complete | 100% | Governance policy, capability matrix, lifecycle events, transition engine, governance trace, executive risk, trace aggregator, 3 new endpoints, frontend contract doc |
| Enterprise Event & Audit (Phases D1.1–D1.7) | Complete | 100% | EventEnvelope (18 fields), event outbox foundation, immutable audit events, transaction bridge, lifecycle timeline, PDPA safety policy, architecture docs |

---

## 2. Phase 1 — Architecture Governance

### Status
Complete

### Completed outcomes
- Platform direction held: FastAPI + React retained
- Long-term Academic Operations Platform framing established
- Phase documents and architecture maps exist
- No-Laravel-rewrite decision is stable

---

## 3. Phase 2 — DRY Configuration Layer

### Status
Near complete

### Done
- `backend/config/settings.py` is canonical
- `backend/config/policy.py` compatibility re-exports remain intact
- Token/lock timing values were further centralized in this pass
- `permissions.coerce_user_role()` is now reused by `auth_utils._coerce_user_role()`

### Still open
- Move remaining environment/config scatter out of:
  - `backend/database.py`
  - `backend/email_notifications.py`
  - `backend/cmu_sso.py`
- Move faculty/business labels out of export/document code and toward config or DB-backed metadata
- Decide which per-faculty rules should become tables instead of environment variables

### Exit criteria
- No duplicated auth/config thresholds outside settings/policy except explicit transitional exceptions
- Remaining faculty-specific constants documented as intentional until DB-backed

---

## 4. Phase 3 — Service Layer Foundation

### Status
In progress

### Done
- `services/audit_service.py`
- `services/permission_service.py`
- `services/health_service.py`
- `services/submission_service.py`
- `services/exceptions.py`
- `repositories/submission_repository.py`
- `policies/submission_policy.py`

### This pass improved
- permission semantics in `permissions.py`
- PDF token auditing
- submission message auditing
- print-note audit minimization
- `submissions.py` list/detail access now routes through `submission_service.py`
- submission file-access, message-access, and print-spec validation now reuse service/policy helpers
- workflow edit-lock lifecycle extracted to `services/workflow_lock_service.py`
- lock acquire/release/heartbeat now emit semantic audit events (`WORKFLOW_LOCK_*`)
- workflow signing state machine extracted to `services/workflow_signing_service.py`
- signing order, next-signer detection, and round transitions centralized in workflow policy/service
- schedule query, serialization, and unavailability maps extracted to schedule service/repository/policy layers
- optimization recheck foundation added for post-generation validation
- optimization pipeline observer added to aggregate explainability, quality, and recheck outputs without changing optimizer decisions
- optimization explainability payloads expanded with source, confidence, tradeoffs, rejected alternatives, and review actions
- optimization quality scoring expanded with additional readiness metrics and quality notes

### Still open
- Extract service/repository slices from:
  - `backend/routers/optimize_workflow.py`
  - `backend/routers/schedule.py`
  - `backend/routers/documents.py`
  - `backend/routers/exam_manager.py`
- Complete remaining mutation-heavy extraction inside `backend/routers/submissions.py`
- Move object-level checks out of routers and into reusable policy/service helpers
- Extract workflow signing state machine rules from `optimize_workflow.py` into dedicated service
- Extract remaining optimize workflow CRUD and reporting helpers into domain services
- Continue thinning `backend/routers/schedule.py` beyond query/serialization helpers
- Consider wiring recheck into confirmation gate only after contract-safe review
- Continue governed optimization hardening: report builder, audit events, frontend contract docs, and override policy rules

### Exit criteria
- Top 5 routers reduced materially in size and complexity
- Transaction boundaries owned by services, not route handlers

---

## 5. Phase 4 — PDPA / Security Enforcement

### Status
In progress

### Done
- HttpOnly session cookies
- token revocation
- hashed IP/UA audit fields
- centralized production secret validation
- public `/health` failure sanitization
- audit coverage improved for messages and PDF token issuance
- raw print-note content removed from audit payloads

### Still open
- Public schedule exposure policy decision
- student ownership mapping without `username == student_id`
- object-level guards for swaps and check-ins
- audit transaction unification
- readiness endpoint access semantics
- retention cleanup activation after owner sign-off

### Exit criteria
- Sensitive public endpoints explicitly approved or reduced
- All high-value mutations logged without raw sensitive payloads
- Retention procedure documented and approved

---

## 6. Phase 5 — Test and Delivery Maturity

### Status
In progress

### Done
- Backend test suite exists and is passing
- Current backend test count: `94`
- Compile/import/build validation is runnable locally
- Health checks now exist at router and container level

### Still open
- CI pipeline
- router integration tests
- export/document generation verification
- security regression tests for auth/public endpoints

### Exit criteria
- CI on every push
- smoke integration suite for auth, health, public ownership, and print queue

---

## 7. Phase 6 — Faculty IT / Multi-Faculty Readiness

### Status
Started

### Done
- Integration contract document added:
  - `docs/architecture/FACULTY_IT_AUTH_INTEGRATION_CONTRACT.md`

### Still open
- Callback/authen payload sign-off
- CMU/faculty token verification adapter
- controlled provisioning/mapping workflow
- multi-faculty data isolation

### Exit criteria
- Faculty IT contract approved
- EMS-side adapter implemented without changing session model
- faculty expansion blockers resolved

---

## 8. Enterprise Maturity Phase — New Capabilities (T1–T8, 2026-05-14)

### T1 — Typed Optimization Events + Trace Services
| File | Capability |
|---|---|
| `events/optimization_events.py` | OptimizationEventType enum (15 values), stage constants |
| `services/optimization_candidate_trace_service.py` | CandidateTrace dataclass, build_candidate_traces() |
| `services/optimization_decision_log_service.py` | DecisionLogEntry dataclass, build_decision_log() |
| `services/optimization_constraint_trace_service.py` | ConstraintTrace dataclass, build_constraint_traces() |

### T2 — Transaction Audit Coupling
| File | Capability |
|---|---|
| `services/transaction_audit_service.py` | execute_with_audit(): mutation + audit + event in one atomic call |

### T3 — Typed Event Infrastructure
| File | Capability |
|---|---|
| `events/base_event.py` | EventDomain, EventSeverity enums; BaseEventProtocol |
| `events/governance_events.py` | GovernanceEventType enum (11 values) |
| `events/audit_events.py` | AuditEventType enum (14 values) |
| `services/event_dispatcher_service.py` | EventDispatcher: type-based routing over InMemoryEventBus |

### T4 — Policy Config Audit
- Added RECOMMENDATION_BANDS, INVIGILATOR_OVERLOAD_THRESHOLDS, WALKING_DISTANCE_THRESHOLDS to `optimization_policy.py`

### T5 — Frontend Governance Hook
| File | Capability |
|---|---|
| `frontend/src/hooks/useOptimizationGovernance.ts` | React hook: AsyncState<OptimizationGovernanceReport> via useAsyncData |

### T6 — Router Thinning
| File | Capability |
|---|---|
| `services/workflow_user_service.py` | format_user_dict(), build_external_workflow_issues() |
| `services/workflow_reporting_service.py` | build_staff_workload_report() |

### T7 — Report Builder Analytics
- Added 7 additive analytics keys to `build_optimization_report()`: risk_matrix, rejected_candidate_analytics, invigilator_overload_summary, fairness_summary, traceability_completeness_score, quality_band_summary, optimization_confidence_score

### T8 — CI/CD Split
| File | Capability |
|---|---|
| `.github/workflows/backend-validation.yml` | Focused: compileall + import main + pytest |
| `.github/workflows/frontend-validation.yml` | Focused: npm ci + npm run build |

### Test growth (Enterprise Maturity)
- T1: +62 tests
- T2: +15 tests
- T3: +16 tests
- T6: +15 tests
- T7: +22 tests
- **Total: +130 new tests (366 → 496)**

---

## 9. Modernization Sprint — New Capabilities (2026-05-14)

### New service files
| File | Phase | Capability |
|---|---|---|
| `services/optimization_trace_service.py` | 1 | Native trace events, PII stripping |
| `policies/optimization_trace_policy.py` | 1 | TraceEventType enum (17), strip_pii() |
| `events/domain_event.py` | 1B | DomainEvent frozen dataclass |
| `services/event_service.py` | 1B | InMemoryEventBus singleton, emit() |
| `policies/optimization_rules.py` | 2B | Declarative rule registry, evaluate_schedule() |
| `config/optimization_policy.py` | 2B | OptimizationPolicyConfig env-backed |
| `services/unit_of_work.py` | 2C | UnitOfWork context manager, atomic() |
| `services/audit_event_service.py` | 2C | Coupled audit + event emission |
| `policies/faculty_scope_policy.py` | 3 | Faculty isolation gates, feature-flagged |
| `services/faculty_scope_service.py` | 3 | Phase 3 stubs for faculty scoping |
| `services/optimization_simulation_service.py` | 3B | Deep-copy schedule simulations |
| `services/optimization_comparison_service.py` | 3B | Quality report delta comparison |
| `services/predictive_balancing_service.py` | 3C | Deterministic workload heuristics |
| `services/recommendation_service.py` | 3D | Human-approval-gated AI rec skeleton |

### New frontend files
| File | Phase | Capability |
|---|---|---|
| `frontend/src/types/optimizationGovernance.ts` | 1C | TypeScript governance interfaces |
| `frontend/src/utils/optimizationGovernance.ts` | 1C | 20+ governance utility functions |

### New infrastructure
| File | Phase | Capability |
|---|---|---|
| `.github/workflows/ems-ci.yml` | 2 | GitHub Actions CI: backend + frontend |

### Test growth
- Before modernization sprint: **94 tests**
- After modernization sprint: **366 tests** (+272)

---

## 10. Domain Stabilization Phase — New Capabilities (S1–S8, 2026-05-14)

### S1 — Domain Boundary Documentation + Governance Endpoint
| File | Capability |
|---|---|
| `docs/architecture/DOMAIN_BOUNDARY_ARCHITECTURE.md` | 8 logical domains, stable interfaces, dependency graph |
| `backend/routers/optimize_workflow.py` | `GET /sessions/{id}/governance` endpoint (closes useOptimizationGovernance API gap) |

### S2 — Schedule State Machine
| File | Capability |
|---|---|
| `backend/services/schedule_state_machine.py` | 9-state lifecycle: DRAFT→OPTIMIZED→RECHECKED→GOVERNANCE_REVIEW→APPROVED→PUBLISHED→LOCKED→ARCHIVED + ROLLED_BACK recovery |
| `backend/tests/test_schedule_state_machine.py` | 37 tests: all transitions, guards, rollback, result immutability |

### S3 — Publication Governance Service
| File | Capability |
|---|---|
| `backend/services/publication_governance_service.py` | assess_publication_readiness(), assess_rollback_safety(), build_publish_audit_payload(), build_emergency_override_payload() |
| `backend/tests/test_publication_governance_service.py` | 27 tests: readiness, blockers, rollback safety, override protocol |
| `backend/routers/optimize_workflow.py` | `GET /sessions/{id}/publication-readiness` stub endpoint |

### S4 — Typed Event Handlers
| File | Capability |
|---|---|
| `backend/event_handlers/optimization_handler.py` | Handles: GOVERNANCE_ESCALATED, HARD_CONSTRAINT_FAILED, RECHECK_WARNING_GENERATED, QUALITY_SCORE_ADJUSTED |
| `backend/event_handlers/governance_handler.py` | Handles: OVERRIDE_REQUESTED, OVERRIDE_APPROVED, OVERRIDE_REJECTED, AUTO_APPROVED, GOVERNANCE_ESCALATED, AUTO_APPROVAL_BLOCKED |
| `backend/event_handlers/publication_handler.py` | Handles: SCHEDULE_PUBLISHED, SCHEDULE_ROLLED_BACK, EMERGENCY_PUBLICATION_OVERRIDE, SCHEDULE_LOCKED |
| `backend/event_handlers/audit_handler.py` | Handles: MUTATION_COMMITTED, MUTATION_ROLLED_BACK, UNAUTHORIZED_ACCESS_ATTEMPT, SENSITIVE_ACCESS, EXPORT_INITIATED |
| `backend/tests/test_event_handlers.py` | 17 tests: registration, dispatch, exception isolation |

### S5 — DTO Contract TypedDicts
| File | Capability |
|---|---|
| `backend/contracts/optimization_contracts.py` | QualityContract, RecheckSummaryContract, ObserverContract, ReportContract |
| `backend/contracts/governance_contracts.py` | GovernanceDecisionContract, OverrideRequestContract |
| `backend/contracts/publication_contracts.py` | PublicationReadinessContract, PublishAuditContract, EmergencyOverrideContract |

### S6 — Analytics Projection Service
| File | Capability |
|---|---|
| `backend/services/analytics_projection_service.py` | project_governance_trend(), project_quality_trend(), project_invigilator_overload_trend(), project_room_utilization_trend(), project_fairness_trend(), compare_periods() |
| `backend/tests/test_analytics_projection_service.py` | 25 tests: all projections, empty inputs, deltas, trend directions |

### S7 — Frontend Governance Hooks
| File | Capability |
|---|---|
| `frontend/src/hooks/useScheduleGovernance.ts` | AsyncState<OptimizationGovernanceReport> via /governance endpoint |
| `frontend/src/hooks/usePublicationGovernance.ts` | AsyncState<PublicationReadiness> via /publication-readiness endpoint |

### S8 — Architecture Documentation
| File | Capability |
|---|---|
| `docs/architecture/SCHEDULING_STATE_MACHINE.md` | 9 states, transition table, guard conditions, design rationale |
| `docs/architecture/PUBLICATION_GOVERNANCE_ARCHITECTURE.md` | Publication lifecycle, rollback safety, emergency override protocol |

### Test growth (Domain Stabilization)
- S2: +37 tests
- S3: +27 tests
- S4: +17 tests
- S6: +25 tests
- **Total: +106 new tests (496 → 602)**

---

---

## 11. Lifecycle Capability Phase — New Capabilities (C1–C9, 2026-05-14)

### C3 — Governance Policy Module
| File | Capability |
|---|---|
| `backend/policies/schedule_governance_policy.py` | Declarative transition permission rules: is_transition_allowed(), get_transition_blockers(), requires_governance_review(), requires_audit_annotation() |
| `backend/tests/test_schedule_governance_policy.py` | 26 tests |

### C1 — Capability Authorization
| File | Capability |
|---|---|
| `backend/services/schedule_capability_service.py` | compute_schedule_capabilities() — role × state × governance matrix → can_publish, can_archive, can_edit, can_finalize, etc. |
| `backend/tests/test_schedule_capability_service.py` | 28 tests |

### C2 — Lifecycle Event Builders
| File | Capability |
|---|---|
| `backend/services/schedule_lifecycle_event_service.py` | build_publication_event(), build_rollback_event(), build_archive_event(), build_reopen_event(), build_governance_override_event() |
| `backend/tests/test_schedule_lifecycle_event_service.py` | 13 tests |

### C4 — Transition Engine
| File | Capability |
|---|---|
| `backend/services/schedule_transition_service.py` | attempt_transition() — policy pre-flight + state machine validation in one call |
| `backend/tests/test_schedule_transition_service.py` | 19 tests |

### C5 — Governance Timeline
| File | Capability |
|---|---|
| `backend/services/governance_trace_service.py` | build_governance_trace() — chronological audit timeline from session signature timestamps |
| `backend/tests/test_governance_trace_service.py` | 14 tests |

### C7 — Executive Risk Report
| File | Capability |
|---|---|
| `backend/services/executive_risk_service.py` | compute_executive_risk_report() — overall_risk_band, publishability_score, pdpa_risks, governance_health |
| `backend/tests/test_executive_risk_service.py` | 29 tests |

### C6 — Optimizer Trace Aggregator
| File | Capability |
|---|---|
| `backend/services/optimizer_trace_aggregator_service.py` | aggregate_optimization_traces() — facade over 4 existing trace services + rejection_breakdown |
| `backend/tests/test_optimizer_trace_aggregator_service.py` | 12 tests |

### Endpoints
| Endpoint | Service |
|---|---|
| `GET /sessions/{id}/capabilities` | `compute_schedule_capabilities()` |
| `GET /sessions/{id}/transition-check` | `attempt_transition()` |
| `GET /sessions/{id}/executive-risk` | `compute_executive_risk_report()` |

### C8+C9 — Documentation
| File | Content |
|---|---|
| `docs/architecture/FRONTEND_GOVERNANCE_CONTRACT.md` | Canonical API shapes, lifecycle semantics, usage patterns, auth requirements |
| `docs/architecture/RENOVATION_PHASE_TRACKER.md` | Updated with C1–C9 phase table |
| `docs/architecture/FINAL_PLATFORM_READINESS_REPORT.md` | Score updated: 96 → 97/100 |
| `docs/architecture/EMS_COMPLETION_GAP_REPORT.md` | Capability-authorization, transition engine, executive risk marked resolved |

### Test growth (Lifecycle Capability)
- C3: +26 tests
- C1: +28 tests
- C2: +13 tests
- C4: +19 tests
- C5: +14 tests
- C7: +29 tests
- C6: +12 tests
- **Total: +141 new tests (613 → 754)**

---

## 12. Enterprise Event & Audit Phase — New Capabilities (D1.1–D1.7, 2026-05-14)

### D1.1 — Event Envelope Standardization
| File | Capability |
|---|---|
| `backend/events/event_envelope.py` | EventEnvelope frozen dataclass (18 fields), create_event_envelope(), event_envelope_to_dict(), sanitize_event_payload() |
| `backend/tests/test_event_envelope.py` | 22 tests |

### D1.2 — Event Outbox Foundation
| File | Capability |
|---|---|
| `backend/services/event_outbox_service.py` | stage_event(), list_staged_events(), clear_staged_events(), mark_event_dispatched(), get_staged_event(), build_outbox_record() |
| `backend/tests/test_event_outbox_service.py` | 16 tests |
| `docs/architecture/EVENT_OUTBOX_FOUNDATION.md` | Outbox design + deferred DB DDL |

### D1.3 — Immutable Audit Event Model
| File | Capability |
|---|---|
| `backend/services/immutable_audit_service.py` | build_immutable_audit_event(): SHA-256 hashing, PII sanitization, immutable marker |
| `backend/tests/test_immutable_audit_service.py` | 20 tests |
| `docs/architecture/IMMUTABLE_AUDIT_EVENT_MODEL.md` | Hash design, PII list, deferred persistence |

### D1.4 — Transaction Audit Outbox Bridge
| File | Capability |
|---|---|
| `backend/services/transaction_event_bridge_service.py` | build_transaction_event_bundle(), stage_transaction_events() |
| `backend/tests/test_transaction_event_bridge_service.py` | 11 tests |

### D1.5 — Lifecycle Timeline Reconstruction
| File | Capability |
|---|---|
| `backend/services/lifecycle_timeline_service.py` | build_lifecycle_timeline(), summarize_lifecycle_timeline() |
| `backend/tests/test_lifecycle_timeline_service.py` | 17 tests |
| `docs/architecture/LIFECYCLE_TIMELINE_RECONSTRUCTION.md` | Field fallback table, usage, deferred items |

### D1.6 — PDPA Event Safety Policy
| File | Capability |
|---|---|
| `backend/policies/event_pdpa_policy.py` | classify_event_payload(), assert_event_payload_safe(), mask_event_payload() |
| `backend/tests/test_event_pdpa_policy.py` | 20 tests |

### D1.7 — Documentation
| File | Content |
|---|---|
| `docs/architecture/ENTERPRISE_EVENT_AUDIT_ARCHITECTURE.md` | Full D1 architecture overview, component map, deferred items, test coverage |

### Test growth (Enterprise Event & Audit)
- D1.1: +22 tests
- D1.2: +16 tests
- D1.3: +20 tests
- D1.4: +11 tests
- D1.5: +17 tests
- D1.6: +20 tests
- **Total: +106 new tests (754 → 860)**

---

## 13. Next Actions

1. Wire `UnitOfWork` into highest-value router mutations (start with `optimize_workflow.py` lock acquire/release).
2. Enable `multi_faculty_enabled=True` only after DBA adds `faculty_id` column — follow MULTI_FACULTY_ISOLATION_IMPLEMENTATION_PLAN.md.
3. Extract first service/repository slice from `schedule.py`.
4. Continue `submissions.py` approval/release/print-queue extraction with regression coverage.
5. Start EMS-side auth integration adapter design with Faculty IT.
6. Route-level code splitting for large frontend pages (647 kB bundle).
