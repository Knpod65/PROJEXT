# PILOT_ROUTE_AND_AUTH_MAPPING.md

**Date**: 2026-05-22
**Status**: DRAFT — all routes marked PRELIMINARY until verified with Laravel owner and IT
**Purpose**: Document the proposed route mapping and middleware chain for EMS on the Faculty LAN Server alongside the PHP/Laravel faculty web system.

---

## 1. Known Preliminary Laravel Routes

> **PRELIMINARY — Verify every route against the actual Laravel codebase before configuring Nginx or integration.**

| Route | Component | Role | Verified? |
|---|---|---|---|
| `/user/student/...` | Faculty web — student section | Student access | NO — TBD |
| `/callback/authen/` | `AuthenController::callback()` | CMU OAuth callback handler | NO — TBD |
| (other faculty routes) | `AuthMiddleware` | All protected faculty routes | NO — TBD |

---

## 2. Proposed EMS Routes

The following EMS routes are proposed. Final paths must be agreed with the Laravel owner and IT before Nginx configuration.

### EMS Frontend (React SPA)

| Proposed Route | Purpose | Notes |
|---|---|---|
| `/ems` | EMS home / login | Entry point for EMS |
| `/ems/admin` | Admin dashboard | Protected — admin role |
| `/ems/staff` | Staff dashboard | Protected — staff/secretary/esq_head role |
| `/ems/teacher` | Teacher dashboard | Protected — teacher role |
| `/ems/student` | Student exam schedule | Protected — if student integration is added |
| `/ems/*` | All other EMS frontend routes | React Router handles sub-routes |

### EMS API (FastAPI backend)

| Proposed Route | Purpose | Notes |
|---|---|---|
| `/api/auth/...` | EMS auth endpoints (login, me, logout, bridge) | Proxied to EMS backend |
| `/api/...` | All EMS API endpoints | Proxied to EMS backend via Nginx |

### Alternative: Separate Subdomain

If Nginx path-based routing is complex, EMS may be served under a separate subdomain:

- `ems.faculty-lan-server.local` (EMS frontend + API)
- This avoids cookie domain conflicts but requires subdomain DNS setup on Faculty LAN

**Decision required**: Path-based (`/ems`) or subdomain? See Section 4 for open questions.

---

## 3. Proposed Nginx Proxy Configuration (Concept Only — Not Verified)

The following is a conceptual Nginx routing sketch. Actual configuration must be written and verified by IT.

```
# Conceptual Nginx sketch — NOT production configuration
# Verify all paths and settings with IT before deployment

server {
    # Faculty web (Laravel) — existing
    location / {
        proxy_pass http://localhost:8000;  # Laravel PHP-FPM or equivalent
    }

    # EMS frontend static files
    location /ems {
        root /path/to/ems/frontend/dist;  # TBD
        try_files $uri $uri/ /ems/index.html;
    }

    # EMS API — proxy to FastAPI backend
    location /api {
        proxy_pass http://localhost:8001;  # EMS FastAPI port — TBD
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        # Do NOT add X-CMU-Email header unless Option C is selected and IT confirms isolation
    }
}
```

All values (ports, paths) are TBD. This sketch is for discussion only.

---

## 4. Open Questions on Route Mounting

| # | Question | Status |
|---|---|---|
| Q1 | Should EMS frontend be served by the Laravel Nginx server, or on a separate port? | OPEN |
| Q2 | Should EMS API remain on a separate FastAPI process? What port? | OPEN |
| Q3 | Should Nginx proxy `/api/...` to the EMS FastAPI backend? | OPEN |
| Q4 | Should `/user/student/...` eventually link into EMS student exam schedule? | OPEN |
| Q5 | Should teacher/staff/admin go through the same Laravel `AuthMiddleware` before reaching EMS? | OPEN |
| Q6 | Is path-based routing (`/ems`) or subdomain routing preferred? | OPEN |
| Q7 | What is the exact Nginx config for the Faculty LAN server? | OPEN |
| Q8 | Should EMS frontend be built and deployed as static files, or served differently? | OPEN |

---

## 5. Middleware Mapping

### Laravel Middleware (Faculty Web)

| Middleware | Scope | Function |
|---|---|---|
| `AuthMiddleware` | Faculty web routes | Checks `session("USS")` — blocks unauthenticated access |
| (Other Laravel middleware) | Various routes | TBD from Laravel codebase |

### EMS Backend Middleware (FastAPI)

| Guard | Scope | Function |
|---|---|---|
| `resolve_request_auth()` | All protected EMS API routes | Extracts and validates EMS JWT from HttpOnly cookie or Bearer header |
| `require_admin()` | Admin-only API routes | Role guard — blocks non-admin |
| `require_staff_or_admin()` | Staff-level API routes | Role guard — blocks non-staff, non-admin |
| `require_view_all()` | Cross-department data routes | Requires admin, esq_head, or secretary |
| `assert_dept_access()` | Department-filtered routes | Supervisor/teacher can only access own department data |

### EMS Frontend Route Guards (React)

| Guard | Scope | Function |
|---|---|---|
| `ProtectedRoute` | All EMS frontend routes except public | Redirects to login if no authenticated user in context |
| `permissions.ts` functions | UI feature visibility | Hides/shows features based on active role |

### IMPORTANT: Middleware Authority

```
Frontend route protection (ProtectedRoute, permissions.ts) = UX ONLY
Backend permission guards (require_admin, etc.) = AUTHORITATIVE
```

Frontend guards prevent navigation to pages the user should not see. They do NOT prevent API access. A user who bypasses frontend route guards will still be blocked by the backend permission middleware on any actual API call.

Role enforcement is always the backend's responsibility. The frontend UI reflects backend-enforced role state; it does not enforce it independently.

---

## 6. Auth Flow in Context of Route Mapping

```
User visits /ems (Faculty LAN)
    ↓
Nginx serves EMS React frontend (static files)
    ↓
EMS frontend ProtectedRoute checks: is user authenticated in EMS context?
    ↓ (no)
Redirect to EMS login page (/ems/login or /)
    ↓
[If Laravel bridge is active]
EMS login page shows "Login with CMU" button
    ↓
Browser is redirected to Laravel CMU auth route
    ↓
Laravel AuthMiddleware → CMU OAuth → callback → session("USS") set
    ↓
Laravel redirects to EMS bridge endpoint (/api/auth/bridge?code=...)
    ↓
EMS backend exchanges code → maps CMU email → creates EMS JWT
    ↓
EMS frontend is now authenticated — ProtectedRoute passes
    ↓
All subsequent /api/... calls carry EMS JWT cookie automatically
    ↓
EMS backend guards enforce permissions on every API call
```

---

## 7. Cookie and Domain Considerations

For EMS JWT cookies to be sent automatically with `/api/...` requests, the following must be true:

| Requirement | Notes |
|---|---|
| EMS frontend and EMS API must share the same origin OR same domain | If served under `/ems` and `/api` on the same server, this is automatic |
| Cookie `Domain` attribute must match the server hostname | Verify with IT — `localhost` vs. actual hostname |
| Cookie `SameSite` must be `Lax` or `Strict` for same-origin | Verify this is configured in EMS JWT cookie settings |
| Cookie `Secure` flag requires HTTPS | If Faculty LAN uses HTTP only, Secure flag must be disabled for pilot — note as security debt |
| Laravel session cookie domain must not conflict with EMS JWT cookie | Verify with Laravel owner if same domain is used |

**All cookie settings must be verified on the actual Faculty LAN server before the auth bridge rehearsal (Stage 4 of the implementation plan).**

---

**End of PILOT_ROUTE_AND_AUTH_MAPPING.md**
All routes and configurations marked PRELIMINARY. No Nginx configuration should be deployed without IT review and verification.
