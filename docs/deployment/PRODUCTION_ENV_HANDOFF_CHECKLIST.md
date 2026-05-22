# PRODUCTION_ENV_HANDOFF_CHECKLIST.md

**Date**: 2026-05-22  
**Location**: `docs/deployment/`  
**Purpose**: Single source of truth for all production environment variables required for EMS pilot/production deployment.  
**Rule**: Never store actual secret values in this repository. Only record who sets them, where evidence lives, and safe verification methods.

---

## Required Environment Variables – Evidence Collection

| Variable                  | Required For                  | Owner     | Where Evidence Recorded                  | Safe Verification Method                  | Configured By | Configured Date | Verification Method Used | Verification Result | Reviewer | Status |
|---------------------------|-------------------------------|-----------|------------------------------------------|-------------------------------------------|---------------|-----------------|--------------------------|---------------------|----------|--------|
| `SECRET_KEY`              | JWT signing (production)      | DevOps    | Secrets manager / production .env        | Length ≥ 64 chars; no dev fallback warning on startup | _____________ | _____________   | ________________________ | ___________________ | ________ | [ ] Pending [ ] Verified |
| `DATABASE_URL`            | PostgreSQL connection         | DevOps/DBA| Production deployment config             | /health returns db:connected; migrations succeed | _____________ | _____________   | ________________________ | ___________________ | ________ | [ ] Pending [ ] Verified |
| `ENVIRONMENT=production`  | Production mode enforcement   | DevOps    | Deployment config                        | Application uses production code paths (no dev warning) | _____________ | _____________   | ________________________ | ___________________ | ________ | [ ] Pending [ ] Verified |
| `DEBUG=False`             | Disable debug mode            | DevOps    | Deployment config                        | No stack traces in error responses        | _____________ | _____________   | ________________________ | ___________________ | ________ | [ ] Pending [ ] Verified |
| `ALLOWED_HOSTS`           | Host header protection        | DevOps    | Deployment config                        | Health checks and API calls succeed from expected hosts | _____________ | _____________   | ________________________ | ___________________ | ________ | [ ] Pending [ ] Verified |
| `ALLOWED_ORIGINS`         | CORS for pilot domain         | DevOps    | Deployment config                        | Browser requests from pilot domain succeed without CORS errors | _____________ | _____________   | ________________________ | ___________________ | ________ | [ ] Pending [ ] Verified |
| `LOG_LEVEL`               | Logging verbosity             | DevOps    | Deployment config                        | Logs at expected level (INFO/ERROR)       | _____________ | _____________   | ________________________ | ___________________ | ________ | [ ] Pending [ ] Verified |
| `PDPA_RETENTION_DAYS`     | Data retention policy         | Admin+DPO | Retention policy + DPO sign-off          | Dry-run report generated and matches policy | _____________ | _____________   | ________________________ | ___________________ | ________ | [ ] Pending [ ] Verified |
| `RETENTION_CLEANUP_ENABLED` | Automated cleanup control   | Ops       | Deployment config (disabled until approved) | Cron/job present but disabled until DPO sign-off | _____________ | _____________   | ________________________ | ___________________ | ________ | [ ] Pending [ ] Verified |

**evidence collected** placeholders: All fields above are to be filled with real operational evidence only. No actual secret values are recorded here.

---

## Handoff Process

1. DevOps generates and injects production values into the target environment.
2. Record the **Configured By**, **Configured Date**, **Verification Method Used**, **Verification Result**, **Reviewer**, and **Status** in the table.
3. Application started in production mode.
4. Verification performed using safe methods only.
5. Evidence (screenshots, logs, tickets, or internal wiki links) attached or referenced.

---

## Verification Without Exposing Secrets

- Use length checks, health endpoints, and behavioral confirmation.
- Never print or log actual `SECRET_KEY` or connection strings.
- For `SECRET_KEY`: confirm production startup produces **no** insecure development fallback warning.
- For `DATABASE_URL`: confirm `/health` and migrations succeed against the real PostgreSQL instance.

---

**Evidence collected** — All entries above are placeholders until real production configuration is performed and verified by the responsible owners.

**End of PRODUCTION_ENV_HANDOFF_CHECKLIST.md**  
This document now contains structured evidence fields for operational verification.