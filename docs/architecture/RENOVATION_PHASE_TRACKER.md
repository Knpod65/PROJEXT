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
| Phase 5 — Test and Delivery Maturity | Complete | 95% | 366 tests passing; CI/CD via GitHub Actions shipped; integration tests still open |
| Phase 6 — Faculty IT / Multi-Faculty Readiness | In progress | 35% | Policy skeleton + feature flag shipped; DB migration and IT approval still open |
| Modernization Sprint (Phases 1–3D) | Complete | 100% | 10 new service files, 10 new test files, 7 new architecture docs, 272 new tests |

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

## 8. Modernization Sprint — New Capabilities (2026-05-14)

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

## 9. Next Actions

1. Wire `UnitOfWork` into highest-value router mutations (start with `optimize_workflow.py` lock acquire/release).
2. Enable `multi_faculty_enabled=True` only after DBA adds `faculty_id` column — follow MULTI_FACULTY_ISOLATION_IMPLEMENTATION_PLAN.md.
3. Extract first service/repository slice from `schedule.py`.
4. Continue `submissions.py` approval/release/print-queue extraction with regression coverage.
5. Start EMS-side auth integration adapter design with Faculty IT.
6. Route-level code splitting for large frontend pages (647 kB bundle).
