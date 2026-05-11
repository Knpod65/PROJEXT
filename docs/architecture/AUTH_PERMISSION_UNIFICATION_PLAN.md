# Auth / Permission Unification Plan
## EMS — Academic Operations Platform

> **Status:** Phase 3 prerequisite — do NOT consolidate before service layer is in place.
> **Target completion:** Phase 3, Week 3–4
> **Risk:** HIGH — 26 routers import from auth_utils; wrong sequencing breaks all protected endpoints

---

## 1. Current Situation

Three overlapping files handle auth and role logic:

| File | Role | Lines | Routers importing |
|------|------|-------|-------------------|
| `auth_utils.py` | Auth (JWT/cookie/hash) + role guards + helpers | ~530 | 26 |
| `permissions.py` | Canonical RBAC guards + role sets | ~215 | Several + main.py |
| `services/permission_service.py` | Semantic domain helpers (Phase 3 new) | ~130 | None yet (additive) |

### Duplicated symbols (auth_utils.py lines 259–332 overlap with permissions.py):

| Symbol | In auth_utils.py | In permissions.py | Safe to remove from |
|--------|-----------------|-------------------|---------------------|
| `require_admin` | line 264 | line 108 (via build_dependencies) | auth_utils after migration |
| `require_staff_or_admin` | line 269 | line 113 (via build_dependencies) | auth_utils after migration |
| `require_view_all` | line 295 | line 118 (via build_dependencies) | auth_utils after migration |
| `require_read_only` | line 336 | (missing) | — (keep in auth_utils for now) |
| `require_can_edit` | line 347 | (missing, maps to require_write) | — keep until both merged |
| `get_dept_filter` | line 316 | line 51 | auth_utils after migration |
| `get_effective_role` | line 252 | line 45 | auth_utils after migration |

### Unique symbols in auth_utils.py (NOT in permissions.py — do NOT remove):

- `hash_password`, `verify_password`, `DUMMY_PASSWORD_HASH`
- `create_token`, `revoke_token`, `is_token_revoked`
- `get_current_user`, `get_current_user_optional`
- `resolve_request_auth`, `RequestAuthState`
- `require_base_admin`, `require_print_shop`
- `require_dept_or_admin`
- `is_eligible_supervisor`, `is_eligible_distributor`
- `show_in_fairness_stat`, `is_room_keeper`
- `is_esq_staff` — permanently returns False; dead code; remove in Phase 3
- `assert_dept_access`
- `log_action`
- `_coerce_user_role` — private; `permissions.coerce_user_role` is the public version

---

## 2. Target Ownership (Post-Consolidation)

```
auth_utils.py          = Authentication only
  ├── JWT encode/decode
  ├── cookie/Bearer token extraction
  ├── token revocation (blacklist)
  ├── password hashing
  ├── get_current_user / get_current_user_optional
  ├── resolve_request_auth
  └── log_action  (audit utility — keep here for now; Phase 4 will move to audit_service)

permissions.py         = FastAPI dependency guards + role sets
  ├── VIEW_ALL_ROLES, WRITE_ROLES, SIGNER_ROLES, SUPERVISION_ROLES
  ├── build_dependencies()  (wires guard functions at startup)
  ├── require_admin, require_staff_or_admin, require_view_all, require_write
  ├── require_print_shop, require_base_admin, require_dept_or_admin
  ├── get_effective_role, get_dept_filter
  ├── coerce_user_role
  └── assert_* object-level guards

services/permission_service.py  = Semantic domain helpers
  ├── can_manage_users, can_view_all, can_manage_workflow ...
  └── (no FastAPI types, no Depends)
```

---

## 3. Migration Sequence

### Step 1 — Add missing guards to permissions.py (Phase 3, Week 1)

Add to `permissions.py` inside `build_dependencies()`:
- `require_read_only` — same semantics as in auth_utils:336
- `require_can_edit` — same semantics as in auth_utils:347
- `require_print_shop` — same semantics as in auth_utils:278
- `require_dept_or_admin` — same semantics as in auth_utils:305

This makes `permissions.py` the complete set; auth_utils copies become redundant.

### Step 2 — Add deprecation shims to auth_utils.py (Phase 3, Week 2)

Replace the duplicate definitions in `auth_utils.py` lines 264–332 with:
```python
# Compatibility shims — import from permissions.py (single source of truth)
from permissions import (
    require_admin as require_admin,
    require_staff_or_admin as require_staff_or_admin,
    require_view_all as require_view_all,
    get_dept_filter as get_dept_filter,
    get_effective_role as get_effective_role,
)
```
All 26 routers that `from auth_utils import require_admin` continue to work unchanged.

### Step 3 — Migrate routers one domain at a time (Phase 3, Weeks 2–4)

Order by risk (lowest-impact domains first):

| Priority | Domain | Routers | Effort |
|----------|--------|---------|--------|
| 1 | Co-exam | `co_exam.py` | 30 min |
| 2 | Documents | `documents.py` | 30 min |
| 3 | External | `external_exams.py` | 30 min |
| 4 | Period lifecycle | `period.py` | 45 min |
| 5 | Checkins / Swaps | `checkins.py`, `swaps.py`, `swaps_v2.py` | 1 hr |
| 6 | Submissions | `submissions.py` | 1 hr |
| 7 | Schedule | `schedule.py` | 2 hr (largest) |
| 8 | Users / Workflow | `users.py`, `optimize_workflow.py` | 2 hr |

For each router: change `from auth_utils import require_admin` → `from permissions import require_admin`.

### Step 4 — Remove dead code from auth_utils.py (Phase 3, Week 4)

Once all routers import from `permissions.py`:
1. Remove duplicate guard definitions from `auth_utils.py` lines 259–332
2. Remove `is_esq_staff()` (permanently returns False)
3. Remove private `_coerce_user_role()` (replaced by `permissions.coerce_user_role`)

---

## 4. Regression Tests Required Before Each Step

For each router migration, verify:
1. `python -m py_compile <router>.py` — no import errors
2. `GET /api/auth/login` returns 200 with valid credentials
3. `GET /api/schedule/` without token returns 401
4. `GET /api/schedule/` with teacher token returns 200
5. `POST /api/co-exam/` with non-admin token returns 403

Minimum smoke test script to add to `tests/`:
```python
# tests/test_auth_migration.py
# Verifies that role guards work identically from both import paths
from permissions import require_admin as p_require_admin
from auth_utils import require_admin as a_require_admin
# Both must be the same function object after consolidation
assert p_require_admin is a_require_admin, "Shim must re-export permissions guard"
```

---

## 5. Functions to Deprecate / Remove

| Function | File | Why | Phase |
|----------|------|-----|-------|
| `is_esq_staff()` | auth_utils:412 | Always returns False; documented as dead code | Phase 3 |
| `_coerce_user_role()` | auth_utils:103 | Private; `permissions.coerce_user_role` is canonical | Phase 3 |
| Duplicate guards | auth_utils:259–332 | Replaced by shims → permissions.py | Phase 3 |
| `require_read_only` | auth_utils | After added to permissions.py | Phase 3 |

---

## 6. No-Laravel-Rewrite Decision

EMS remains FastAPI + React. The full rationale is in `EMS_COMPLETION_GAP_REPORT.md §13`.

**Summary:** 190 endpoints, 35+ pages, CMU SSO already integrated — no rewrite justification.

---

## 7. Optional: Faculty IT / Laravel Auth Gateway Integration

If Faculty IT runs a Laravel-based auth system, the recommended integration is:

```
Faculty IT (Laravel/PHP)           EMS (FastAPI)
─────────────────────────          ──────────────────────────
                                   cmu_sso.py  ←── existing SSO sidecar
Faculty IT OAuth2 server ─────────► /api/auth/sso/callback
                                   JWT issued by EMS backend
                                   Session cookie set
```

**How:**
1. `cmu_sso.py` already provides the CMU Nimbus SSO integration point
2. Extend `cmu_sso.py` to accept Faculty IT as an additional OAuth2 provider
3. Faculty IT acts as IdP; EMS verifies the identity claim and issues its own JWT
4. No changes to role system, middleware, or frontend required

**What this is NOT:**
- Not a rewrite of EMS in Laravel
- Not delegating RBAC to Faculty IT (EMS owns role assignment)
- Not replacing the JWT / cookie session mechanism

**Contract to agree with Faculty IT:**
- OAuth2 authorization code flow
- Scopes: `openid profile email`
- Required claim: `employee_id` or `username` (to match `users.username` in EMS DB)
- Token expiry: 15 min access token; EMS issues its own session cookie

---

## 8. Routers Affected by Consolidation

All 26 routers currently import from `auth_utils`. After Step 2 shims:
- No immediate changes needed in any router
- Gradual migration can happen one router per sprint without coordination overhead

```
auth.py            checkins.py       co_exam.py         courses.py
dashboard.py       documents.py      exam_manager.py    exports.py
exports_excel.py   external_exams.py historical_schedules.py
imports.py         imports_v2.py     optimize_workflow.py  pdf.py
period.py          printing.py       public.py          schedule.py
scheduler.py       settings.py       submissions.py     swaps.py
swaps_v2.py        users.py
```

---

## 9. Exit Criteria for Full Consolidation

- `grep -r "from auth_utils import require_" backend/routers/` → 0 results
- `grep -r "from auth_utils import get_effective_role" backend/routers/` → 0 results
- `python -m py_compile` passes for all 26 routers
- Login/logout flow works end-to-end
- `/api/schedule/` returns correct 401/403/200 based on role
- `auth_utils.py` ≤ 300 lines (currently ~530)
