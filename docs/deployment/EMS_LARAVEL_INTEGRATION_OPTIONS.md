# EMS_LARAVEL_INTEGRATION_OPTIONS.md

**Date**: 2026-05-22
**Purpose**: Compare integration options for running EMS alongside the Faculty LAN Server's Laravel/CMU auth system. An option must be selected and verified before integration code is written.

---

## Summary Table

| Option | Name | Safety | Complexity | Recommendation |
|---|---|---|---|---|
| A | Laravel as Auth Gateway + EMS behind protected route | Medium (requires session bridge) | Medium | Viable if session contract verified |
| B | Laravel issues short-lived EMS backend token | High | Medium | **Preferred** — clean API boundary |
| C | Reverse proxy injects trusted internal headers | High only if fully isolated | Low | Only if header spoofing provably blocked |
| D | EMS keeps separate login (CMU email as identifier only) | Low (duplicate auth) | Very Low | Temporary pilot fallback only |

---

## Option A — Laravel as Auth Gateway, EMS behind Protected Route

### Description

Laravel handles CMU login and session. EMS (FastAPI backend + React frontend) is served after the user has passed through `AuthMiddleware`. Laravel passes the verified user identity to EMS via a server-side mechanism (shared session, internal API call, or signed cookie).

### Flow

```
User → Laravel AuthMiddleware → (if not logged in) CMU OAuth → callback
     → session("USS") set → user reaches EMS-served page
     → EMS backend reads identity from Laravel session or secure bridge
     → EMS issues its own internal session token
     → EMS API requests use EMS token (HttpOnly cookie)
```

### Pros

- Fits into existing faculty web infrastructure
- Lower user friction (single login experience)
- CMU auth is maintained centrally by Laravel
- EMS frontend can be served by Laravel's Nginx/web server

### Cons

- EMS backend must read or verify the Laravel session, which requires a shared session driver or a server-to-server check endpoint
- Session sharing across frameworks (PHP Laravel ↔ Python FastAPI) adds complexity
- Cookie domain must be aligned
- Requires verified contract for `session("USS")` payload

### Required Contract Items

- `session("USS")` exact structure (user ID, CMU email field)
- Laravel session driver and storage location (file, database, Redis)
- Cookie domain and SameSite policy
- A safe read mechanism for EMS to verify the session (shared Redis, internal API, signed session token)

### Safety Considerations

- EMS must never read the Laravel session directly from the file system without a secure channel
- EMS must verify the session exists and is current, not just trust a forwarded value
- If session driver is Redis, share access must be restricted to internal network only

---

## Option B — Laravel Issues Short-Lived EMS Backend Token (Preferred)

### Description

After CMU authentication succeeds and `session("USS")` is set, Laravel calls or redirects to an internal EMS backend endpoint with a one-time, server-generated, short-lived code. The EMS backend exchanges this code for the verified CMU identity (never touching the raw cmu_at), creates an EMS user session, and issues an EMS JWT in an HttpOnly cookie. No CMU token is ever forwarded to the EMS frontend.

### Flow

```
User → Laravel CMU auth → callback → session("USS") set
     → Laravel generates short-lived one-time code (server-side)
     → Laravel redirects user to EMS at /api/auth/bridge?code=<otp>
     → EMS backend receives code
     → EMS backend calls Laravel internal endpoint (server-to-server) to validate code
     → Laravel returns verified CMU email (and optionally user_id)
     → EMS maps CMU email → EMS user/role from EMS DB
     → EMS creates JWT → sets HttpOnly cookie → returns user to EMS frontend
     → All subsequent EMS API calls use EMS JWT cookie (no CMU token involved)
```

### Pros

- Clean boundary between Laravel auth and EMS auth
- cmu_at never leaves Laravel server
- No shared session driver required
- EMS auth system remains self-contained after the bridge step
- Consistent with EMS existing HttpOnly cookie pattern
- One-time code prevents replay attacks (if short-lived and invalidated after use)

### Cons

- Requires a new internal endpoint on the Laravel side (short-lived code issuance and validation)
- Requires coordination with Laravel owner to implement the code-exchange endpoint
- More implementation work than Option A or C

### Required Contract Items

- Laravel owner agrees to implement an internal code-issuance endpoint
- Code lifetime agreed (e.g., 30–60 seconds)
- Code is invalidated immediately after EMS exchanges it
- Internal endpoint is accessible only on Faculty LAN (not public)
- CMU email field name in Laravel's verified user response

### Safety Considerations

- One-time code must expire quickly (30–60 seconds)
- Code endpoint must require the Laravel session to exist before issuing
- EMS backend call to Laravel must be server-to-server only (not from frontend)
- Code must be invalidated immediately after a successful exchange
- Log the exchange event (not the code itself)

---

## Option C — Reverse Proxy Injects Trusted Internal Headers

### Description

The Nginx (or equivalent) reverse proxy validates that the user has a valid Laravel session and injects an internal header (e.g., `X-CMU-Email: user@cmu.ac.th`) before forwarding requests to the EMS backend. EMS trusts this header because it is on an internal network path that external requests cannot reach.

### Flow

```
User → Nginx (Faculty LAN internal)
     → Nginx checks Laravel session validity (via auth_request or similar)
     → If valid: injects X-CMU-Email header
     → Forwards to EMS FastAPI backend
     → EMS reads X-CMU-Email from trusted internal header
     → EMS maps CMU email → EMS user/role from EMS DB
     → EMS issues its own JWT cookie
```

### Pros

- Very simple for EMS backend (no code-exchange needed)
- No shared session driver required
- Laravel/CMU auth remains entirely separate from EMS internals

### Cons

- DANGEROUS if the EMS backend is ever accidentally exposed outside the proxy (header can be spoofed)
- Requires strict network controls — EMS backend port must be unreachable except via the internal proxy
- Requires Nginx `auth_request` configuration or similar, which requires IT expertise
- EMS cannot independently verify that the header was not forged

### Condition for Use

Option C is acceptable ONLY if ALL of the following are true:
1. EMS FastAPI backend port is bound to `127.0.0.1` only (not exposed to LAN directly)
2. All requests to EMS must pass through the Nginx reverse proxy
3. No external access is possible to the EMS backend port
4. IT owner explicitly confirms and documents the network isolation
5. The Faculty LAN network boundary is confirmed to prevent spoofed headers

### Required Contract Items

- IT confirms network isolation (EMS backend not directly accessible)
- Nginx `auth_request` or equivalent configured
- Exact header name and value format confirmed
- IT documents the network topology proving isolation

---

## Option D — EMS Keeps Separate Login, CMU Email as Identifier Only

### Description

EMS login remains entirely separate. Users log in to EMS directly using their CMU email as their username. EMS does not integrate with Laravel session. The link between CMU email and EMS user is maintained only by the EMS user table. Users must log in twice (once to faculty web, once to EMS).

### Flow

```
User → EMS login page → enters CMU email + EMS password
     → EMS validates credentials from EMS DB
     → EMS issues JWT HttpOnly cookie
     → EMS frontend loaded
```

### Pros

- Fastest technically — no integration work needed
- No dependency on Laravel auth contract
- EMS remains completely self-contained

### Cons

- Worst user experience — two separate logins
- Not aligned with faculty web integration goal
- Users may have weak or forgotten EMS-specific passwords
- Does not leverage CMU auth as the identity source
- Pilot goal of integrating with faculty web is not met

### When Acceptable

Option D is acceptable ONLY as a temporary pilot fallback if:
- The Laravel auth contract cannot be verified before the pilot start date
- The Laravel owner is unavailable for integration coordination
- Pilot must proceed with the current EMS auth system unchanged

**If Option D is used for the pilot**, the integration work (Option A or B) must be scheduled immediately after.

---

## Recommendation

**Prefer Option B** (Laravel issues short-lived EMS backend token) for the following reasons:

- Clean boundary: cmu_at never leaves Laravel
- EMS remains self-contained after the bridge step
- Consistent with EMS security design (HttpOnly JWT cookie)
- No shared session driver complexity
- One-time code pattern is safe and well-understood

**Accept Option A** if the Laravel owner cannot implement a code-exchange endpoint and the session contract is fully verified.

**Accept Option C** only after IT explicitly documents and confirms network isolation — never assume it is safe.

**Accept Option D** only as a temporary fallback if the pilot cannot wait for integration.

---

## Decision (To Be Filled)

| Field | Value |
|---|---|
| Selected Option | TBD |
| Decision Date | TBD |
| Decision Owner | TBD |
| Rationale | TBD |
| Conditions Met | TBD |

---

**End of EMS_LARAVEL_INTEGRATION_OPTIONS.md**
No integration code may be written until an option is selected and its required contract items are verified.
