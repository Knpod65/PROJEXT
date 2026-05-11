# Auth DRY Refactor Plan
## EMS Authentication and Authorization Cleanup

**Purpose:** Identify the current DRY violations in EMS auth logic and define a safe cleanup plan without rewriting the platform.

**Scope:** Documentation-first. No code refactor in this phase unless explicitly approved as a safe follow-up.

---

## 1. Current DRY Violations

### Backend duplication

#### `auth_utils.py` and `permissions.py`
Both modules currently carry overlapping responsibilities:
- role-based authorization helpers
- `get_effective_role()` behavior
- role predicates such as admin / staff / view-all checks
- session-driven access logic that should be centralized

#### Symptoms
- Same concepts exist in more than one module
- Permission rules are implemented in parallel rather than through a single source of truth
- `permissions.py` is the intended policy module, but `auth_utils.py` still contains legacy helpers that overlap

### Frontend duplication

#### Repeated effective role chain
Pages repeatedly use:
- `user?.effective_role ?? user?.active_role ?? user?.role ?? null`

Confirmed locations:
- [frontend/src/pages/Checkins.tsx](../../frontend/src/pages/Checkins.tsx) line 77
- [frontend/src/pages/Schedule.tsx](../../frontend/src/pages/Schedule.tsx) line 21
- [frontend/src/pages/ExportCenter.tsx](../../frontend/src/pages/ExportCenter.tsx) line 51

#### Existing canonical helper already exists
- [frontend/src/utils/roles.ts](../../frontend/src/utils/roles.ts) already exports `getEffectiveRole(user)`
- That means the frontend can be cleaned up without changing behavior

### Route and page access mixing
- Route-level guards are already centralized in `App.tsx`
- Page-level permission checks are scattered and often expressed directly as role arrays or ad hoc comparisons
- This is harder to maintain than a semantic permission hook

---

## 2. Canonicalization Targets

### Backend canonical source of truth
`permissions.py` should be the policy layer.

It should own:
- `get_effective_role()` or a single equivalent helper
- `require_admin`
- `require_staff_or_admin`
- `require_view_all`
- object-level authorization helpers
- future faculty-scoped access checks

`auth_utils.py` should own:
- password hashing and verification
- JWT creation / validation utilities
- request token extraction and session resolution
- login/logout session mechanics
- auth audit logging helpers

### Frontend canonical source of truth
`frontend/src/utils/roles.ts` should remain the role helper source.

Recommended frontend abstractions:
- `getEffectiveRole(user)` for pure role normalization
- `useEffectiveRole()` for components that need the current user role
- `usePermission(action)` for semantic access decisions

---

## 3. Cleanup Strategy

### Phase 1: Replace duplicated frontend role resolution
**Goal:** Remove the three confirmed copy-paste chains with zero behavior change.

Safe change:
- Replace the inline fallback chain with `getEffectiveRole(user)` or a hook wrapper around it

Expected result:
- No change in visible behavior
- One canonical role resolution path in the UI
- Easier future auth integration with faculty callback login

### Phase 2: Consolidate backend role helpers
**Goal:** Move policy decisions into one module.

Safe cleanup targets:
- Remove or deprecate duplicate authorization helpers in `auth_utils.py`
- Keep `permissions.py` as the canonical policy module
- Keep `auth_utils.py` focused on auth/session primitives

Suggested compatibility approach:
- Preserve existing imports temporarily if the codebase relies on them
- Re-export or wrap where necessary during transition
- Add a repo-level search check so duplicate helpers do not reappear

### Phase 3: Introduce semantic permission naming
**Goal:** Replace raw role comparisons with intention-revealing permission names.

Examples:
- `manage_pickup`
- `approve_submission`
- `view_audit_logs`
- `edit_schedule`

This is safer than scattering role arrays because it expresses business intent rather than account type logic.

---

## 4. Files Most Likely Affected

### Backend
- [backend/auth_utils.py](../../backend/auth_utils.py)
- [backend/permissions.py](../../backend/permissions.py)
- [backend/routers/auth.py](../../backend/routers/auth.py)
- Any routers that still import role predicates directly from `auth_utils.py`

### Frontend
- [frontend/src/pages/Checkins.tsx](../../frontend/src/pages/Checkins.tsx)
- [frontend/src/pages/Schedule.tsx](../../frontend/src/pages/Schedule.tsx)
- [frontend/src/pages/ExportCenter.tsx](../../frontend/src/pages/ExportCenter.tsx)
- [frontend/src/utils/roles.ts](../../frontend/src/utils/roles.ts)
- Future permission hook file, if introduced

---

## 5. Safe Migration Order

### Step 1: Frontend role extraction cleanup
- Replace the three manual role chains with `getEffectiveRole(user)`
- Add a tiny hook wrapper if needed for page ergonomics
- Verify no UI behavior changes

### Step 2: Backend policy consolidation
- Keep `permissions.py` as the policy source of truth
- Gradually remove duplicate role predicates from `auth_utils.py`
- Update imports in routers to reference the canonical policy helpers

### Step 3: Add auth integration layer for faculty login
- Add callback/authen support without changing EMS session semantics
- Keep session issuance inside EMS
- Add tests for callback login and token verification

### Step 4: Semantic permission layer
- Add `usePermission(action)` on the frontend
- Convert page-level permission checks from direct role logic to permission names
- Keep route guards centralized

---

## 6. Regression Risks

### Risk: mismatch between base role and effective role
- If a page bypasses canonical role resolution, impersonation behavior can drift
- Mitigation: centralize role resolution and test admin view-as flows

### Risk: backend policy drift
- If both `auth_utils.py` and `permissions.py` continue to evolve independently, authorization behavior can diverge
- Mitigation: designate `permissions.py` as policy owner and add a duplicate-helper cleanup step

### Risk: callback auth introduces session confusion
- External identity callbacks should not directly become frontend state without EMS session issuance
- Mitigation: always exchange callback proof for EMS-native JWT/session

### Risk: PDPA/audit gaps
- Auth callback handling can become a blind spot if not audited
- Mitigation: log received callback source, verification result, session issuance, and failures

---

## 7. DRY Cleanup Rules

1. Do not duplicate role resolution in pages
2. Do not duplicate authorization policy in multiple backend modules
3. Do not store external auth proof in the frontend as the session of record
4. Do not let callback handling bypass audit logging
5. Do not conflate authentication with authorization; keep them separate

---

## 8. Recommended Follow-up Work

### Documentation / config only
- Add the auth integration strategy to the architecture baseline
- Define a single canonical callback contract with faculty IT
- Record the backend ownership split: session mechanics vs policy decisions

### Safe code follow-up later
- Replace the three frontend role chains
- Add canonical backend import paths for permission helpers
- Introduce a small auth integration service for callback verification

---

## 9. Summary

The DRY problem in EMS auth is not a missing framework. It is the duplication of role resolution and permission policy across layers.

The safest cleanup path is to keep EMS on FastAPI, add a dedicated auth integration boundary for faculty callback login, and consolidate role helpers so one module owns policy decisions and one frontend utility owns role normalization.