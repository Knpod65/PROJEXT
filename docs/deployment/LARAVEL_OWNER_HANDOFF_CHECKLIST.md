# LARAVEL_OWNER_HANDOFF_CHECKLIST.md

**Date**: 2026-05-22
**Purpose**: Final handoff checklist for the Laravel / CMU auth contract before EMS auth bridge implementation. Nothing is marked COMPLETE. All items require evidence from the real Laravel codebase.
**Status**: SEND — not yet transmitted to owner

---

## A. Required Laravel Files / Snippets to Inspect

The Laravel / IT owner must make these files available (or provide sanitized snippets with all secrets removed).

| # | File / Item | What to extract | Status |
|---|-------------|----------------|--------|
| A1 | `routes/web.php` | Auth route definitions — login, CMU callback, student routes, EMS mount path | SENT / PARTIAL / COMPLETE |
| A2 | AuthMiddleware class | What checks it runs on each request; what it reads from session | SENT / PARTIAL / COMPLETE |
| A3 | `AuthenController::callback()` | Exact callback route path, HTTP method, what it does with CMU response | SENT / PARTIAL / COMPLETE |
| A4 | Session creation logic | Where and how `session("USS")` or equivalent is set; what fields are stored | SENT / PARTIAL / COMPLETE |
| A5 | CMU token validation | How `cmu_at` is validated server-side; what library or endpoint is called | SENT / PARTIAL / COMPLETE |
| A6 | `Auth::routes()` or logout route | Exact logout URL path and what it does | SENT / PARTIAL / COMPLETE |
| A7 | `config/session.php` + `config/cookie.php` | Cookie name, Domain, SameSite, Secure, HttpOnly, Path | SENT / PARTIAL / COMPLETE |
| A8 | `config/auth.php` | User provider and credentials guard relevant to CMU / external auth | SENT / PARTIAL / COMPLETE |
| A9 | `.env` sample (sanitized) | Session driver, cookie domain, CMU OAuth base URL (no secrets) | SENT / PARTIAL / COMPLETE |
| A10 | Nginx or server config (sanitized) | Reverse proxy settings, proxy paths for EMS API | SENT / PARTIAL / COMPLETE |

---

## B. Required Route Answers

**Do not proceed to auth bridge implementation until all items below are confirmed with real code evidence.**

| # | Question | Answer | Status |
|---|----------|--------|--------|
| B1 | Exact CMU OAuth callback route URL and HTTP method | TBD | OPEN |
| B2 | Exact protected faculty route where EMS should be served | TBD | OPEN |
| B3 | Exact EMS frontend mount path (e.g. `/ems`, `/exam`, subdomain) | TBD | OPEN |
| B4 | EMS API proxy path (e.g. `/api/proxy → EMS FastAPI`) | TBD | OPEN |
| B5 | Student route path(s) under `/user/student/...` | TBD | OPEN |
| B6 | Logout route URL | TBD | OPEN |
| B7 | AuthMiddleware name, config | TBD | OPEN |
| B8 | Laravel server hostname / IP (for EMS bridge endpoint call) | TBD | OPEN |
| B9 | Whether `AuthMiddleware` must be bypassed for EMS routes or inherited | TBD | OPEN |

---

## C. Required Session Answers

| # | Question | Answer | Status |
|---|----------|--------|--------|
| C1 | Exact session key for the authenticated user — is it `session("USS")` or different? | TBD | OPEN |
| C2 | What fields does the session value contain? (list exact keys) | TBD | OPEN |
| C3 | Is the CMU email directly stored in the session value? | TBD | OPEN |
| C4 | Is personnel/employee ID stored in the session value? | TBD | OPEN |
| C5 | Is student ID stored in the session value? | TBD | OPEN |
| C6 | Is a role stored in the session value? | TBD | OPEN |
| C7 | Session lifetime (minutes or hours) | TBD | OPEN |
| C8 | Session driver (file, database, Redis, cookie) | TBD | OPEN |
| C9 | Cookie name for the session cookie | TBD | OPEN |
| C10 | Cookie Domain attribute | TBD | OPEN |
| C11 | SameSite policy (Strict, Lax, None) | TBD | OPEN |
| C12 | Secure flag set? | TBD | OPEN |
| C13 | HttpOnly flag set? | TBD | OPEN |

---

## D. Required Token Answers

| # | Question | Answer | Status |
|---|----------|--------|--------|
| D1 | What exactly is `cmu_at` in your system? | TBD | OPEN |
| D2 | Is it a CMU OAuth access token? | TBD | OPEN |
| D3 | Is it a short-lived authorization code or longer-lived access token? | TBD | OPEN |
| D4 | Where is `cmu_at` validated — at the CMU OAuth server or locally? | TBD | OPEN |
| D5 | Is `cmu_at` stored in the database after the callback? | TBD | OPEN |
| D6 | Is `cmu_at` discarded after the CMU email is extracted? | TBD | OPEN |
| D7 | Is there a refresh token? | TBD | OPEN |
| D8 | Is `cmu_at` or any CMU token ever forwarded to any frontend page or JavaScript? Answer must be NO. | TBD | OPEN |
| D9 | What CMU API is called to get user info from the token? | TBD | OPEN |

---

## E. Required Database / Deployment Answers

| # | Question | Answer | Status |
|---|----------|--------|--------|
| E1 | Which PostgreSQL instance will EMS use? (host, port, database name) | TBD | OPEN |
| E2 | Will EMS share the faculty Laravel database or use a separate database? | TBD | OPEN |
| E3 | If separate: who owns and provisions the EMS database? | TBD | OPEN |
| E4 | Who owns EMS database migrations? | TBD | OPEN |
| E5 | Who is responsible for EMS database backup? | TBD | OPEN |
| E6 | Will the EMS FastAPI backend run on the same server as Laravel or a separate server/VM/Docker container? | TBD | OPEN |
| E7 | Deployment model (Docker Compose, systemd, direct Python service)? | TBD | OPEN |
| E8 | EMS FastAPI backend listening port | TBD | OPEN |
| E9 | Will Nginx proxy `/api/...` to the EMS FastAPI backend? | TBD | OPEN |

---

## F. Required Security Confirmations

| # | Confirmation Required | Confirmed? | Notes |
|---|-----------------------|------------|-------|
| F1 | `cmu_at` is NEVER exposed to any EMS frontend JavaScript | TBD | No — must be YES |
| F2 | Frontend never sends raw CMU email or `cmu_at` as an identity proof — EMS backend reads identity only from verified session or server-to-server call | TBD | Must be YES |
| F3 | EMS role is determined from EMS database only — never from client-provided claims or email domain | TBD | Must be YES |
| F4 | LMS backend performs DB-authoritative role mapping after CMU email is verified | TBD | Must be YES |
| F5 | Auth bridge events are audited — no tokens logged in logs | TBD | Must be YES |
| F6 | CSRF is enabled for LMS routes EMS will interact with | TBD | Must be YES |
| F7 | EMS backend port is firewalled from direct LAN access (only via Nginx proxy) | TBD | Must be YES |
| F8 | DPO is notified of CMU email identity data flow before pilot | TBD | Must be YES |

---

## G. Required Evidence Summary

The following must be received from the LMS owner before contract can be marked COMPLETE:

| # | Evidence Item | Status |
|---|--------------|--------|
| G1 | Sanitized route list output from LMS | OPEN |
| G2 | Session payload example with dummy values (no real user data) | OPEN |
| G3 | AuthMiddleware code or behavioral summary | OPEN |
| G4 | AuthenController callback summary with dummy flow | OPEN |
| G5 | `config/session.php` and `config/cookie.php` values (sanitized) | OPEN |
| G6 | Confirmed PostgreSQL target (yes/no on using LMS DB vs separate DB; separate DB strongly recommended) | OPEN |
| G7 | Confirmations on security items F1 — F8 | OPEN |
| G8 | Designated contact person / owner name and contact | OPEN |

---

**Do not mark any row as COMPLETE until real code evidence is verified. This checklist is the hard gate.**

---

**End of LARAVEL_OWNER_HANDOFF_CHECKLIST.md**
