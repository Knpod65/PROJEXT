# IT_HANDOFF_ACTION_PACK.md

**Date**: 2026-05-22 (Updated — Faculty LAN Server section added)
**Purpose**: Practical checklist and requirements for the IT/infrastructure team that will receive and provision the pilot environment. The selected pilot environment is the Faculty LAN Server running PHP/Laravel/PostgreSQL.

---

## 1. What IT Needs to Provide

- Host / VM / Docker host (name or IP)
- Access method (SSH key, VPN, jump host, etc.)
- Service account for deployment
- PostgreSQL database or connection details
- Backup storage location and method
- Log access for the deployment owner
- Network access scope (LAN ranges, firewall rules)
- HTTPS certificate or LAN URL
- Any proxy / load balancer notes

---

## 2. Minimum Technical Requirements

- Support for Python backend (or full Docker Compose)
- Ability to serve frontend static files (nginx, Caddy, or equivalent)
- PostgreSQL 14+ instance
- Environment variable injection (for .env or secrets)
- Secure storage for SECRET_KEY (never in code)
- Scheduled backup capability (daily pg_dump preferred)
- Log retention for at least 30 days during pilot
- Restricted network access (LAN-only recommended for initial pilot)

---

## 3. Required Environment Variables (to be supplied securely by EMS team)

- ENVIRONMENT=production (or pilot)
- SECRET_KEY (cryptographically strong, ≥50 characters)
- DATABASE_URL (PostgreSQL connection string)
- ALLOWED_HOSTS
- ALLOWED_ORIGINS
- DEBUG=False
- LOG_LEVEL
- PDPA_RETENTION_DAYS
- Any backup-related paths

---

## 4. What Must Be Verified After Handover

- Backend starts cleanly
- Frontend loads without errors
- Database connection successful
- `/health` endpoint returns OK
- Login works for multiple roles
- Main dashboards (Workload, Governance, Executive) load
- Export and import routes respond
- Audit logging is active
- Backup process runs successfully
- Restore test to a safe target completes

---

## 5. Evidence IT Must Return

- Target host / VM details
- Confirmation of each environment variable configured (yes/no)
- Smoke test results (pass/fail + notes)
- Backup execution evidence
- Responsible IT contact during pilot
- Date and time of handover
- Any known issues or limitations

---

## 6. IT Handoff Checklist

- [ ] Host / VM provisioned and accessible
- [ ] PostgreSQL database created and connection string provided
- [ ] SECRET_KEY generated and injected securely
- [ ] All other production env vars configured
- [ ] Backend and frontend deployed
- [ ] Health endpoint verified
- [ ] Basic login and dashboard smoke test passed
- [ ] Backup process scheduled and first backup taken
- [ ] Restore test performed to non-production target
- [ ] Log access granted to EMS deployment owner
- [ ] Network access configured for pilot users

---

## 7. Faculty LAN Server — Specific Requirements (Added 2026-05-22)

The following information is required from the IT owner and Laravel code owner before EMS integration can proceed. This section is specific to the Faculty LAN Server deployment.

### 7.1 Required from IT/Laravel Owner

| Item | Required From | Status |
|---|---|---|
| Exact Laravel route for EMS (e.g., `/ems`, `/exam`, subdomain) | Laravel owner + IT | TBD |
| Exact CMU auth callback route (confirm `/callback/authen/` or correct path) | Laravel owner | TBD |
| `session("USS")` payload structure (field names only — no actual values) | Laravel owner | TBD |
| `cmu_at` validation logic location (server-side, which URL?) | Laravel owner | TBD |
| CMU email field name in validated user response (`cmu_mail` / `email` / `mail`) | Laravel owner | TBD |
| PostgreSQL connection target (host, port, database name — no password) | IT/DBA | TBD |
| Deployment method for EMS (same server as Laravel, Docker, separate service) | IT | TBD |
| Server path where EMS files will be deployed | IT | TBD |
| Reverse proxy config (Nginx route for EMS frontend + `/api/` proxy to EMS backend) | IT | TBD |
| SSL/HTTPS availability on Faculty LAN server | IT | TBD |
| LAN-only restriction confirmed (is external access blocked?) | IT | TBD |
| Backup location and schedule (for EMS PostgreSQL database) | IT/Ops | TBD |
| Log location and retention policy | IT | TBD |
| Faculty LAN server hostname or IP | IT | TBD |
| SSH or deployment access method | IT | TBD |

### 7.2 Security Confirmation Items

Confirm each item below with YES (configured) or NO (not yet configured). Do NOT provide actual secret values.

| Security Item | Confirmed? |
|---|---|
| EMS backend port bound to localhost only (not exposed to LAN directly) | TBD |
| All EMS requests pass through Nginx reverse proxy | TBD |
| Session cookies set with HttpOnly flag | TBD |
| Session cookies set with Secure flag (HTTPS) | TBD |
| SameSite cookie policy confirmed | TBD |
| CSRF protection active on relevant routes | TBD |
| Network firewall restricts access to Faculty LAN only | TBD |

### 7.3 Laravel Auth Integration Notes

- EMS has an existing CMU SSO stub at `backend/cmu_sso.py` targeting `oauth.cmu.ac.th`. This stub requires `CMU_SSO_CLIENT_ID`, `CMU_SSO_CLIENT_SECRET`, and `CMU_SSO_REDIRECT_URI` from OIT. If the EMS direct-OAuth path is selected, these credentials must be provided.
- The auth bridge design and full contract questions are documented in:
  - `docs/deployment/FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md`
  - `docs/deployment/LARAVEL_AUTH_CONTRACT_QUESTIONS.md`
  - `docs/deployment/EMS_LARAVEL_INTEGRATION_OPTIONS.md`
  - `docs/architecture/EMS_AUTH_BRIDGE_DESIGN.md`

### 7.4 Additional Environment Variables for Faculty LAN Deployment

In addition to the standard env vars in Section 3, the following may be needed for the Laravel/CMU integration:

- `CMU_SSO_CLIENT_ID` (if direct CMU OAuth path selected — from OIT)
- `CMU_SSO_CLIENT_SECRET` (if direct CMU OAuth path selected — from OIT)
- `CMU_SSO_REDIRECT_URI` (callback URL for EMS after CMU auth)
- `LARAVEL_BRIDGE_URL` (internal URL for code-exchange if Option B chosen)
- `LARAVEL_BRIDGE_SECRET` (shared secret for server-to-server bridge call if Option B chosen)

**Do not send actual secret values in this document. Confirm configured yes/no only.**

---

**End of IT_HANDOFF_ACTION_PACK.md (Updated 2026-05-22)**
Faculty LAN Server section added. No secrets included. All TBD items require IT/Laravel owner confirmation.