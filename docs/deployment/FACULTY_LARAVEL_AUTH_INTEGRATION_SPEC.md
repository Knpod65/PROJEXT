# FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md

**Date**: 2026-05-22
**Status**: DRAFT — pending verification against actual Laravel codebase
**Purpose**: Specification for integrating EMS with the Faculty LAN Server's PHP/Laravel + CMU email authentication system.

---

## 1. Purpose

EMS pilot will run on the Faculty LAN Server. The faculty's primary web system is built with PHP/Laravel and uses CMU email as the identity basis through CMU OAuth. This document specifies the integration approach, documents known preliminary information from the faculty-side auth system, and lists all contract items that must be verified before any integration code is written.

**Key constraint**: No integration code may be written until the Laravel/CMU auth contract is verified. The existing EMS username/password login must remain intact as a fallback for the pilot period.

---

## 2. Known Preliminary Routes and Components

> **PRELIMINARY — These are early notes from the faculty side. Verify every item against the actual Laravel codebase before implementation.**

| Component | Preliminary Value | Verified? |
|---|---|---|
| Student route prefix | `/user/student/...` | NO — TBD |
| CMU auth callback route | `/callback/authen/` | NO — TBD |
| Auth middleware | `AuthMiddleware` | NO — TBD |
| Auth controller | `Auth` / `AuthenController` | NO — TBD |
| Callback function | `callback()` | NO — TBD |
| Session key for user | `session("USS")` | NO — TBD |
| CMU token variable | `cmu_at` | NO — TBD |
| Primary identity field | CMU email | NO — TBD (exact field name TBD) |

**Note on EMS existing SSO stub**: EMS already contains `backend/cmu_sso.py`, a stub for CMU OAuth2 using `oauth.cmu.ac.th` and `misapi.cmu.ac.th/cmuitaccount/v1/api/cmuitaccount/basicinfo`. This stub requires `CMU_SSO_CLIENT_ID`, `CMU_SSO_CLIENT_SECRET`, and `CMU_SSO_REDIRECT_URI` from OIT. The stub must be reviewed and potentially activated rather than duplicated when the Laravel bridge is implemented.

---

## 3. Expected Authentication Flow (Proposed — Not Verified)

The following flow is a reasonable expectation based on the preliminary notes. It must be confirmed against the real Laravel implementation.

```
User visits faculty web route
    ↓
Laravel AuthMiddleware checks session("USS")
    ↓ (not authenticated)
Laravel redirects user to CMU authentication endpoint
    ↓
User authenticates at CMU
    ↓
CMU returns to /callback/authen/ with auth code or token
    ↓
AuthenController::callback() receives cmu_at or equivalent
    ↓
Laravel validates cmu_at server-side (against CMU auth server)
    ↓
Laravel extracts CMU email from validated response
    ↓
Laravel creates/updates server-side session
    ↓
session("USS") is set with authenticated user data
    ↓
AuthMiddleware now passes on subsequent requests
    ↓
EMS access is granted only after server-side session is verified
```

**Critical**: The EMS backend must not rely on any client-provided identity claim. The bridge between Laravel session and EMS session must be server-side only.

---

## 4. EMS Integration Boundary

### EMS Must NOT Trust

- Frontend localStorage tokens or session data
- Raw URL parameters containing email or role
- Unsigned or unverified email parameters from any source
- Client-provided role claims
- Client-provided access tokens (including cmu_at if somehow forwarded)
- Cookie values that are not verified server-side

### EMS May Trust (subject to verified contract)

- Server-verified Laravel session, confirmed by direct session check or secure server-to-server call
- A backend-issued short-lived EMS token, minted only after Laravel-side identity verification
- A trusted reverse proxy internal header, ONLY if restricted to Faculty LAN internal network with no external access and no possibility of header spoofing — must be confirmed by IT

### EMS Maintains

- Its own internal session/token after identity verification
- Its own role resolution from the EMS database
- Its own audit logging for all access events

---

## 5. Identity Mapping

**Primary identity key**: CMU email (exact field name TBD — see Section 6 for questions)

After CMU email is verified by Laravel, EMS must map it to:

| Identity Field | EMS Target | Notes |
|---|---|---|
| `cmu_email` | `personnel` record | For staff/admin/secretary |
| `cmu_email` | `teacher` record | For teacher role |
| `cmu_email` | `student` record | If student route integration is needed |
| `cmu_email` | EMS `user` record | Primary auth record |
| EMS `user` → `active_role` | EMS role | DB-authoritative, not inferred from email domain |
| EMS role | Permission set | From EMS permission system |

**Rule**: Role must remain EMS-DB-authoritative. Admin/staff/teacher role must not be inferred solely from email domain or email pattern. The mapping must be maintained in the EMS user table with explicit role assignment by EMS administrators.

---

## 6. Session Contract Questions

The following must be answered by the Laravel owner before integration proceeds:

| Question | Status |
|---|---|
| What exactly is stored in `session("USS")`? | OPEN |
| Is it user id, CMU email, array/object, or serialized user? | OPEN |
| Does `session("USS")` contain CMU email directly? | OPEN |
| Does it contain personnel ID or student ID? | OPEN |
| Does it contain a role? | OPEN |
| Session lifetime (minutes/hours)? | OPEN |
| Session driver (file, database, Redis, cookie)? | OPEN |
| Session cookie name? | OPEN |
| SameSite policy (Strict/Lax/None)? | OPEN |
| Cookie domain? | OPEN |
| Secure flag (HTTPS required)? | OPEN |
| HttpOnly flag? | OPEN |
| CSRF token implementation? | OPEN |

---

## 7. Token Contract Questions

The following must be answered about `cmu_at`:

| Question | Status |
|---|---|
| What is `cmu_at`? | OPEN |
| Is it a CMU OAuth access token? | OPEN |
| Is it a short-lived authorization code? | OPEN |
| Where is it validated (Laravel server-side or external call)? | OPEN |
| Is `cmu_at` stored after callback? | OPEN |
| Is it discarded after CMU email is extracted? | OPEN |
| Is there a refresh token? | OPEN |
| Is `cmu_at` or any token ever sent to a frontend page? | OPEN |

**Requirement**: `cmu_at` must never be exposed to the EMS frontend JavaScript or any client-side storage. If it is an OAuth access token, it must be treated as a server-side secret and discarded or secured after identity extraction.

**Note**: EMS `cmu_sso.py` stub references `oauth.cmu.ac.th/v1/GetToken.aspx` for token exchange and `misapi.cmu.ac.th/cmuitaccount/v1/api/cmuitaccount/basicinfo` for user info. If the faculty Laravel side uses a different CMU OAuth flow, the integration approach must account for both.

---

## 8. Logout Behavior

Questions for the Laravel owner:

| Question | Status |
|---|---|
| What is the Laravel logout route? | OPEN |
| Does Laravel logout invalidate the CMU session or only the local session? | OPEN |
| Should EMS logout also call Laravel logout? | OPEN |
| Should EMS redirect to a faculty logout URL after logout? | OPEN |
| Should a single-logout flow be implemented (EMS + Laravel + CMU)? | OPEN |
| If session expires in Laravel but not in EMS, what happens? | OPEN |

**Recommendation**: Coordinate logout behavior to avoid ghost sessions. At minimum, EMS logout should revoke the EMS token/session. Single-logout is a future enhancement.

---

## 9. Audit Requirements

EMS must log the following for every login via the Laravel/CMU bridge:

| Audit Field | Required | Notes |
|---|---|---|
| Login method | YES | "laravel_cmu_bridge" or "direct_login" |
| Mapped CMU email | YES | Normalized, lowercase |
| EMS user ID | YES | After mapping |
| EMS role used | YES | From DB, not from client |
| Login timestamp | YES | UTC |
| IP address | YES | If available from request |
| Request/session ID | YES | If available |
| cmu_at or raw token | NO | Must NOT be logged |
| session("USS") raw value | NO | Must NOT be logged |

Audit records must be stored in the EMS `AuditLog` table. Log retention must comply with PDPA data retention policy (`PDPA_RETENTION_DAYS`).

---

## 10. Prerequisites Before Integration Code Is Written

- [ ] Laravel owner confirms exact callback route
- [ ] Laravel owner confirms `session("USS")` payload structure
- [ ] Laravel owner confirms CMU email field name
- [ ] IT confirms PostgreSQL deployment target
- [ ] IT confirms deployment method (same server, Docker, Nginx proxy)
- [ ] IT confirms SSL/LAN policy
- [ ] EMS `cmu_sso.py` stub reviewed and decision made (activate vs. new bridge)
- [ ] CMU OIT credentials obtained (`CMU_SSO_CLIENT_ID`, `CMU_SSO_CLIENT_SECRET`) if EMS direct OAuth is used
- [ ] Auth bridge option selected from EMS_LARAVEL_INTEGRATION_OPTIONS.md
- [ ] DPO notified of CMU email data flow

---

**End of FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md**
This document is DRAFT. No values have been fabricated. All contract items require verification.
