# EMS Completion Gap Report
## Academic Operations Platform — 2026-05-12

> Scope: codebase reality on `main` after the ultra-detailed stabilization pass
> Baseline head at audit start: `c4e864d` (`Finalize EMS production hardening and platform readiness`)
> User-provided last known head: `1d4e78c` (`Add EMS service foundation, health checks, and production hardening report`)

---

## 1. Executive Summary

EMS is no longer a fragile prototype. It is a working FastAPI + React academic operations platform with healthy baseline validation, a growing service layer, typed configuration, and materially improved security posture. It is also not yet fully renovated: the largest remaining risks are still router fatness, public data-surface decisions, transaction/audit coupling, partial PDPA enforcement, and uneven frontend/i18n consistency.

**Current readiness score: 80 / 100**

This is a real improvement from the earlier **75 / 100** user-known state and from the previously documented **78 / 100** internal report state on 2026-05-11.

---

## 2. What Is Complete

### Architecture / governance
- Phase 1 architecture governance is complete.
- EMS remains on the intended stack: React + TypeScript + Vite, FastAPI + SQLAlchemy + Pydantic v2, SQLite dev / PostgreSQL-ready, Docker + Nginx.
- The codebase continues on the existing platform; no Laravel/PHP rewrite is required or recommended.

### DRY configuration foundation
- `backend/config/settings.py` is the canonical typed runtime configuration source.
- `backend/config/policy.py` is functioning as a compatibility re-export layer.
- Token, QR, lock, and print timing values are now more centralized than before:
  - `PDF_TOKEN_EXPIRE_HOURS`
  - `PRINTSHOP_TOKEN_EXPIRE_HOURS`
  - `SUBMISSION_ACCESS_TOKEN_EXPIRE_HOURS`
  - `WORKFLOW_LOCK_TTL_SECONDS`

### Validation baseline
- Backend compile: pass
- Backend `import main`: pass
- Backend tests: `94 passed`
- Frontend build: pass

### Service-layer foundation
- `services/permission_service.py`
- `services/audit_service.py`
- `services/health_service.py`
- `services/submission_service.py`
- `services/exceptions.py`

---

## 3. What Is Partially Complete

### Phase 2 DRY close-out
- Role/permission semantics are still duplicated across `auth_utils.py` and `permissions.py`.
- Some business constants still live outside `config/settings.py`:
  - `backend/database.py`
  - `backend/email_notifications.py`
  - `backend/cmu_sso.py`
- Person-specific and faculty-specific operational rules are env-backed, but still not DB-backed:
  - signer order
  - paper-distribution exclusions
  - faculty labels embedded in export/document code

### Phase 3 service extraction
- The service layer exists, but the top routers are still too large:
  - `backend/routers/optimize_workflow.py` — 1330 lines
  - `backend/routers/schedule.py` — 1088 lines
  - `backend/routers/documents.py` — 1020 lines
  - `backend/routers/exam_manager.py` — 907 lines
  - `backend/routers/imports.py` — 865 lines
  - `backend/routers/submissions.py` — 858 lines

### Frontend DRY / UX
- API transport is mostly centralized through `frontend/src/services/api.ts`.
- Role checks are improved but not fully normalized.
- Raw JSX strings remain widespread; i18n coverage is incomplete in both Thai and English.

---

## 4. Current Gaps by Severity

### Critical
1. `auth_utils.log_action()` still commits in its own transaction path. This means many business writes can succeed even if the audit row fails, and vice versa.
2. Several high-value public endpoints still expose schedule metadata without a final policy decision:
   - `backend/routers/public.py:250`
   - `backend/routers/public.py:290`
3. Router/service boundaries are still weak in the largest operational modules, limiting testability and controlled refactor depth.

### High
1. `backend/routers/optimize_workflow.py` still owns lock state, user CRUD, unavailability, workflow signing, and reporting in one file.
2. `backend/routers/exam_manager.py` still contains object-level permission logic inline instead of a service/policy layer:
   - `_can_manage_section()` at `backend/routers/exam_manager.py:72`
3. `backend/routers/public.py` still uses temporary username-to-student-id ownership mapping:
   - `backend/routers/public.py:145`
4. `frontend/src/hooks/useSwapsData.ts` still contains direct role branching for view shaping:
   - lines 147, 151, 180, 184, 185, 188
5. Frontend production bundle remains large:
   - `647.95 kB` main JS chunk after minification

### Medium
1. `backend/routers/scheduler.py` internal cron endpoints are still not audit-logged.
2. `backend/routers/optimize_workflow.py` lock / unlock / heartbeat events are still not audit-logged.
3. `backend/routers/health.py` readiness logic still documents stricter access semantics than it currently enforces.
4. `frontend/src/pages/Users.tsx`, `Settings.tsx`, `Period.tsx`, `Workflow.tsx`, `Swaps.tsx` are legacy-style pages with raw labels and ad hoc UX patterns.
5. There is still no CI pipeline and no migration framework such as Alembic.

---

## 5. Safe Fixes Implemented in This Pass

- Unified `permissions.py` effective-role and dept-filter behavior with `auth_utils.py`.
- Routed `auth_utils._coerce_user_role()` through `permissions.coerce_user_role()`.
- Centralized more runtime thresholds into settings/policy re-exports.
- Added audit coverage for:
  - submission messages
  - PDF token issuance
- Removed raw free-text print notes from audit payloads; replaced with presence/length metadata.
- Fixed the authenticated legacy student-schedule route forwarding bug in `backend/routers/public.py:324`.
- Sanitized public `/health` failure detail to avoid leaking exception messages.
- Added frontend semantic helper `canManageOperationalWork()` and replaced two direct UI role checks.
- Added Docker `HEALTHCHECK`.
- Fixed PostgreSQL Docker healthcheck to respect environment overrides.
- Updated `.env.example` and `RUNBOOK.md`.
- Added 7 backend tests; total is now `94`.

---

## 6. Remaining Completion Gaps

### Backend architecture
- Extract service modules for:
  - schedule management
  - optimizer session locking and workflow state
  - exam manager ownership / materials
  - document export orchestration
  - print-queue lifecycle

### PDPA / governance
- Decide whether public upcoming schedule data should remain public, be reduced, or require auth.
- Move student ownership lookup off temporary `username == student_id` behavior.
- Add object-level guards for swaps and check-ins, not just role-level guards.
- Replace audit side effects that commit separately from business writes.

### Frontend
- Finish semantic permission migration in hooks/components, not just pages.
- Introduce shared validation helpers for numeric/date/time coercion.
- Continue i18n migration; current raw-string footprint is still broad.
- Add route-level code splitting for the heaviest pages.

### DevOps
- Add CI.
- Add documented restore verification beyond manual curl checks.
- Add explicit production readiness checklist for TLS, secrets rotation, and retention activation.

---

## 7. Recommended Next 2-Week Sprint

### Sprint objective
Close the biggest correctness and governance gaps without rewriting core workflows.

### Work order
1. Extract `schedule_service.py` and `workflow_lock_service.py` from the two largest operational routers.
2. Introduce a transaction-safe audit boundary so business writes and audit writes fail together when required.
3. Decide the public schedule exposure policy and implement the chosen surface reduction.
4. Finish the remaining frontend semantic permission migrations in hooks/components.
5. Add CI + one router integration test slice:
   - health
   - auth/session
   - public student schedule ownership
   - print queue transitions

---

## 8. Go / No-Go

### Go
- Single-faculty continued production use
- Faculty IT auth alignment planning
- Controlled phase-by-phase service extraction

### No-Go
- No Laravel rewrite
- No multi-faculty expansion yet
- No retention cleanup activation without owner sign-off
- No broad public-data expansion without policy approval

---

## 9. No-Laravel-Rewrite Decision

Rewriting EMS to Laravel/PHP is not justified.

Reasons:
- The current codebase already has mature business workflows in FastAPI + React.
- The system has existing RBAC, session, export, QR, workflow, and submission machinery that would be expensive and risky to re-implement.
- Current risk is architectural stabilization, not framework insufficiency.
- Faculty IT auth alignment can be solved with an integration contract and adapter layer, not a platform reset.

---

## 10. Bottom Line

EMS is in the right direction for a long-term Academic Operations Platform. The platform is stable enough to harden, test, and progressively renovate. The fastest path to production confidence is continued targeted extraction and governance cleanup, not rewrite energy.
