# SAFE_CODE_HARDENING_PLAN.md

**Date**: 2026-05-22  
**Purpose**: Plan for independent, safe, no-dependency hardening changes before pilot.  
**Scope**: Only items classified "Fix now" in `HIGH_RISK_HARDENING_TRIAGE.md`: `#1` create_all/seed, `#2` SQLite fallback, `#3` ENV vs ENVIRONMENT, `#4` validate_production_secrets env check.

---

## Candidate 1 — Gate create_all() + seed_data() on Environment

**File**: `backend/main.py` (lifespan hook, lines 50-66)  
**Risk**: Silent mutation of any database EMS connects to on startup — publication, production, or pilot.  
**Proposed Change**: Wrap both `create_all()` and seed_data() in an `if` that only fires when the process is explicitly in a deliberate local-dev or migration schema-setup mode. Suggested guard: check `getattr(settings, "environment", "development") != "production"` AND add explicit opt-in flag `EMS_ALLOW_STARTUP_MUTATION=True` (or remove seed service entirely from normal runtime path and only run manually when DB owner confirms). For pilot, production==False is already wrong; we need explicit permission.  
**Implementation options** (choose one):
1. Gate entirely on `settings.environment != "production"` (simplest)
2. Gate on explicit env var `EMS_ALLOW_STARTUP_MUTATION=True`
3. Gate on all of `settings.environment != "production" AND EMS_ALLOW_STARTUP_MUTATION=True`
4. Remove from lifespan and document as a manual migration action (`docs/architecture/POSTGRESQL_DATA_ARCHITECTURE_AUDIT.md` already recommends this at item #106)  
**Recommended**: Option 1 — gate on `settings.environment != "production"` (covers pilot too if pilot env uses `production` profile; local development schema setup can still use the env-var override if local dev must use SQLite)  
**Tests required**: Verify `create_all()` does NOT run when `ENVIRONMENT=production`; verify `seed_data()` does NOT run when `ENVIRONMENT=production`; verify they DO run when `ENVIRONMENT=development`  
**Safe now?** ✅ Yes — isolated to main.py lifespan, no auth or DB contract impact, no production DB change unless ENVIRONMENT=production is already missing or mis-set  
**Test file needed**: A new test file `backend/tests/test_startup_safety.py` or add to existing migration/runtime tests

---

## Candidate 2 — SQLite fallback: warn loudly and fail on production/pilot

**File**: `backend/database.py` (lines 10-14)  
**Risk**: Missing DATABASE_URL silently falls back to local SQLite file — hides broken deploy and causes pilot data to go to wrong store  
**Proposed Change**: Check Sentinel env (`ENVIRONMENT`) before SQLite fallback. Allow SQLite fallback only when `getattr(settings, "environment", "development") != "production"`. In production/pilot, raise a startup crash with a clear error message pointing to DATABASE_URL. Add explicit audit log note so the initiator knows why the process stopped.

**Implementation**:
```python
from config.settings import settings

if not DATABASE_URL:
    if settings.environment != "production":
        print(
            "WARN: DATABASE_URL not set - using SQLite (development only). "
            "Set DATABASE_URL to a PostgreSQL connection string for pilot/production.",
            file=sys.stderr,
        )
        DATABASE_URL = f"sqlite:///{backend_db_path.as_posix()}"
    else:
        raise RuntimeError(
            "DATABASE_URL must be set in production/pilot environment. "
            "SQLite fallback is not allowed. Set DATABASE_URL to a PostgreSQL connection string."
        )
```

**Tests required**: Verify RuntimeError is raised when `ENVIRONMENT=production` and `DATABASE_URL` unset; verify SQLite fallback still works when `ENVIRONMENT=development`  
**Safe now?** ✅ Yes — only changes behavior when DATABASE_URL is missing AND environment is production; no route, auth, or DB contract change

---

## Candidate 3 — Unify ENV / ENVIRONMENT for production detection

**File**: `backend/security.py:validate_production_secrets()` (line 71) and cookie production flag  
**Risk**: Two different env vars (`ENV` and `ENVIRONMENT`) gate independent production-mode checks. If `ENV` is unset and `ENVIRONMENT=production` is set, validate_production_secrets skips validation. If `ENVIRONMENT` is unset and `ENV=production` is set, settings._get_secret_key() treats the key as unset rather than using it. Either mismatch creates inconsistent production behavior.  
**Proposed Change**: Update `validate_production_secrets()` to check `ENVIRONMENT` first, then `ENV` as fallback:

```python
def _is_production() -> bool:
    return os.getenv("ENVIRONMENT", os.getenv("ENV", "development")).lower() in ("production", "prod")
```

Use `_is_production()` in both `validate_production_secrets()` and in `security.py` cookie flags (lines 101/126) where `ENV` is used directly.  
**Tests required**: New tests in `test_config_validation_service.py` or a new `test_security_production_detection.py` to confirm consistent detection across all three locations  
**Safe now?** ✅ Yes — no production or route change concerns

---

## Candidate 4 — Warn on CMU email in seed data vs. real DB usage in production

**File**: `backend/seed.py`  
**Risk**: Hardcoded CMU email addresses (`@cmu.ac.th`) in seed data are fine for local development, but running `seed_data` in a connected production database would insert test user records alongside real production data. Since Candidate 1 gates `seed_data` on environment, this is an additional protection layer.  
**Proposed Change**: While Candidate 1 gates the call, add a check at the top of `seed_data()` to early-return with a loud log warning if CMU email domains in the seed data are about to be committed to a database whose URL doesn't match the local dev pattern.  
**Tests required**: Verify seed_data returns without changes when `ENVIRONMENT` is non-dev  
**Safe now?** ✅ Yes — added safety on top of Candidate 1 gate

---

## Commits

| Commit # | Change | Message |
|----------|--------|---------|
| 1 | Candidate 1 + Candidate 4 | `fix(startup): gate schema creation and seeding on environment; seed_data warns on production DB` |
| 2 | Candidate 2 + Candidate 3 | `fix(db, security): enforce DATABASE_URL in production, unify ENVIRONMENT env check` |

---

**End of SAFE_CODE_HARDENING_PLAN.md**  
Each candidate is independent of the Laravel auth contract, has a clear test plan, and can be implemented now without affecting runtime behavior in development mode. Proceed to Phase 7 only after this plan is reviewed and confirmed safe.