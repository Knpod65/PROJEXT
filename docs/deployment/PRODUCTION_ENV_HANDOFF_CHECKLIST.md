# PRODUCTION_ENV_HANDOFF_CHECKLIST.md

**Date**: 2026-05-22  
**Location**: `docs/deployment/`  
**Purpose**: Single source of truth for all production environment variables required for EMS pilot/production deployment.  
**Rule**: Never store actual secret values in this repository. Only record who sets them, where evidence lives, and safe verification methods.

---

## Required Environment Variables

| Variable                        | Required For                  | Owner          | Where Evidence Is Recorded                          | Safe Verification Method (no secrets exposed) |
|---------------------------------|-------------------------------|----------------|-----------------------------------------------------|-----------------------------------------------|
| `SECRET_KEY`                    | JWT signing (production)      | DevOps         | PRODUCTION_ENV_HANDOFF_CHECKLIST.md + secrets manager | Length check (`wc -c`), application starts without dev warning |
| `DATABASE_URL`                  | PostgreSQL connection         | DevOps / DBA   | Same as above                                       | `/health` returns `db: connected`; migrations succeed |
| `ENVIRONMENT`                   | "production" vs "development" | DevOps         | `.env` or deployment config                         | Application uses production path (no dev fallback warning) |
| `ALLOWED_ORIGINS`               | CORS                          | DevOps         | Deployment config                                   | Browser requests from pilot domain succeed      |
| `ALLOWED_HOSTS`                 | Host header validation        | DevOps         | Deployment config                                   | Health checks and API calls succeed             |
| `LOG_LEVEL`                     | Logging verbosity             | DevOps         | Deployment config                                   | Logs at INFO/ERROR level as expected            |
| `PDPA_RETENTION_DAYS`           | Data retention policy         | Admin + DPO    | Retention policy + DPO sign-off                     | Dry-run report generated                        |
| `MULTI_FACULTY_ENABLED`         | Future multi-faculty          | Admin          | Feature flag config                                 | Current single-faculty behavior unchanged       |
| `RETENTION_CLEANUP_ENABLED`     | Automated cleanup             | Ops            | Only after backup + DPO sign-off                    | Cron job present but disabled until approved    |

---

## Handoff Process

1. DevOps generates and injects production values into the target environment (Kubernetes secrets, Docker secrets, or `.env` on secure host).
2. Record the **owner**, **date set**, and **evidence location** (ticket, secret ID, or internal wiki link) in the table above. Do **not** paste values here.
3. Application is started in production mode.
4. Verification is performed using the safe methods column (no secret values are printed or logged).
5. Evidence of successful verification is attached to this document or linked.

---

## Verification Without Exposing Secrets

- Never run `echo $SECRET_KEY` or similar in shared logs.
- Use length checks, health endpoints, and application behavior.
- For `SECRET_KEY`: confirm that production startup produces **no** "using insecure development fallback" warning.
- For `DATABASE_URL`: confirm migrations and health endpoint succeed against the real database.

---

**End of PRODUCTION_ENV_HANDOFF_CHECKLIST.md**  
This is a living handoff document. Update it as each variable is set in production.