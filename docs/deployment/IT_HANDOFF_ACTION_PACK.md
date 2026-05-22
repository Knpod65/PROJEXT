# IT_HANDOFF_ACTION_PACK.md

**Date**: 2026-05-22  
**Purpose**: Practical checklist and requirements for the IT/infrastructure team that will receive and provision the pilot environment.

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

**End of IT_HANDOFF_ACTION_PACK.md**  
This package is ready to be attached to the IT request. No secrets included.