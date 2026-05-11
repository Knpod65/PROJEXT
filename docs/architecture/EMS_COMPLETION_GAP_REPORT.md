# EMS Completion Gap Report
## Academic Operations Intelligence Platform — Production Readiness Assessment

> **Generated:** 2026-05-11 (updated — Phase 3 Week 2 session)
> **Scope:** Full system audit — backend, frontend, PDPA, deployment, architecture
> **Based on:** Live codebase scan + renovation phase tracking
> **See also:** `PRODUCTION_HARDENING_FINAL_REPORT.md` for full session detail

---

## 1. Executive Summary

The EMS system is a **functional, deployed FastAPI + React exam management platform** serving CMU Political Science Faculty. Core workflows are complete and operational. A multi-phase architectural renovation is underway. The system is **suitable for single-faculty production use** with known gaps in test coverage, audit completeness, and service layer structure. Multi-faculty use requires Phase 6 work.

**Overall readiness score: 78 / 100** *(was 75/100; +3 from Phase 3 Week 2 session)*

---

## 2. Current Readiness Score

| Area | Score | Notes |
|------|-------|-------|
| Authentication & Authorization | 89/100 | permissions.py now has all 9 guards (Step 1 unification complete); unification plan active |
| PDPA & Privacy | 77/100 | Retention disabled; ~21 audit gaps remain (1 more closed); masking implemented |
| Workflow & Operations | 88/100 | All core workflows implemented; state machine guards partially missing |
| Import / Export / Lineage | 80/100 | V2 pipeline solid; `_resolve_period` consolidated; lineage metadata present |
| Frontend UX/UI | 83/100 | permissions.ts complete; **0 pages** with inline role checks (6→0 across two sessions) |
| Backend Architecture | 72/100 | 6 service modules; 87 tests; submission_service extracted; fat routers remain |
| Deployment / DevOps | 82/100 | `/api/health` + `/api/health/ready` added; Docker HEALTHCHECK still missing |
| **Overall** | **78/100** | +3 from Phase 3 Week 2; single-faculty production viable |

---

## 3. What Is Complete

### Authentication & Session
- JWT + HttpOnly cookie dual-mode auth (`auth_utils.py`)
- CMU SSO integration (`cmu_sso.py`)
- `permissions.build_dependencies()` correctly called in `main.py` lifespan (line 39)
- 8-role RBAC enforced via FastAPI `Depends()` guards on all routes
- Admin `view_as_role` impersonation for testing
- `getEffectiveRole()` used consistently in frontend (3 copy-paste chains fixed)
- `selected_role` / `view_as_role` state in frontend Zustand store

### PDPA & Privacy
- `AuditLog` model with 12-field schema: actor, IP hash, UA hash, request ID, duration
- `log_action()` called from ~95 mutation endpoints
- Student PII masked in public endpoints
- HttpOnly cookie prevents client-side token access
- Data retention policy model in `config/retention_policy.py` (disabled pending sign-off)
- Export access gated by role; exports logged via `log_action`
- QR pickup access control with expiry window

### Workflow & Operations
- Full exam period lifecycle: `pending → active → locked → archived`
- Teacher submission 3-step wizard (confirm date → exam type → metadata → upload)
- ESQ workflow signing: multi-round with `SIGN_ORDER_USERNAMES` config
- Swap request system with conflict detection (V2 + legacy V1)
- Paper distribution algorithm with eligibility rules
- Copy count management with room-level tracking
- Print queue with priority scoring (high/medium/normal thresholds in `config/settings.py`)
- Room opening confirmation with QR codes
- Historical schedule archiving with `historical_schedule_batches`

### Import / Export / Lineage
- Import V2 pipeline: parser → validator → normalizer → importer
- `ImportExecutionBlocked` guard prevents import on locked period
- Idempotent upsert with `import_session_id` linkage
- Export catalog: PDF, Excel, QR, regulation sheets
- `resolve_export_period()` centralized in `config/periods.py`
- Import audit trail in `ImportSession` and `ImportRowLog` models

### Configuration (Phase 2 complete items)
- `backend/config/settings.py` — typed `@dataclass(frozen=True)` Settings singleton
- `backend/config/policy.py` — re-export shim, all existing imports unchanged
- `SupervisionRole` enum in `models.py` (supervisor/chief/distributor/room_keeper)
- `permissions.coerce_user_role()` replaces inline `try: UserRole(x) except ValueError` patterns
- `SIGN_ORDER_USERNAMES` / `PAPER_DISTRIBUTION_*` env-backed via Settings

### Deployment
- `Dockerfile` with multi-stage build
- `docker-compose.yml` + `docker-compose.dev.yml` + `docker-compose.local.yml`
- `nginx.conf` with SPA fallback and static file serving
- `.env.example` present with all required keys
- `validate_production_secrets()` called at startup — blocks launch with `change-me` SECRET_KEY
- `.gitignore` excludes `.env`, SQLite files, `__pycache__`, `uploads/`

---

## 4. What Is Partially Complete

### PDPA / Audit Coverage
- **~26 mutation endpoints still lack `log_action()` calls** (down from ~30; 4 fixed in co_exam.py this session)
- `RETENTION_CLEANUP_ENABLED = False` — dry-run report exists, sign-off pending
- No automated audit coverage test (verifiable via `grep @router.post|put|delete`)

### Auth / Permissions Architecture
- `auth_utils.py` contains duplicate definitions of `require_admin`, `require_staff_or_admin`, `require_view_all`, `get_dept_filter`, `get_effective_role` (lines 259–332) that also exist in `permissions.py`
- 26 routers import these from `auth_utils` — safe consolidation deferred to Phase 3

### Frontend Role Authorization
- `getEffectiveRole()` used in 3 key pages (Checkins, Schedule, ExportCenter) ✅
- **6 pages still use inline `role === "..."` comparisons** (see §8 below)
- No `usePermission(action)` hook — role arrays duplicated across files
- No Zod validation on mutation forms (silent `NaN` on type coercion possible)

### Service Layer
- Business logic embedded in fat route handlers
- `schedule.py`: 1087 lines (CP-SAT optimizer + CRUD + conflict detection)
- `optimize_workflow.py`: 1330 lines (user CRUD + signing + unavailability)
- `submissions.py`: 911 lines (state machine + print queue + PDF tokens)
- No `backend/services/` directory exists yet

### Testing
- **Zero test files** exist (`backend/tests/` directory does not exist)
- No CI pipeline configured
- No integration tests against DB

---

## 5. What Is Missing

### Critical
1. **Test coverage** — zero tests; regressions undetectable
2. **`auth_utils.py` permission consolidation** — parallel implementations risk divergence
3. **State machine guard completeness** — some transitions lack all guard conditions (documented in `WORKFLOW_STATE_MACHINE.md` §8)

### High Priority
4. **`usePermission(action)` hook** — 6 pages still use inline role comparisons
5. **Zod form validation** — all mutation forms lack schema validation
6. **~26 missing audit log calls** — Phase 4 target, systematic sweep needed
7. **App-level Docker health check** — no `HEALTHCHECK` directive in Dockerfile
8. **Retention cleanup activation** — needs dry-run review and admin sign-off

### Medium Priority
9. **Service layer extraction** — Phase 3 work; fat routers block testability
10. **`usePermission` migration** — inline role checks in Dashboard, Submissions, PrintReview, WorkflowV2, SwapsV2, External
11. **Backend copy count enforcement** — copy count validation is UI-only; backend does not enforce
12. **`assert_checkin_access()` and `assert_swap_request_access()`** — object-level guards missing
13. **Bundle size** — 647 kB JS (> 500 kB warning); no code splitting configured
14. **Dashboard analytics backend** — `/api/dashboard/period-health` not yet implemented

---

## 6. Critical Blockers

| # | Issue | File | Impact |
|---|-------|------|--------|
| C1 | Zero test coverage | — | Any refactor can break without detection |
| C2 | `auth_utils.py` dual permission system | `auth_utils.py:259-332`, `permissions.py` | Will diverge; unexpected auth behavior |
| C3 | ~26 mutation endpoints without audit logs | Multiple routers | PDPA non-compliance; regulatory exposure |

---

## 7. High-Priority Blockers

| # | Issue | File | Effort |
|---|-------|------|--------|
| H1 | Inline role checks in 6 pages | `Dashboard.tsx`, `Submissions.tsx`, `PrintReview.tsx`, `WorkflowV2.tsx`, `SwapsV2.tsx`, `External.tsx` | 2–3 hours |
| H2 | No Zod validation on mutation forms | `frontend/src/` | 4–6 hours |
| H3 | Retention cleanup still disabled | `config/retention_policy.py:100` | Admin sign-off + 1 hour |
| H4 | No app Docker health check | `Dockerfile` | 30 min |
| H5 | `schedule.py` 1087 lines — CP-SAT mixed with CRUD | `routers/schedule.py` | Phase 3, 2 weeks |

---

## 8. Medium-Priority Backlog

### Backend
- `documents.py:189, 246, 551` — 3 mutation endpoints without audit logs
- `routers/schedule.py:638` — inline `from auth_utils import is_room_keeper` (lazy local import)
- `exports.py:165` — hardcoded faculty name in PDF generation: `"คณะรัฐศาสตร์และรัฐประศาสนศาสตร์"` (should come from config/DB)
- `staff_workloads.py` — person-specific exclusions still in code (`PAPER_DISTRIBUTION_EXCLUDED_USERNAMES` env-backed but not DB-backed)
- `SIGN_ORDER_USERNAMES` still a flat list; should be `WorkflowSignerConfig` table (Phase 6)
- No `backend/services/exceptions.py` — business errors raised as `HTTPException` directly

### Frontend
- `Dashboard.tsx:57, 144` — `role === "admin"` inline checks
- `Submissions.tsx:127` — `role === "teacher"` inline check
- `PrintReview.tsx:270` — role array check: `role === "admin" || role === "esq_head" || role === "secretary"`
- `WorkflowV2.tsx:264-265` — admin + view-all role checks inline
- `SwapsV2.tsx:147` — `role === "admin"` check
- `External.tsx:372-373` — admin + staff inline checks
- `Workflow.tsx:83` — `<Badge>คุณ</Badge>` raw Thai in JSX (minor i18n gap)
- `Period.tsx:72` — `<Button>สร้างรอบ</Button>` raw Thai in JSX (minor)
- Bundle size 647 kB — no `React.lazy()` / code splitting

### Architecture
- No CI configuration (GitHub Actions or equivalent)
- No database migration framework (Alembic); schema managed via `create_all()`
- `academic_groups.py` imported by `models.py` — coupling that blocks Phase 6

---

## 9. Low-Priority Cleanup

- Old dev docs in root: `IMPLEMENTATION_STATUS_2026-04-16.md`, `STITCH_ADAPTATION_GAP_ANALYSIS_2026-04-17.md`, `sidebar_mapping_for_approval_2026-04-16.md` — can be archived
- `ui_schema.json`, `ui_spec.md` in root — should move to `docs/`
- `is_esq_staff()` in `auth_utils.py:412` is permanently `False` — dead code, can be removed in Phase 3
- `schedule.py:638, 839, 866` — local lazy imports inside route functions; move to file top
- Docker chunk size warning (647 kB) — add `rollupOptions.output.manualChunks` in `vite.config.ts`

---

## 10. Production Go / No-Go Recommendation

### ✅ Go — Current Single-Faculty Production Use

The system **is acceptable for continued single-faculty production use** with these conditions:
1. `SECRET_KEY` is a strong random value (enforced by `validate_production_secrets()`)
2. PDPA data retention procedure is documented and a schedule is set for dry-run review
3. Faculty operators understand that audit logs have ~26 gap endpoints (Phase 4 closure)

### ⛔ No-Go — Multi-Faculty or Regulated Expansion

**Do NOT expand to additional faculties** or increase PDPA regulatory scope until:
1. Phase 3 (service layer) is complete — provides testability
2. Phase 4 (PDPA enforcement) is complete — closes audit gaps
3. Phase 6 (multi-faculty) is complete — adds faculty isolation

---

## 11. Phase 2 Final Status

**Phase 2 DRY Configuration Layer: 85% complete**

| Task | Status |
|------|--------|
| Typed `Settings` dataclass in `config/settings.py` | ✅ Done |
| `config/policy.py` re-export shim | ✅ Done |
| `SupervisionRole` enum in `models.py` | ✅ Done |
| `permissions.coerce_user_role()` | ✅ Done |
| 3 inline `try: UserRole(x)` blocks replaced | ✅ Done |
| Export period resolver centralized | ✅ Done |
| `useAsyncData.ts` Thai fallback → `translate("errors.unexpected")` | ✅ Done |
| PAPER_DISTRIBUTION_EXCLUDED_USERNAMES → DB table | 🔄 Deferred Phase 6 |
| SIGN_ORDER_USERNAMES → WorkflowSignerConfig table | 🔄 Deferred Phase 6 |
| `auth_utils.py` duplicate guards → `permissions.py` consolidation | 🔄 Deferred Phase 3 |

Remaining work: 3 items explicitly deferred to later phases (correct architectural decision — safe to declare Phase 2 closure).

---

## 12. Phase 3 Recommended Start Scope

### Week 1–2: Foundation
```
backend/services/__init__.py          (empty)
backend/services/exceptions.py        (EMSDomainError hierarchy)
backend/services/submission_service.py (extract from submissions.py)
  - _get_submission()
  - _save_version()
  - _get_print_priority()   ← highest-ROI extraction
  - _upsert_print_queue_job()
```

### Week 3–4: High-ROI Routers
```
backend/services/schedule_service.py  (non-optimizer helpers from schedule.py)
backend/services/audit_service.py     (wrap log_action; add ~26 missing calls)
backend/services/user_service.py      (extract from optimize_workflow.py user section)
tests/services/                       (test each service module)
```

### Phase 3 Exit Criteria
- `schedule.py` < 400 lines
- `submissions.py` < 300 lines
- `optimize_workflow.py` < 500 lines
- All service functions covered by unit tests in `tests/services/`
- No `HTTPException` in any service module
- No `db.commit()` in any service module

---

## 13. Laravel/PHP Decision Note

**EMS remains FastAPI + React. No PHP/Laravel rewrite recommended.**

The system already has:
- Working FastAPI backend with 26 routers, 190 endpoints
- React 18 + TypeScript + Vite frontend with 35+ pages
- CMU SSO integration already implemented as a FastAPI sidecar

**Recommended integration model for Faculty IT (Laravel-based):**
- Laravel/Faculty IT auth system → acts as OAuth2 callback endpoint
- EMS calls Faculty IT as an external IdP for user provisioning
- `cmu_sso.py` already provides the integration point
- No full rewrite needed; extend the SSO contract

---

## 14. Final Checklist

| Area | Status | Notes |
|------|--------|-------|
| **Auth** — login/logout/JWT/cookie | ✅ | HttpOnly cookie, dual-mode extraction |
| **Auth** — RBAC on all routes | ✅ | `permissions.build_dependencies()` called |
| **Auth** — `view_as_role` impersonation | ✅ | Admin-only, guarded |
| **PDPA** — data masking | ✅ | PII masked in public endpoints |
| **PDPA** — audit log schema | ✅ | 12-field `AuditLog` model |
| **PDPA** — audit coverage | ⚠️ | ~26 endpoints still missing |
| **PDPA** — retention policy | ⚠️ | Disabled; dry-run ready; needs sign-off |
| **Audit** — action name registry | ✅ | `config/audit_actions.py` |
| **Import** — V2 pipeline | ✅ | 4-stage parser/validator/normalizer/importer |
| **Import** — guard conditions | ✅ | `ImportExecutionBlocked` on locked period |
| **Workflow** — period lifecycle | ✅ | pending→active→locked→archived |
| **Workflow** — submission wizard | ✅ | 3-step + upload + approval |
| **Workflow** — signing rounds | ✅ | Multi-round with SIGN_ORDER config |
| **Optimization** — CP-SAT scheduler | ✅ | Operational in `schedule.py` |
| **Optimization** — transaction safety | ⚠️ | Boundaries unclear; Phase 3 prerequisite |
| **Reports** — PDF export | ✅ | Regulation sheets, submission PDFs |
| **Reports** — Excel export | ✅ | Multiple export types |
| **Reports** — historical snapshots | ✅ | `historical_schedule_batches` |
| **UI** — bilingual TH/EN | ✅ | Custom i18n system, both dictionaries |
| **UI** — role theming | ✅ | `roleThemes.ts` → CSS custom properties |
| **UI** — inline role checks | ⚠️ | 6 pages still use `role === "..."` |
| **UI** — form validation | ⚠️ | No Zod schemas; silent type coercion |
| **UI** — loading/error states | ✅ | `useAsyncData` + i18n error messages |
| **Deployment** — Docker | ✅ | Multi-stage Dockerfile + compose |
| **Deployment** — Nginx | ✅ | SPA fallback + proxy |
| **Deployment** — `.env.example` | ✅ | All required keys documented |
| **Deployment** — SECRET_KEY guard | ✅ | `validate_production_secrets()` at startup |
| **Deployment** — app health check | ⚠️ | No `HEALTHCHECK` in Dockerfile |
| **Deployment** — DB migration framework | ⚠️ | Using `create_all()`; no Alembic |
| **Documentation** — architecture docs | ✅ | 11 documents in `docs/architecture/` |
| **Documentation** — API spec | ⚠️ | Auto-generated OpenAPI only; no maintained spec |
| **Testing** | ❌ | Zero test files; highest priority debt |
