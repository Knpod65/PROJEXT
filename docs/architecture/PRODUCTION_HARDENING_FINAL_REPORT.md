# Production Hardening Final Report
## EMS Academic Operations Platform — 2026-05-12 Stabilization Pass

> Branch: `main`
> Audit-start head: `c4e864d`
> Scope: production hardening, DRY audit, PDPA/security review, DevOps verification, small safe fixes only

---

## 1. Outcome

This pass was intentionally not a feature sprint. It was a system inspection and stabilization pass on the current pushed `main` branch. The baseline was green before changes, and the codebase remained green after the safe-fix set.

**Readiness score after this pass: 80 / 100**

> **Updated 2026-05-14:** After the modernization sprint (Phases 1–3D), readiness score is now **90 / 100**.
> See `FINAL_PLATFORM_READINESS_REPORT.md` for the current Go/No-Go assessment.

---

## 2. Validation Results

### Baseline at audit start
- `git status`: clean
- `git log --oneline -8`: latest head was `c4e864d`
- backend compile: pass
- backend `import main`: pass
- backend tests: pass
- frontend build: pass

### Post-fix validation
- backend compile: pass
- backend `import main`: pass
- backend tests: `94 passed`
- frontend build: pass
- bundle warning remains: `647.95 kB` main JS chunk

---

## 3. Safe Fixes Shipped

### Permission / DRY correctness
- `backend/permissions.py`
  - aligned `get_effective_role()`
  - aligned `get_dept_filter()`
  - aligned guard semantics with effective-role behavior
  - aligned `assert_submission_access()` with effective role
- `backend/auth_utils.py`
  - routed `_coerce_user_role()` through `permissions.coerce_user_role()`

### Config centralization
- `backend/config/settings.py`
- `backend/config/policy.py`

Added typed configuration ownership for:
- `PDF_TOKEN_EXPIRE_HOURS`
- `PRINTSHOP_TOKEN_EXPIRE_HOURS`
- `SUBMISSION_ACCESS_TOKEN_EXPIRE_HOURS`
- `WORKFLOW_LOCK_TTL_SECONDS`

### Audit / PDPA improvements
- `backend/routers/submissions.py`
  - `send_message()` now produces an audit row without logging raw message text
- `backend/routers/pdf.py`
  - PDF token issuance is now audited
- `backend/routers/printing.py`
  - print note audit payloads now store presence/length metadata instead of raw note bodies

### Security / correctness
- `backend/routers/public.py`
  - fixed authenticated legacy route forwarding for student schedule lookup
- `backend/main.py`
  - sanitized `/health` failure detail to exception class name only
- `backend/security.py`
  - session cookie lifetime now follows centralized settings
  - cookie clear path now mirrors secure flag behavior

### Frontend DRY
- `frontend/src/utils/permissions.ts`
  - added `canManageOperationalWork()`
- `frontend/src/pages/Checkins.tsx`
- `frontend/src/pages/Schedule.tsx`
  - removed direct `admin || staff` permission branching

### DevOps
- `Dockerfile`
  - added container healthcheck
- `docker-compose.yml`
  - PostgreSQL healthcheck now honors env overrides
- `.env.example`
  - expanded required production knobs
- `RUNBOOK.md`
  - corrected student schedule auth documentation
  - added restore procedure notes

### Tests
- Added 7 backend tests across:
  - `backend/tests/test_permissions.py`
  - `backend/tests/test_settings.py`
- Added targeted submission extraction tests in:
  - `backend/tests/test_submission_architecture.py`

---

## 4. Key Findings Not Fixed Here

### Backend
- `backend/routers/optimize_workflow.py` is still the largest operational risk due to scope and line count.
- `backend/routers/schedule.py` is now the next router recommended for service extraction.
- `backend/routers/exam_manager.py` still mixes policy, query, and workflow logic.
- `backend/routers/submissions.py` now has a safe extraction foundation, but upload/approval/release mutations are still router-heavy.
- `auth_utils.log_action()` still commits independently from many business writes.

### Frontend
- Inline role logic still exists in:
  - `frontend/src/hooks/useSwapsData.ts`
  - `frontend/src/pages/ExportCenter.tsx`
  - `frontend/src/pages/Optimizer.tsx`
  - `frontend/src/components/swaps/SwapRequestTable.tsx`
  - `frontend/src/components/swaps/SwapStatsCards.tsx`
- Raw JSX strings remain widespread; i18n is not yet complete.

### Security / PDPA
- Public schedule-facing endpoints still require a policy decision on exposure depth.
- Student ownership lookup still relies on temporary username mapping.
- Lock-state and cron-trigger mutations still lack audit logging.

### DevOps
- No CI
- No migration framework
- No final retention activation

---

## 5. Production Recommendation

### Go
- Continue current single-faculty EMS operations
- Continue controlled hardening on the current stack
- Proceed with Faculty IT auth contract alignment

### No-Go
- No Laravel rewrite
- No large router rewrite inside a stabilization pass
- No multi-faculty rollout yet
- No public-data scope expansion yet

---

## 6. Recommended Next Sprint

1. Extract the first service/repository slice from `schedule.py`.
2. Continue `submissions.py` extraction for approval/release/print-queue mutations.
3. Extract lock/workflow state from `optimize_workflow.py`.
4. Implement transaction-safe audit strategy.
5. Decide and enforce public schedule data exposure policy.
6. Add CI + router integration tests.
