# EMS_AUTH_BRIDGE_DESIGN.md

**Date**: 2026-05-22
**Status**: DESIGN DRAFT — pending Laravel/CMU auth contract verification
**Purpose**: Define the safe target architecture for bridging EMS authentication with the Faculty LAN Server's Laravel/CMU email auth system. No bridge code may be written until the contract is verified.

---

## 1. Context

EMS currently uses its own username/password → JWT → HttpOnly cookie auth system (see `docs/architecture/EMS_CURRENT_AUTH_FLOW_AUDIT.md`). EMS also has an existing CMU SSO stub (`backend/cmu_sso.py`) that targets CMU OAuth at `oauth.cmu.ac.th` and the CMU MIS API at `misapi.cmu.ac.th/cmuitaccount`. This stub is currently inactive (returns 503 until OIT provides credentials).

The Faculty LAN Server runs PHP/Laravel with CMU email as the identity basis. The faculty web system has its own CMU auth flow using `AuthenController`, `session("USS")`, and a `cmu_at` token variable (all preliminary — see `FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md`).

The bridge must connect these two systems safely without exposing CMU tokens to the frontend, without trusting client-side identity claims, and without breaking the existing EMS login flow.

---

## 2. Preferred Target Architecture (Option B — Short-Lived Token Bridge)

Based on the options analysis in `EMS_LARAVEL_INTEGRATION_OPTIONS.md`, **Option B** is the preferred pattern.

### Step-by-Step Flow

```
Step 1 — User visits EMS on Faculty LAN
         User navigates to EMS (e.g., faculty-lan-server/ems)

Step 2 — Laravel AuthMiddleware gate
         Laravel checks session("USS")
         If not authenticated: redirects to CMU OAuth
         
Step 3 — CMU OAuth authentication
         User authenticates at oauth.cmu.ac.th
         CMU redirects to /callback/authen/ with auth code
         
Step 4 — AuthenController callback
         Laravel receives auth code (cmu_at or equivalent)
         Laravel validates token server-side against CMU auth server
         Laravel extracts CMU email from validated response
         session("USS") is set with verified user data
         
Step 5 — Laravel issues one-time bridge code
         Laravel generates a short-lived (30–60 second) one-time code
         Code is stored server-side (database or Redis) tied to the CMU email
         
Step 6 — Laravel redirects to EMS bridge endpoint
         Laravel sends user to: /api/auth/bridge?code=<one_time_code>
         The code is opaque — it does not contain CMU email or any identity data
         
Step 7 — EMS backend exchanges code for identity
         EMS backend receives the one-time code
         EMS backend calls Laravel internal endpoint (server-to-server, LAN only)
         Laravel validates the code, returns verified CMU email
         Laravel immediately invalidates the code (single use)
         
Step 8 — EMS maps identity to EMS user
         EMS queries EMS database by CMU email
         Finds (or creates) EMS user record
         Resolves EMS role from EMS database (DB-authoritative)
         
Step 9 — EMS issues its own session token
         EMS creates JWT with EMS user ID and active_role
         Sets HttpOnly cookie (ems_session) — consistent with current auth pattern
         Returns EMS user info to frontend
         
Step 10 — Normal EMS operation
          All subsequent EMS API calls use EMS JWT cookie
          No CMU token is ever used or referenced again
          cmu_at is never seen by EMS frontend
```

### Relation to Existing cmu_sso.py

The existing `backend/cmu_sso.py` stub implements a direct CMU OAuth flow (EMS calls CMU directly, not mediated by Laravel). Before building the Laravel bridge, the team must decide:

- **Path A (Activate cmu_sso.py)**: EMS handles CMU OAuth directly, using OIT-provided credentials. This bypasses Laravel entirely and would be used if the Faculty LAN Server cannot host the bridge endpoint. Requires `CMU_SSO_CLIENT_ID`, `CMU_SSO_CLIENT_SECRET`, `CMU_SSO_REDIRECT_URI` from OIT.

- **Path B (Laravel bridge via Option B)**: EMS uses the short-lived code bridge. `cmu_sso.py` remains inactive. This is the preferred approach if the Laravel owner can implement the code-issuance endpoint.

- **Path C (Both active)**: `cmu_sso.py` active as direct fallback if Laravel bridge fails. Adds complexity; consider only if resilience is required.

**Decision required**: Which path? (Document in `EMS_LARAVEL_INTEGRATION_OPTIONS.md` Decision section.)

---

## 3. Design Principles

| Principle | Rule |
|---|---|
| Never trust frontend email | CMU email must be verified server-side only; never read from URL params, localStorage, or request body |
| Never expose cmu_at | The CMU auth token must never be forwarded to or accessible by EMS frontend JavaScript |
| Never store raw CMU token unnecessarily | After CMU email is extracted, the cmu_at should be discarded or not stored by EMS |
| Role mapping is DB-authoritative | EMS role (admin, teacher, staff, etc.) is determined by the EMS database, never by email domain or token claims |
| Audit all bridge events | Every bridge login must be logged with CMU email, EMS user, EMS role, timestamp, IP — never the raw token |
| One-time code must expire | Bridge codes expire within 60 seconds and are invalidated immediately after successful exchange |
| Server-to-server only | The code-exchange call between EMS and Laravel must be LAN-internal, not accessible from the browser |
| Preserve existing login | EMS username/password login must remain available as a fallback during the pilot |

---

## 4. Data Model Mapping

After CMU email is verified by Laravel, EMS maps identity using this chain:

```
cmu_email (verified by Laravel)
    ↓
EMS User table (cmu_email as unique identifier field)
    ↓ (upsert on first login)
EMS user.id + user.active_role
    ↓
Role: admin / teacher / dept_supervisor / esq_head / secretary / staff / print_shop
    ↓
Permission set (from backend permission system in permissions.py)
```

Additional mappings (after EMS user is resolved):

| CMU Email Context | EMS Target Record | Notes |
|---|---|---|
| Faculty staff | `personnel` table | For staff/admin/secretary roles |
| Teacher | `teacher` table | For teacher role + department assignment |
| Student | (future) `student` table | If student exam schedule integration is added |

**Upsert rule**: On first CMU-email login, if no EMS user exists with that CMU email, create a new EMS user with a default role (e.g., `teacher` or `staff`). Role must be confirmed by an EMS admin before the user gains elevated permissions.

**Uniqueness constraint**: `cmu_email` must be a unique, indexed field in the EMS User table for this mapping to work safely. Verify this constraint exists before activating the bridge.

---

## 5. Risk Table

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Spoofed CMU email | Auth bypass — attacker claims someone else's email | Low (requires server access) | CMU email verified server-side only; never trust client-provided email |
| Leaked cmu_at token | Token abuse — attacker can impersonate user at CMU | Medium | Never forward cmu_at to EMS frontend; discard after identity extraction |
| Stale Laravel session | Ghost access — user logged out of CMU but EMS session still active | Medium | EMS session has its own lifetime; log out of EMS clears EMS JWT; coordinated logout recommended |
| Role mismatch | Privilege escalation — user gets wrong EMS role | Low | DB-authoritative only; admin must assign correct role; no role inference from email domain |
| Logout mismatch | Ghost session — user logs out of EMS but Laravel session persists (or vice versa) | Medium | Document logout flow; consider coordinated logout in future; for pilot, log out of both systems separately |
| Cookie domain mismatch | Auth failure — cookies not sent with requests | Medium | Verify domain/same-site policy with IT; test on Faculty LAN before pilot |
| Reverse proxy header spoofing | Auth bypass — attacker injects X-CMU-Email header | High if Option C not isolated | Use Option B (code exchange) instead; if Option C used, confirm EMS port unreachable externally |
| Duplicate user record | Data inconsistency — same person, two EMS users | Low | Use cmu_email as unique key; upsert not insert; check for existing records before creating |
| One-time code replay | Attacker reuses bridge code | Low (if implemented correctly) | Code expires in 60 seconds; single-use; invalidated immediately after exchange |
| Bridge endpoint exposed | Attacker calls EMS bridge endpoint directly | Low (internal only) | Server-to-server call only; EMS bridge endpoint should not be callable from browser |
| cmu_sso.py activated without OIT credentials | SSO stub panics or exposes error | Low | Stub already returns 503 gracefully; ensure `CMU_SSO_ENABLED=False` in production config if not activated |

---

## 6. Audit Event Specification

Every authentication event via the bridge must emit an audit log entry:

| Field | Value | Required |
|---|---|---|
| `action` | `"cmu_bridge_login"` | YES |
| `user_id` | EMS user ID (integer) | YES |
| `cmu_email` | Normalized CMU email (lowercase) | YES |
| `ems_role` | Role from EMS DB (not from token) | YES |
| `ip_address` | From request (X-Forwarded-For if behind proxy) | YES |
| `timestamp` | UTC ISO 8601 | YES |
| `session_id` or `request_id` | From request context if available | PREFERRED |
| `cmu_at` | — | NEVER |
| `session("USS")` raw | — | NEVER |
| `bridge_code` | — | NEVER |

Audit log is written to `AuditLog` table via the existing `log_action()` function in `backend/auth_utils.py`.

---

## 7. Prerequisites Checklist

Before writing any bridge code:

- [ ] Laravel auth contract answers received (LARAVEL_AUTH_CONTRACT_QUESTIONS.md completed)
- [ ] `session("USS")` payload verified against real Laravel codebase
- [ ] CMU email field name confirmed
- [ ] Integration option decided (A, B, C, or D)
- [ ] `cmu_sso.py` decision made (activate vs. bridge vs. deactivate)
- [ ] EMS User table `cmu_email` uniqueness constraint verified
- [ ] OIT credentials available if direct OAuth path is used
- [ ] One-time code storage mechanism agreed (Redis, DB table)
- [ ] Network isolation confirmed by IT (for Option C or server-to-server calls)
- [ ] DPO notified of CMU email data flow and storage

---

---

## 8A. Observed POLSCI OAuth Boundary (Added 2026-05-25)

Observed evidence from the faculty environment:

- Login endpoint: `https://account.pol.cmu.ac.th/oauth/login`
- Observed callback target via `ServiceUrl`: `https://portal.mis.pol.cmu.ac.th/oauth/callback`
- Login page wording indicates CMU Account / MS Entra ID through POLSCI infrastructure

Updated architectural interpretation:

1. The browser is redirected first to a faculty-owned POLSCI OAuth gateway.
2. The gateway returns to a faculty portal callback.
3. Faculty-side server logic is expected to validate the auth result and create a local session.
4. EMS must integrate after that faculty-side verification boundary.

What this does **not** prove:

- It does not prove what callback parameters are used.
- It does not prove that `cmu_at` exists in this implementation.
- It does not prove that EMS can own its own callback path yet.

Design rule:

**EMS must receive only verified identity or a one-time bridge artifact after faculty-side server validation. EMS must never rely on raw POLSCI OAuth artifacts in the browser.**

---

## 8B. Hybrid Auth Model: CMU Users and External Print Shop Users

### Lane A - CMU / POLSCI authenticated users

Applies to:

- admin
- staff
- secretary
- esq_head / executive
- dept_supervisor
- teacher
- student if student integration is later enabled

Identity source:

- Verified faculty-side session after POLSCI OAuth / CMU Account / MS Entra ID
- Expected EMS mapping key: verified CMU email

Authority rules:

- EMS database remains authoritative for role mapping
- Backend permissions remain authoritative for access decisions
- Frontend role state is for navigation and display only
- No client-provided email, role, or token claim is trusted

### Lane B - external print shop / partner users

Applies to:

- print shop
- external copy center
- controlled document handling partner

Current live-code context:

- EMS already contains a `print_shop` role
- EMS already contains a dedicated `/print-queue` route and backend printing endpoints guarded by `require_print_shop`
- Current code does not yet decide who owns the external identity source

Allowed identity model for this lane:

- `partner_account_id`
- `external_username`
- `partner_org`
- optional contact email
- CMU email is not required

Required restrictions for this lane:

- Access limited to assigned print queue and assigned print jobs
- Can update print status and acknowledge handoff / delivery
- Cannot access admin, staff, teacher, student, or governance dashboards
- Cannot receive broad export or general user-directory access
- Must be auditable at every login, document view/download, and state transition

PDPA design rule:

- Show the minimum metadata needed for print operations
- Prefer time-limited access for external partners
- Never reuse student-facing or internal CMU routes as a shortcut for print-shop access

---

**End of EMS_AUTH_BRIDGE_DESIGN.md**
No bridge code may be written until all prerequisites are checked. All contract items remain TBD.
