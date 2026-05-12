# Ultra Detailed System Audit
## EMS Academic Operations Platform — 2026-05-12

> Branch audited: `main`
> Audit-start head: `c4e864d`
> User-provided last known head: `1d4e78c`
> Scope: backend, frontend, PDPA/security, DevOps, testing, Faculty IT auth alignment

---

## 1. Executive Summary

EMS is a viable long-term Academic Operations Platform on the current FastAPI + React stack. The codebase is already production-shaped in core workflow coverage, but it is not fully production-hardened. The largest remaining risks are architectural concentration in a small number of routers, public data-surface policy decisions, partial PDPA closure, and inconsistent frontend/i18n cleanup.

This pass kept to the requested discipline:
- no Laravel rewrite
- no large router rewrite
- no destructive migration
- only safe, validated fixes

---

## 2. Current Readiness Score

**80 / 100**

### Score by area

| Area | Score | Notes |
|------|------:|------|
| Authentication and authorization | 90 | Good structure, but still split across `auth_utils.py` and `permissions.py` |
| Backend architecture | 76 | Service layer exists; top routers remain too large |
| Frontend DRY and UX | 74 | API layer mostly centralized; i18n and legacy patterns remain uneven |
| PDPA and security | 79 | Strong baseline controls; public exposure and audit/transaction coupling still open |
| DevOps and deployment | 82 | Docker/Nginx are usable; health and env handling improved |
| Testing and delivery | 72 | 94 backend tests, but no CI and limited integration coverage |
| Overall | 80 | Safe for continued controlled single-faculty use, not yet fully hardened |

---

## 3. DRY Maturity Score by Layer

| Layer | Maturity | Notes |
|------|------:|------|
| Backend runtime config | 88 | `settings.py` is canonical; a few env reads remain outside it |
| Backend RBAC / guards | 76 | safer after this pass, but dual ownership still exists |
| Backend service layer | 58 | foundation present, extraction incomplete |
| Backend audit naming / wrappers | 67 | wrappers exist; not all routers use them |
| Frontend API transport | 84 | `services/api.ts` is the dominant path |
| Frontend permissions | 70 | helper layer exists, but hooks/components still bypass it |
| Frontend i18n | 52 | raw JSX strings remain widespread |
| DevOps configuration | 74 | multiple compose modes exist; some knobs were still scattered |

---

## 4. Backend Findings

### A. Auth / permission duplication

Confirmed duplication or drift existed in:
- `backend/auth_utils.py:103` `_coerce_user_role()`
- `backend/permissions.py:45` `get_effective_role()`
- `backend/permissions.py:51` `get_dept_filter()`
- `backend/permissions.py:121` `build_dependencies()`
- `backend/permissions.py:197` `assert_submission_access()`

Why it mattered:
- `permissions.py` previously used base-role semantics in places where `auth_utils.py` used effective-role semantics.
- That creates risk for admin `view_as` sessions and any future multi-role expansion.

Safe fix implemented:
- `permissions.py` now defers effective-role and dept-filter semantics to the canonical auth layer.
- `auth_utils._coerce_user_role()` now routes through `permissions.coerce_user_role()`.

Still open:
- 26 routers still import guard helpers from `auth_utils.py`, so full consolidation is deferred.

### B. Config / constants duplication

Remaining duplicated or scattered config ownership still exists in:
- `backend/database.py`
- `backend/email_notifications.py`
- `backend/cmu_sso.py`

Safe fix implemented:
- centralized additional token/lock timings through:
  - `PDF_TOKEN_EXPIRE_HOURS`
  - `PRINTSHOP_TOKEN_EXPIRE_HOURS`
  - `SUBMISSION_ACCESS_TOKEN_EXPIRE_HOURS`
  - `WORKFLOW_LOCK_TTL_SECONDS`

Deferred:
- faculty labels and signer rules should eventually become DB-backed policy tables

### C. Router fatness / extraction priority

Highest priority routers:
1. `backend/routers/optimize_workflow.py` — 1330 lines
2. `backend/routers/schedule.py` — 1088 lines
3. `backend/routers/documents.py` — 1020 lines
4. `backend/routers/exam_manager.py` — 907 lines
5. `backend/routers/imports.py` — 865 lines
6. `backend/routers/submissions.py` — 858 lines

Recommended extraction targets:
- `optimize_workflow.py`
  - lock lifecycle service
  - workflow state service
  - unavailability service
  - user admin service
- `schedule.py`
  - schedule CRUD service
  - supervision assignment service
  - optimizer orchestration service
- `exam_manager.py`
  - ownership policy helper
  - manager proposal/confirmation service
  - materials request service
- `documents.py`
  - document export orchestrator
  - QR lifecycle policy helper

### D. Audit logging coverage

After this pass, notable states are:

#### Clearly audited
- schedule CRUD and supervision mutations
- submissions lifecycle mutations
- print queue transitions via helper
- print job notes updates
- pickup QR regenerate / confirm
- swaps v1/v2
- user CRUD
- period lifecycle
- PDF token issuance
- submission message creation

#### Not logged or intentionally deferred
- `backend/routers/optimize_workflow.py:1045` `acquire_edit_lock()`
- `backend/routers/optimize_workflow.py:1075` `release_edit_lock()`
- `backend/routers/optimize_workflow.py:1089` `heartbeat_lock()`
- `backend/routers/scheduler.py` internal cron-trigger routes

#### POST but likely “preview/not needed”
- `backend/routers/co_exam.py` `auto_detect_co_exams()`
- `backend/routers/external_exams.py` `preview_auto_assign()`

### E. Transaction boundary risks

High-value risks still present:
- `auth_utils.log_action()` commits separately from many business writes.
- `backend/routers/exam_manager.py:801` `save_materials()` commits twice before audit logging.
- `backend/routers/documents.py` export flow can create/activate QR state while generating documents.

Recommended design:
- service-layer transaction boundary with audit write inside the same unit of work where the audit record is mandatory for compliance

### F. Error / exception consistency

Observed patterns:
- good: `services/exceptions.py` exists
- partial: most routers still raise `HTTPException` directly
- partial: several legacy export/import routers still use broad catches

Examples of broad/generic exception patterns remain in:
- `backend/routers/exports.py`
- `backend/routers/exports_excel.py`
- `backend/routers/imports.py`
- `backend/routers/imports_v2.py`

No mass rewrite was done in this pass.

---

## 5. Frontend Findings

### A. Role / permission duplication

Safe fixes implemented:
- `frontend/src/utils/permissions.ts:115` added `canManageOperationalWork()`
- `frontend/src/pages/Checkins.tsx:78` now uses the helper
- `frontend/src/pages/Schedule.tsx:22` now uses the helper

Remaining direct role branching still exists in active frontend logic:
- `frontend/src/hooks/useSwapsData.ts:147,151,180,184,185,188`
- `frontend/src/pages/ExportCenter.tsx:53`
- `frontend/src/pages/Optimizer.tsx:342`
- `frontend/src/components/swaps/SwapRequestTable.tsx:41,58,105,123`
- `frontend/src/components/swaps/SwapStatsCards.tsx:17,18,19,20,22`

Note:
- `frontend/src/hooks/useUsersData.ts:71-72` direct role comparisons are aggregation/statistics, not access control, but still count as DRY drift.

### B. API / service duplication

Positive finding:
- direct page/component `fetch()` usage is largely absent
- `frontend/src/services/api.ts` is the dominant transport layer

Remaining duplication:
- repeated local loading/error toast patterns across legacy pages such as:
  - `Users.tsx`
  - `Settings.tsx`
  - `Period.tsx`
  - `Swaps.tsx`
  - `PrintReview.tsx`

### C. Form / validation duplication

Examples:
- `frontend/src/pages/Checkins.tsx` manual numeric coercion via `Number(...)`
- `frontend/src/pages/RoomManagementV2.tsx` manual time splitting/parsing
- several pages rely on field-empty checks instead of shared validators

Recommendation:
- add a lightweight shared validation layer before considering a new dependency

### D. UI / table / layout duplication

Positive finding:
- reusable primitives exist (`DataTable`, `Card`, `EmptyState`, `Badge`, `Modal`)

Remaining issues:
- legacy pages still mix old layout patterns and untranslated labels
- the heaviest pages are still large enough to resist reuse:
  - `Checkins.tsx` — 721 lines
  - `MyExam.tsx` — 633 lines
  - `Optimizer.tsx` — 607 lines
  - `RoomManagementV2.tsx` — 604 lines
  - `WorkflowV2.tsx` — 587 lines
  - `External.tsx` — 566 lines

### E. i18n coverage

Raw-string footprint remains high:
- 94 `.tsx` files contain raw Thai JSX strings
- biggest hotspots by raw Thai count:
  - `Checkins.tsx`
  - `Optimizer.tsx`
  - `MyExam.tsx`
  - `WorkflowV2.tsx`
  - `RoomManagementV2.tsx`
  - `External.tsx`

### F. Frontend build / bundle

Validation result:
- build passes
- warning remains: main JS chunk is `647.95 kB`

Low-risk next step:
- route-level code splitting for the heaviest pages first

---

## 6. PDPA / Security Findings

### Data exposure classification

#### Public
- `backend/routers/public.py:250` schedule stats
- `backend/routers/public.py:290` upcoming schedules
- `backend/routers/public.py:330` timeline
- `/health` basic service liveness

#### Authenticated / role-restricted
- student schedule lookup with ownership check:
  - `backend/routers/public.py:145`
- submissions, documents, exports, QR status, print queue, workflow mutations

### Key risks

1. Public upcoming schedule data includes course, date, time, room, and student counts.
2. Student-schedule access still relies on temporary username mapping.
3. Readiness endpoint documentation and runtime access policy are not yet aligned.
4. Audit writes are still not transaction-coupled with business writes in many routers.

### Safe security fixes implemented
- public `/health` no longer returns raw exception text
- print-note audit payloads no longer store raw free text
- PDF token issuance and submission messages now leave audit trails

---

## 7. DevOps Findings

### Positive
- Docker + Nginx stack is viable
- database healthcheck exists
- container app healthcheck now exists
- secrets validation blocks obviously unsafe production boot

### Gaps
- no CI
- no migration framework
- HTTPS block in `nginx.conf` is still commented and deployment-dependent
- log rotation is still external to the app/container docs

### Safe fixes implemented
- `Dockerfile` `HEALTHCHECK`
- env-aware PostgreSQL healthcheck in `docker-compose.yml`
- `.env.example` expanded with additional required production knobs
- `RUNBOOK.md` restore section added

---

## 8. Testing Findings

### Current test count
- Before this pass: 87
- After this pass: 94
- Net new: 7

### New coverage added
- permission guard semantics around effective role vs base admin
- new settings/policy re-exports and positive window assertions

### Biggest remaining coverage gaps
- router integration tests
- public student-schedule ownership tests
- print queue transition tests
- document/export tests
- auth callback / SSO adapter tests

---

## 9. Auth / Laravel Integration Decision

Decision:
- EMS should integrate with Faculty IT auth through a contract and adapter layer.
- EMS should continue issuing its own JWT and HttpOnly cookie.
- EMS should continue owning RBAC and permission decisions.
- Laravel rewrite is not recommended.

See:
- `docs/architecture/FACULTY_IT_AUTH_INTEGRATION_CONTRACT.md`

---

## 10. Remaining Blockers

1. Full permission consolidation is not complete.
2. Largest routers still need service extraction.
3. Public schedule exposure policy is not formally closed.
4. Audit transaction coupling is not solved.
5. CI and integration coverage are not in place.

---

## 11. Safe Fixes Implemented

- permission semantic alignment
- config centralization for token/lock windows
- submission-message audit logging
- PDF token audit logging
- print-note audit payload minimization
- legacy student-schedule route forwarding fix
- sanitized public health errors
- frontend helper reuse for operational-role checks
- Docker healthcheck improvements
- runbook and env documentation updates

---

## 12. Deferred Items

- service extraction for top routers
- readiness endpoint access hardening
- public schedule surface reduction
- swap/checkin object-level guards
- CI and Alembic
- complete i18n migration
- route-level code splitting

---

## 13. Recommended Next 2-Week Sprint

1. Extract `schedule_service.py` and `workflow_lock_service.py`.
2. Introduce transaction-safe audit handling for required compliance events.
3. Close the public schedule exposure decision and implement it.
4. Add CI and 3-4 integration smoke tests.
5. Continue frontend permission and i18n normalization.

---

## 14. Production Go / No-Go

### Go
- continue current single-faculty EMS production operations
- continue hardening on current stack

### No-Go
- no Laravel rewrite
- no broad architectural rewrite inside stabilization work
- no multi-faculty rollout yet
- no retention activation without formal owner approval

---

## 15. Do Not Rewrite to Laravel Rationale

The limiting factor in EMS is not framework capability. The limiting factor is finishing stabilization work on an already-working business platform. Rewriting would reset risk upward and delay hardening on the exact workflows already in production shape.

---

## 16. Exact Files Changed

### Code and config
- `.env.example`
- `Dockerfile`
- `RUNBOOK.md`
- `backend/auth_utils.py`
- `backend/config/policy.py`
- `backend/config/settings.py`
- `backend/main.py`
- `backend/permissions.py`
- `backend/routers/optimize_workflow.py`
- `backend/routers/pdf.py`
- `backend/routers/printing.py`
- `backend/routers/public.py`
- `backend/routers/submissions.py`
- `backend/security.py`
- `backend/tests/test_permissions.py`
- `backend/tests/test_settings.py`
- `docker-compose.yml`
- `frontend/src/pages/Checkins.tsx`
- `frontend/src/pages/Schedule.tsx`
- `frontend/src/utils/permissions.ts`

### Reports and contracts
- `docs/architecture/EMS_COMPLETION_GAP_REPORT.md`
- `docs/architecture/PRODUCTION_HARDENING_FINAL_REPORT.md`
- `docs/architecture/RENOVATION_PHASE_TRACKER.md`
- `docs/architecture/FACULTY_IT_AUTH_INTEGRATION_CONTRACT.md`
- `docs/architecture/ULTRA_DETAILED_SYSTEM_AUDIT.md`

---

## 17. Validation Results

### Baseline
- `git status`: clean
- compile: pass
- `import main`: pass
- tests: pass
- frontend build: pass

### After safe fixes
- backend compile: pass
- `import main`: pass
- backend tests: `94 passed`
- frontend build: pass
- bundle warning still present at `647.95 kB`
