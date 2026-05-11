# Renovation Phase Tracker
## EMS Architecture Renovation — Living Project Management Document

> **Audience:** Tech leads, project managers, all engineers
> **Scope:** Phase status, quick wins, risk register, architecture metrics
> **Last updated:** 2026-05-11 (Phase 2 second slice)
> **Update this file** whenever a phase, task, or quick win changes status

---

## Phase Status Overview

| # | Phase | Status | Owner | % Done | Target |
|---|-------|--------|-------|--------|--------|
| 1 | Architecture Mapping & Governance | ✅ Complete (Approval Pending) | — | 100% | 2026-05-11 |
| 2 | DRY Configuration Layer | 🟡 In Progress | — | 60% | 2026-06-08 |
| 3 | Service Layer Renovation | ⬜ Not Started | — | 0% | 2026-07-06 |
| 4 | PDPA & Security Enforcement | ⬜ Not Started | — | 0% | 2026-07-20 |
| 5 | Operational Intelligence | ⬜ Not Started | — | 0% | 2026-08-10 |
| 6 | Multi-Faculty Architecture | ⬜ Not Started | — | 0% | 2026-09-07 |

**Phase 1 is 100% done** (subject to approval completion). Deliverables:
- ✅ 11 core architecture documents (comprehensive governance baseline)
- ✅ Production permissions startup defect fixed and validated (no NotImplementedError at runtime)
- ✅ 7 concrete Phase 1 artifact maps (route/page/role/data/audit/import/faculty scoping)
- ✅ 3 final planning documents (settings map, frontend cleanup plan, approval checklist)
- ⏳ Pending: Team lead sign-offs and compliance/PDPA approvals on security documents

---

## Phase 1 — Architecture Mapping & Governance

**Goal:** Produce the 11 architecture documents and fix two critical structural bugs.
**Effort:** 2 engineers, 2 weeks
**Dependencies:** None (baseline phase)

### Documentation Tasks
| Task | Status |
|------|--------|
| Create `docs/architecture/` directory | ✅ Done |
| Write `EMS_ARCHITECTURE_MAP.md` | ✅ Done |
| Write `DOMAIN_BOUNDARY_MAP.md` | ✅ Done |
| Write `SERVICE_LAYER_PLAN.md` | ✅ Done |
| Write `POLICY_AND_PDPA_ENFORCEMENT.md` | ✅ Done |
| Write `OPERATIONAL_INTELLIGENCE_ROADMAP.md` | ✅ Done |
| Write `MULTI_FACULTY_ARCHITECTURE.md` | ✅ Done |
| Write `WORKFLOW_STATE_MACHINE.md` | ✅ Done |
| Write `AUDIT_AND_EVENT_MODEL.md` | ✅ Done |
| Write `IMPORT_EXPORT_GOVERNANCE.md` | ✅ Done |
| Write `UI_SYSTEM_AND_ROLE_THEME_GUIDE.md` | ✅ Done |
| Write `RENOVATION_PHASE_TRACKER.md` | ✅ Done |
| Create `phase1_artifacts/ROUTE_OWNERSHIP_MAP.md` | ✅ Done |
| Create `phase1_artifacts/PAGE_OWNERSHIP_MAP.md` | ✅ Done |
| Create `phase1_artifacts/ROLE_PERMISSION_MATRIX.md` | ✅ Done |
| Create `phase1_artifacts/SENSITIVE_DATA_EXPOSURE_MAP.md` | ✅ Done |
| Create `phase1_artifacts/AUDIT_EVENT_COVERAGE_TABLE.md` | ✅ Done |
| Create `phase1_artifacts/IMPORT_EXPORT_LINEAGE_MAP.md` | ✅ Done |
| Create `phase1_artifacts/FACULTY_SCOPING_MAP.md` | ✅ Done |
| Create `phase1_artifacts/SETTINGS_CENTRALIZATION_MAP.md` | ✅ Done |
| Create `phase1_artifacts/FRONTEND_ROLE_EXTRACTION_CLEANUP_PLAN.md` | ✅ Done |
| Create `phase1_artifacts/PHASE1_APPROVAL_CHECKLIST.md` | ✅ Done |

### Critical Code Fixes (still pending)
| Task | Status | File | Effort |
|------|--------|------|--------|
| Add `permissions.build_dependencies()` to `main.py` lifespan | ✅ Done | `backend/main.py` | 30 min |
| Create `backend/config/settings.py` (typed Settings dataclass) | ✅ Done | `backend/config/settings.py` | — |
| Replace 3 role extraction chains with `getEffectiveRole(user)` | ✅ Done | `Checkins.tsx:77`, `Schedule.tsx:21`, `ExportCenter.tsx:51` | 1 hour |
| Centralize hardcoded policy constants | ✅ Done | `backend/config/policy.py` | 1–2 hours |
| Centralize export period resolution | ✅ Done | `backend/config/periods.py` | 1 hour |
| Add audit action constants for common auth/export events | ✅ Done | `backend/config/audit_actions.py` | 1 hour |

### Success Criteria for Phase 1 Completion
- [x] All 11 documents created and comprehensive (see docs/architecture/)
- [x] `permissions.build_dependencies()` is called in lifespan — confirmed by smoke tests
- [x] 7 concrete artifact maps created and indexed (see docs/architecture/phase1_artifacts/)
- [x] 3 final planning documents created (settings map, frontend cleanup, approval checklist)
- [ ] All artifacts reviewed and approved by team leads (approval in progress)
- [ ] PDPA/Compliance sign-offs on security docs (approval in progress)
- [ ] Phase 2 backlog confirmed and capacity assigned (pending approval closure)

---

## Phase 2 — DRY Configuration Layer

**Goal:** Eliminate all hardcoded constants, magic strings, and duplicated validation patterns.
**Effort:** 1–2 engineers, 2 weeks
**Dependencies:** Phase 1 (`settings.py` must exist)

### Tasks
| Task | Status | File | Notes |
|------|--------|------|-------|
| Move print priority thresholds to `config/settings.py` | ✅ | `config/settings.py` | Settings.print_priority_*_threshold fields |
| Add `SupervisionRole` enum to `models.py` | ✅ | `models.py` | supervisor/chief/distributor/room_keeper |
| Add `coerce_user_role()` public function to `permissions.py` | ✅ | `permissions.py` | Returns UserRole\|None, replaces try/except |
| Replace 3+ inline `try: models.UserRole(...)` blocks | ✅ | `optimize_workflow.py` (3 sites) | Uses permissions.coerce_user_role() |
| Move `PAPER_DISTRIBUTION_EXCLUDED_USERNAMES` to DB config | ⬜ | `staff_workloads.py:15-16` | `StaffExclusionRule` table (Phase 6 prereq) |
| Move `SIGN_ORDER_USERNAMES` to `WorkflowSignerConfig` table | ⬜ | `auth_utils.py:473` | Phase 6 prereq; keep fallback during transition |
| Centralize export period resolver | ✅ | `backend/config/periods.py`, `exports.py`, `exports_excel.py`, `pdf.py` | `resolve_export_period()` function |
| Fix `useAsyncData.ts:25` hardcoded Thai string | ⬜ | `frontend/src/hooks/useAsyncData.ts` | Use `t("errors.generic")` or caller param |
| Remove duplicate `require_admin`/`get_dept_filter` from `auth_utils.py` | ⬜ | `auth_utils.py:264-332` | Consolidate to `permissions.py` |

### Success Criteria
- `grep -r '"distributor"' backend/routers/` → 0 results
- `grep -r 'students >= 120' backend/` → 0 results
- `grep -r 'models.UserRole(' backend/routers/` → 0 results
- `grep -r '"เกิดข้อผิดพลาด"' frontend/src/` → 0 results
- `grep -r '_resolve_period' backend/routers/` → 0 results (only in term_lifecycle.py)
 - `python -m py_compile` passes for touched backend files
 - `npm run build` passes for the frontend pages touched by role extraction cleanup

---

## Phase 3 — Service Layer Renovation

**Goal:** Extract all business logic from route handlers into dedicated service modules.
**Effort:** 2 engineers, 4 weeks
**Dependencies:** Phase 1 (exceptions.py), Phase 2 (coerce_user_role, settings.py)

### Files to Create
| File | Source | Lines to Extract | Priority |
|------|--------|-----------------|---------|
| `backend/services/__init__.py` | New | — | Week 1 |
| `backend/services/exceptions.py` | New | — | Week 1 |
| `backend/services/submission_service.py` | `submissions.py` helpers | ~120 lines | Week 2 |
| `backend/services/schedule_service.py` | `schedule.py` helpers (non-optimizer) | ~200 lines | Week 3 |
| `backend/services/period_service.py` | `term_lifecycle.py` wrapper | ~30 lines | Week 3 |
| `backend/services/user_service.py` | `optimize_workflow.py` user section | ~100 lines | Week 4 |
| `backend/services/audit_service.py` | `auth_utils.log_action` wrapper | ~80 lines | Week 4 |
| `backend/services/print_service.py` | `submissions._get_print_priority` | ~20 lines | Week 2 |

### Success Criteria
- `schedule.py` < 400 lines (from 1087)
- `submissions.py` < 300 lines (from 911)
- `optimize_workflow.py` < 500 lines (from 1331)
- All service functions have unit tests in `tests/services/`
- No `HTTPException` in any service file (`grep -r 'HTTPException' backend/services/` → 0)
- No `db.commit()` in any service file (`grep -r 'db.commit()' backend/services/` → 0)

---

## Phase 4 — PDPA & Security Enforcement

**Goal:** Close audit coverage gaps, enforce data access controls systematically.
**Effort:** 1–2 engineers, 2 weeks
**Dependencies:** Phase 3 (`audit_service.py`)

### Tasks
| Task | Status | Notes |
|------|--------|-------|
| Audit coverage sweep: add ~30 missing `audit_service.record()` calls | ⬜ | See `AUDIT_AND_EVENT_MODEL.md` §3 |
| Set `RETENTION_CLEANUP_ENABLED = True` after dry-run review | ⬜ | Requires admin sign-off |
| Add `_user_id_var.set(user.id)` in `RequestLoggingMiddleware` | ⬜ | `main.py` |
| Add Zod schemas for all mutation forms | ⬜ | `frontend/src/schemas/` |
| Implement `usePermission(action)` hook | ⬜ | `frontend/src/hooks/usePermission.ts` |
| Migrate page-level role checks to `usePermission()` | ⬜ | Pilot: `Checkins.tsx`, `Submissions.tsx` |
| Add backend enforcement for copy count (not just UI-layer) | ⬜ | `exports_excel.py` / `printing.py` |
| Add `assert_checkin_access()` and `assert_swap_request_access()` | ⬜ | `permissions.py` |

### Success Criteria
- 100% of mutation endpoints have audit log calls (verifiable by automated test)
- `grep -r 'roles=\[' frontend/src/pages/` → 0 results (all moved to `App.tsx`)
- Retention dry-run reviewed, approved, and `RETENTION_CLEANUP_ENABLED = True`
- Zod schemas cover all mutation forms

---

## Phase 5 — Operational Intelligence

**Goal:** Build metrics, alerting, and dashboard APIs.
**Effort:** 1–2 engineers, 3 weeks
**Dependencies:** Phase 3 (service layer), Phase 4 (audit coverage)

### Tasks
| Task | Status | Notes |
|------|--------|-------|
| Create `backend/services/health_service.py` | ⬜ | All metric calculations |
| Implement `GET /api/dashboard/period-health` | ⬜ | Role-filtered response |
| Implement `GET /api/dashboard/audit-timeline` | ⬜ | Last N significant events |
| Add `PeriodHealthSnapshot` model + write-on-lock | ⬜ | `models.py` |
| Implement 3 alert conditions in health_service | ⬜ | See `OPERATIONAL_INTELLIGENCE_ROADMAP.md` §5 |
| Frontend: update Dashboard with period health display | ⬜ | `Dashboard.tsx` |
| Add `cacheKey` + TTL to `useAsyncData.ts` | ⬜ | Reduce redundant API calls |
| Email digest: add period-health summary | ⬜ | `email_notifications.py` |

### Success Criteria
- `/api/dashboard/period-health` returns correct data in <500ms
- 3 alert conditions surface in `blockers[]` array
- Every locked period has a `PeriodHealthSnapshot` record

---

## Phase 6 — Multi-Faculty Architecture

**Goal:** Remove all single-faculty hardcoding.
**Effort:** 2 engineers, 4 weeks
**Dependencies:** All previous phases complete; Phase 2 must have moved SIGN_ORDER_USERNAMES to DB

### Tasks
| Task | Status | Notes |
|------|--------|-------|
| Add `Faculty` model | ⬜ | `models.py` |
| Add `faculty_id` nullable FKs to `User`, `ExamPeriod`, `Room`, `Section` | ⬜ | Via migration |
| Seed default faculty and backfill existing rows | ⬜ | `migrate_faculty.py` |
| Seed `WorkflowSignerConfig` from current `SIGN_ORDER_USERNAMES` | ⬜ | |
| Seed `StaffExclusionRule` from hardcoded exclusions | ⬜ | |
| Add `Department` table, seed from `academic_groups.py` | ⬜ | |
| Add faculty-scoped RBAC (`get_faculty_filter()`) | ⬜ | `permissions.py` |
| Add `MULTI_FACULTY_ENABLED` feature flag | ⬜ | `config/settings.py` |
| Frontend: show faculty label in nav when multi-faculty enabled | ⬜ | |

### Success Criteria
- All existing tests pass with `MULTI_FACULTY_ENABLED = False`
- A second faculty can be seeded and have its own separate `ExamPeriod`
- Role checks correctly scope `dept_supervisor` to their faculty

---

## Quick Win Tracker

Five high-impact, low-risk changes that can be done NOW, independent of phase order.

| # | Quick Win | Status | File | Effort | Risk |
|---|-----------|--------|------|--------|------|
| 1 | **Fix `permissions.build_dependencies()` missing call** | ✅ Done | `backend/main.py` | 30 min | Zero (Validated) |
| 2 | **Replace 3 role extraction chains with `getEffectiveRole(user)`** | ✅ Done | `Checkins.tsx:77`, `Schedule.tsx:21`, `ExportCenter.tsx:51` | 1 hour | Zero |
| 3 | **Fix `useAsyncData.ts:25` hardcoded Thai string** | ⬜ Pending | `frontend/src/hooks/useAsyncData.ts:25` | 15 min | Zero |
| 4 | **Add `coerce_user_role()` to `permissions.py`** | ⬜ Pending | `permissions.py`, `optimize_workflow.py`, `users.py` | 1–2 hours | Low |
| 5 | **Centralize export period resolver** | ✅ Done | `backend/config/periods.py`, `exports.py`, `exports_excel.py` | 2–3 hours | Low |

---

## Risk Register

| Risk | Severity | Status | Mitigation |
|------|----------|--------|------------|
| `permissions.build_dependencies()` never called — latent production defect | CRITICAL | ✅ Closed | **FIXED** in `backend/main.py` line 38; validated by compile ✅, import ✅, guard smoke ✅ tests |
| Two parallel permission systems (`auth_utils.py` + `permissions.py`) | HIGH | 🔴 Open | Phase 2: consolidate to `permissions.py` as single source of truth |
| CP-SAT optimizer in `schedule.py` has unclear transaction boundaries | HIGH | 🟡 Tracked | Phase 3: extract optimizer LAST; design transaction scope first |
| Thai strings in error messages cannot be internationalized | MEDIUM | 🟡 Tracked | Phase 2: move all error strings to i18n keys |
| Copy count accessible via API despite UI-layer hiding | MEDIUM | 🟡 Tracked | Phase 4: add backend role check |
| `academic_groups.py` imported by `models.py` — multi-faculty risk | MEDIUM | 🟡 Tracked | Phase 6: move to `Department` table |
| No test coverage — regressions undetectable | HIGH | 🟡 Tracked | Phase 3 requirement: service tests before extraction |
| Retention cleanup disabled — regulatory exposure | MEDIUM | 🟡 Tracked | Phase 4: activate after dry-run sign-off |

---

## Architecture Metrics

Track these metrics as the renovation progresses. Current state measured 2026-05-11.

| Metric | Current | Target | Phase |
|--------|---------|--------|-------|
| Lines of business logic in top 3 routers | ~3329 (1087+1331+911) | <1200 total | Phase 3 |
| Uncovered audit events (mutation endpoints without log_action) | ~30 | 0 | Phase 4 |
| Hardcoded strings outside i18n in backend | ~50+ | 0 | Phase 2 |
| Hardcoded strings outside i18n in frontend | 1 (`useAsyncData.ts:25`) | 0 | Phase 1 |
| Role extraction copy-paste chains in frontend | 3 | 0 | Phase 1 |
| Duplicate `_resolve_period()` implementations | 2 | 0 | Phase 2 |
| Inline `try: models.UserRole(...)` blocks in routers | 4+ | 0 | Phase 2 |
| Service files in `backend/services/` | 0 | 7 | Phase 3 |
| Test coverage on service layer | 0% | >60% | Phase 3 |
| `permissions.build_dependencies()` called at startup | ✅ Yes | ✅ Yes | Phase 1 |
| Single source of truth for permission deps | ❌ No (2 files) | ✅ Yes | Phase 2 |

---

## Recommended First Sprint (2 weeks, 2 engineers)

See `SERVICE_LAYER_PLAN.md` §8 for the day-by-day breakdown.

**Engineer A (Backend):** `settings.py`, permissions bug fix, `coerce_user_role`, `submission_service.py`, period resolution consolidation

**Engineer B (Frontend):** Role extraction chains, `useAsyncData` fix, `usePermission` hook, decompose `Checkins.tsx` hooks, `PageSkeleton` component

**Sprint exit criteria:**
- `permissions.build_dependencies()` called at startup, confirmed by test
- Zero role extraction chains in frontend (CI grep enforced)
- `submission_service.py` exists with unit tests
- `_resolve_period()` centralized in `term_lifecycle.py`
- `Checkins.tsx` < 250 lines of component code
