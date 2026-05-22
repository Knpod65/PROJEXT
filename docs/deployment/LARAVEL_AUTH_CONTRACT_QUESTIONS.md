# LARAVEL_AUTH_CONTRACT_QUESTIONS.md

**Date**: 2026-05-22
**Purpose**: Structured questions to ask the IT/Laravel owner before EMS-to-Laravel integration begins. All items are OPEN until answered and verified against the real Laravel codebase.
**Owner**: EMS team — send to Faculty IT owner and Laravel code owner for answers.

---

## How to Use This Document

1. EMS team sends this document to the Faculty IT owner and Laravel code owner.
2. Owners fill in the "Answer" column for each question.
3. Filled answers are returned to EMS team.
4. EMS team verifies answers against actual code/config before writing integration.
5. Do NOT include actual secret values (passwords, tokens, keys) in this document.

---

## A. Routes

| # | Question | Answer | Notes |
|---|---|---|---|
| A1 | What is the exact URL path that handles CMU OAuth callback? Is it `/callback/authen/` or different? | TBD | |
| A2 | Is the callback route a GET or POST? | TBD | |
| A3 | What route prefix should EMS be mounted under? (`/ems`, `/exam`, separate subdomain?) | TBD | |
| A4 | Should EMS frontend be served by Laravel's web server (Nginx)? Or separate port? | TBD | |
| A5 | Should the EMS API (`/api/...`) be proxied through Nginx to the EMS FastAPI backend? | TBD | |
| A6 | Are there existing routes under `/user/student/...` that should eventually link into EMS student exam schedule? | TBD | |
| A7 | What is the Laravel logout route? | TBD | |
| A8 | Does any existing route protect access via `AuthMiddleware` that EMS would be served behind? | TBD | |

---

## B. Session

| # | Question | Answer | Notes |
|---|---|---|---|
| B1 | What exact key is used to store the authenticated user in the Laravel session? Is it `session("USS")` or different? | TBD | |
| B2 | What fields does the session value contain? (user_id, email, name, role, personnel_id, student_id, etc.) | TBD | |
| B3 | Is the CMU email directly included in the session value? | TBD | |
| B4 | Is personnel ID or student ID included in the session value? | TBD | |
| B5 | Is a role included in the session value? | TBD | |
| B6 | What is the session lifetime in minutes? | TBD | |
| B7 | What session driver is used? (file, database, Redis, cookie) | TBD | |
| B8 | What is the session cookie name? | TBD | |
| B9 | What is the SameSite policy? (Strict / Lax / None) | TBD | |
| B10 | What is the cookie domain? (e.g., `.cmu.ac.th`, `.faculty.cmu.ac.th`, `localhost`) | TBD | |
| B11 | Is the Secure flag set? (HTTPS required?) | TBD | |
| B12 | Is the HttpOnly flag set? | TBD | |
| B13 | How is CSRF handled? (Laravel CSRF token in form / X-CSRF-TOKEN header?) | TBD | |

---

## C. Token

| # | Question | Answer | Notes |
|---|---|---|---|
| C1 | What exactly is `cmu_at` in the context of your system? | TBD | |
| C2 | Is it a CMU OAuth access token (from `oauth.cmu.ac.th`)? | TBD | |
| C3 | Is it a short-lived authorization code or a longer-lived access token? | TBD | |
| C4 | Where is `cmu_at` validated — against CMU OAuth server, or locally? | TBD | |
| C5 | Is `cmu_at` stored in the database after the callback? | TBD | |
| C6 | Is `cmu_at` discarded after CMU user info is extracted? | TBD | |
| C7 | Is there a refresh token? | TBD | |
| C8 | Is `cmu_at` or any CMU token ever forwarded to any frontend page or JavaScript? | TBD | Must be NO |
| C9 | What CMU API is called to get user info from the token? (Is it `misapi.cmu.ac.th/cmuitaccount`?) | TBD | EMS stub references this URL |
| C10 | Does your system use `scope=cmuitaccount.basicinfo` when requesting CMU auth? | TBD | EMS stub uses this scope |

---

## D. User Identity

| # | Question | Answer | Notes |
|---|---|---|---|
| D1 | What is the authoritative CMU email field name returned from CMU user info API? | TBD | (e.g., `cmuitaccount_email`, `email`, `cmu_mail`, `mail`, `account`) |
| D2 | Is the CMU email in the format `username@cmu.ac.th`? | TBD | |
| D3 | Can non-CMU email addresses exist in your system (e.g., external collaborators)? | TBD | |
| D4 | What field is the unique identifier for faculty staff? (employee ID, personnel ID, CMU email?) | TBD | |
| D5 | What field is the unique identifier for students? (student ID, CMU email?) | TBD | |
| D6 | Is there a faculty/staff distinction in the user data returned by CMU auth? | TBD | |

---

## E. Database

| # | Question | Answer | Notes |
|---|---|---|---|
| E1 | Which PostgreSQL instance will EMS use? | TBD | |
| E2 | Will EMS use the same database as the faculty Laravel web system, or a separate database? | TBD | Separate DB strongly recommended |
| E3 | If separate: who provisions and owns the EMS database? | TBD | |
| E4 | Who owns EMS database migrations? | TBD | |
| E5 | Who is responsible for EMS database backup? | TBD | |
| E6 | Where is the PostgreSQL server hosted? (same server as Laravel, separate server?) | TBD | |
| E7 | What PostgreSQL version is running? | TBD | EMS requires PostgreSQL 13+ |
| E8 | Is a PostgreSQL superuser available for initial migration, or only a limited-privilege account? | TBD | |

---

## F. Deployment

| # | Question | Answer | Notes |
|---|---|---|---|
| F1 | Will EMS FastAPI backend run on the same server as the Laravel application? | TBD | |
| F2 | Will EMS be deployed via Docker / Docker Compose, or directly as a Python service? | TBD | |
| F3 | What port will the EMS FastAPI backend listen on? | TBD | |
| F4 | What path will the EMS React frontend static files be served from? | TBD | |
| F5 | Will Nginx proxy requests from `/api/...` to the EMS FastAPI backend? | TBD | |
| F6 | Is there an existing Nginx configuration that EMS must be inserted into? | TBD | |
| F7 | Is HTTPS available on the Faculty LAN server? | TBD | |
| F8 | Is access restricted to LAN only, or can external users reach the server? | TBD | |
| F9 | What is the expected path for EMS deployment files on the server? | TBD | |
| F10 | Who has SSH or deployment access to the server? | TBD | |

---

## G. Security

| # | Question | Answer | Notes |
|---|---|---|---|
| G1 | Is CSRF protection enabled for the Laravel routes EMS will interact with? | TBD | |
| G2 | What SameSite cookie policy does Laravel use? | TBD | |
| G3 | Are all session cookies set as HttpOnly? | TBD | |
| G4 | Are all session cookies set as Secure (HTTPS-only)? | TBD | |
| G5 | Is the EMS backend port firewalled from direct LAN access (accessible only via Nginx proxy)? | TBD | Required for Option C |
| G6 | Is VPN or LAN restriction enforced for the pilot? | TBD | |
| G7 | Are there IP whitelist rules in place? | TBD | |
| G8 | Who reviews and approves network security configuration? | TBD | |

---

## H. Logout

| # | Question | Answer | Notes |
|---|---|---|---|
| H1 | What is the Laravel logout route path? | TBD | |
| H2 | Does Laravel logout invalidate the CMU OAuth session, or only the local Laravel session? | TBD | |
| H3 | Should EMS logout redirect to the Laravel logout route? | TBD | |
| H4 | Should a single-logout flow be implemented (EMS + Laravel both log out together)? | TBD | |
| H5 | If the Laravel session expires but EMS session is still active, how should EMS handle it? | TBD | |

---

## Return Instructions

When complete, return this document (or a copy with the Answer column filled) to:

- EMS team contact: TBD
- Return deadline: TBD

**Do NOT include in your answers**:
- Database passwords
- SECRET_KEY values
- OAuth client secrets
- Session contents beyond the field structure
- Any credentials or tokens

For secret configuration, confirm each item with "YES" (configured) or "NO" (not yet configured).

---

**End of LARAVEL_AUTH_CONTRACT_QUESTIONS.md**
All answers are TBD until verified by the Laravel owner and IT team.
