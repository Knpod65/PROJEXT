# EMS_CURRENT_AUTH_FLOW_AUDIT.md

**Date**: 2026-05-22
**Purpose**: Read-only audit of the current EMS authentication system, to inform the Laravel/CMU auth bridge design. No code was changed during this audit.
**Files reviewed**:
- `backend/auth_utils.py` (519 lines)
- `backend/routers/auth.py` (167 lines)
- `backend/cmu_sso.py` (54 lines)
- `frontend/src/store/auth.store.tsx` (179 lines)
- `frontend/src/components/layout/ProtectedRoute.tsx` (33 lines)
- `frontend/src/services/api.ts` (146 lines)
- `frontend/src/utils/permissions.ts` (149 lines)

---

## 1. Current Login Flow

### Step-by-Step

```
User enters username + password + selected_role on EMS login page
    ↓
Frontend calls: POST /api/auth/login
    body: { username, password, selected_role }
    ↓
Backend (routers/auth.py: login endpoint):
    1. Look up user by username in DB
    2. Verify password with bcrypt (constant-time to prevent timing oracle)
    3. Validate selected_role is in user's allowed roles
    4. Call create_token() → creates JWT with { sub: user_id, active_role }
    5. Set HttpOnly cookie: ems_session = <JWT>
       (secure, httponly, samesite=lax — JS cannot read this cookie)
    6. Also return token in response body (legacy Bearer header support)
    7. Call log_action(user_id, "login") → writes to AuditLog table
    ↓
Frontend (auth.store.tsx: signIn):
    1. Receives UserMe object from login response
    2. Sets user state in React Context
    3. Sets localStorage hint (auth_hint = "1") — used to skip /me call on public pages
    ↓
All subsequent API calls:
    - fetch() sends credentials: "include" → ems_session cookie attached automatically
    - No manual Bearer token handling required in frontend
```

### Token Structure

JWT payload created by `create_token()` in `auth_utils.py`:
```json
{
  "sub": "<user_id>",
  "active_role": "<role>",
  "exp": "<expiry_timestamp>"
}
```

---

## 2. Token Extraction: `resolve_request_auth()`

Located in `backend/auth_utils.py`.

**Priority order**:
1. HttpOnly cookie (`ems_session`) — preferred
2. `Authorization: Bearer <token>` header — legacy fallback for non-browser clients

This dual-extraction allows browser clients to use the secure HttpOnly cookie while API/script clients can use a Bearer token. For the Faculty LAN pilot, the HttpOnly cookie path is the primary one.

---

## 3. Role Enforcement

**Backend** (`auth_utils.py`):

| Guard function | Allowed | Usage |
|---|---|---|
| `require_admin()` | `admin` only | Admin-only API endpoints |
| `require_base_admin()` | `admin` (real base role, not view_as) | Endpoints that must not be reachable by impersonated admin |
| `require_staff_or_admin()` | `admin`, `esq_head`, `secretary` | Staff-level endpoints |
| `require_view_all()` | `admin`, `esq_head`, `secretary` | Cross-department data access |
| `assert_dept_access()` | `dept_supervisor`, `teacher` | Restricts to own department's data |

**Admin view-as impersonation** (`auth_utils.py`):
- Admin can set `view_as_role` via `POST /api/auth/view-as`
- `get_effective_role()` returns `view_as_role` if set, otherwise `active_role`
- `get_base_role()` always returns the real `active_role`, ignoring `view_as_role`
- `require_base_admin()` uses `get_base_role()` — cannot be bypassed by impersonation

**Frontend** (`permissions.ts`):
- All permission functions call `getEffectiveRole(user)` — respects `view_as_role`
- `canUseViewAs()` uses `getBaseRole(user)` — requires real admin role
- Frontend permissions are UX-only; backend guards are authoritative

---

## 4. Frontend Auth State

**`frontend/src/store/auth.store.tsx`** — React Context:

```
AuthContext provides:
- user: UserMe | null
- loading: boolean
- initialized: boolean  ← false until first /me check completes
- activeRole: UserRole | null
- availableRoles: UserRole[]
- signIn(), signOut(), refreshUser(), switchViewAs(), clearSession()
```

**Bootstrap optimization**:
- On mount, if current path is in `PUBLIC_PATHS` (`/`, `/login`, `/role-selection`, `/student-search`): skip `/me` call
- Otherwise: call `GET /api/auth/me` to restore session from HttpOnly cookie
- `localStorage.setItem("auth_hint", "1")` set on login, removed on logout
- Public pages check localStorage hint; if no hint set, skip auth check (avoids unnecessary /me call)

**Event-driven logout**:
- `api.ts` dispatches `ems:unauthorized` custom event on any 401 response
- `auth.store.tsx` listens for this event and calls `clearSession()`
- This covers cases where the token expires mid-session without user action

---

## 5. Token Storage

| Location | Content | Readable by JS? | Notes |
|---|---|---|---|
| HttpOnly cookie (`ems_session`) | Full JWT | NO | Set by backend; XSS-safe; sent automatically by browser |
| Response body (login endpoint) | Full JWT | YES | Legacy; for non-browser API clients only |
| localStorage (`auth_hint`) | "1" (flag only) | YES | Not a token; just a hint to skip /me call on public pages |
| Frontend React Context | `UserMe` object | YES | User info only (id, name, role); no JWT token value |

**Security note**: The JWT itself is stored only in the HttpOnly cookie. The frontend never reads or stores the raw JWT. The `auth_hint` flag in localStorage is not a token and contains no identity information.

---

## 6. Token Revocation

**Mechanism**: Token blacklisting via `RevokedToken` database table.

- On logout: `revoke_token(token)` computes `SHA-256(token)` and stores the hash in `RevokedToken`
- On every auth check: `is_token_revoked(token)` queries `RevokedToken` by hash
- Token blacklist is permanent until the `RevokedToken` row is deleted (no TTL currently — review for PDPA retention)
- Blacklist is checked in `_resolve_user_from_token()` before any request is processed

**Implications for Laravel bridge**: When the bridge creates an EMS JWT, that JWT must also be revokable via the same mechanism. Logout via EMS must blacklist the EMS JWT (this is already handled by the existing logout endpoint).

---

## 7. Existing CMU SSO Stub (`backend/cmu_sso.py`)

**Status**: INACTIVE — returns 503 "SSO not configured" unless env vars are set.

**What it does (when activated)**:
- `GET /api/auth/sso/login` → redirects to `oauth.cmu.ac.th/v1/Authorize.aspx` with:
  - `response_type=code`
  - `client_id=CMU_SSO_CLIENT_ID`
  - `redirect_uri=CMU_SSO_REDIRECT_URI`
  - `scope=cmuitaccount.basicinfo`
  - `state=ems_login`
- `GET /api/auth/sso/callback?code=...&state=...` → TODO (not implemented):
  1. POST to `oauth.cmu.ac.th/v1/GetToken.aspx` with code + client credentials
  2. GET `misapi.cmu.ac.th/cmuitaccount/v1/api/cmuitaccount/basicinfo` with access_token
  3. Map CMU itaccount email → User in DB
  4. Create JWT → redirect frontend

**Required env vars**:
- `CMU_SSO_CLIENT_ID` — from OIT
- `CMU_SSO_CLIENT_SECRET` — from OIT
- `CMU_SSO_REDIRECT_URI` — callback URL for EMS

**Known CMU API endpoints** (from stub):
- Auth: `https://oauth.cmu.ac.th/v1/Authorize.aspx`
- Token: `https://oauth.cmu.ac.th/v1/GetToken.aspx`
- User info: `https://misapi.cmu.ac.th/cmuitaccount/v1/api/cmuitaccount/basicinfo`

**Decision required before bridge implementation**:
- Activate `cmu_sso.py` (EMS handles CMU OAuth directly, no Laravel involvement)?
- Use Laravel bridge (Option B) and keep `cmu_sso.py` inactive?
- Both active (cmu_sso.py as fallback)?

This is documented as Blocker #9 in `PILOT_BLOCKER_DASHBOARD.md`.

---

## 8. What Must Change for Laravel Bridge

### Required changes (after contract verified):

| Change | Scope | Risk |
|---|---|---|
| New endpoint `GET /api/auth/bridge` to receive one-time code from Laravel | backend/routers/auth.py | Low — additive |
| Server-to-server call from EMS to Laravel to validate code and receive CMU email | New bridge logic in auth_utils.py or new module | Medium — requires working Laravel endpoint |
| Map CMU email → EMS user (upsert on first login) | backend/auth_utils.py or new mapper | Low — use existing user lookup by email |
| Add `cmu_email` as unique indexed field on EMS User table | DB migration | Low — additive migration |
| Activate `cmu_sso.py` callback implementation (if direct OAuth path selected) | backend/cmu_sso.py | Medium — requires OIT credentials |
| New env vars for bridge (`LARAVEL_BRIDGE_URL`, `LARAVEL_BRIDGE_SECRET` or OIT credentials) | .env + config | Low |
| Audit log entry for bridge login events | backend/auth_utils.py log_action | Low — extend existing function |

### Additive changes only — the following must NOT change:

| What | Why |
|---|---|
| Existing username/password login (`POST /api/auth/login`) | Keep as fallback during pilot; do not break existing admin/staff accounts |
| HttpOnly cookie pattern (`ems_session`) | Security invariant; all EMS auth must use HttpOnly cookies |
| Token blacklist mechanism (`RevokedToken` table) | Logout must continue to invalidate sessions |
| Role DB-authoritativeness | Role must always come from EMS DB, never from CMU token claims |
| Backend permission guards | Do not weaken or bypass any existing `require_*` guards |
| Audit logging | All auth events must be logged; bridge login must be added, not replace existing |
| PDPA data handling | CMU email is personal data; must comply with `PDPA_RETENTION_DAYS` |

---

## 9. Auth Files Summary

| File | Lines | Role | Bridge Impact |
|---|---|---|---|
| `backend/auth_utils.py` | 519 | JWT creation, cookie setting, token extraction, role guards, blacklist, audit logging | New bridge mapper; new log action type |
| `backend/routers/auth.py` | 167 | Login, me, view-as, logout endpoints | New /bridge endpoint |
| `backend/cmu_sso.py` | 54 | CMU OAuth stub (inactive) | Activate if direct OAuth path selected |
| `frontend/src/store/auth.store.tsx` | 179 | Auth state, signIn/signOut/refresh | Add CMU login trigger if bridge active |
| `frontend/src/components/layout/ProtectedRoute.tsx` | 33 | Frontend route guard (UX only) | No change |
| `frontend/src/services/api.ts` | 146 | HTTP client, cookie transport, 401 handler | No change |
| `frontend/src/utils/permissions.ts` | 149 | Role-based permission functions (UX only) | No change |

---

**End of EMS_CURRENT_AUTH_FLOW_AUDIT.md**
Read-only audit. No code was modified. All bridge changes require contract verification first.
