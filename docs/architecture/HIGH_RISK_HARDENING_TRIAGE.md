# HIGH_RISK_HARDENING_TRIAGE.md

**Date**: 2026-05-22  
**Purpose**: Triage all high-risk findings from the superior developer audit into action categories.  
**Source audit**: `EMS_FULL_SYSTEM_SUPERIOR_DEVELOPER_REVIEW.md`, `SECURITY_PDPA_AUTHORIZATION_AUDIT.md`, `POSTGRESQL_DATA_ARCHITECTURE_AUDIT.md`

---

## Triaged Findings

| # | Item | Risk | Current Evidence | Fix Now | Fix After Contract | Fix After Pilot | Owner | Recommended Action |
|---|------|------|-----------------|---------|-------------------|-----------------|-------|-------------------|
| 1 | `create_all()` / `seed_data()` on every startup (`main.py` lifespan) | Critical — causes schema mutation and DB session open on every startup; could run in shared-Tenant or pilot environment | Lines 60-65 in `main.py`: every startup opens a Session, runs `Base.metadata.create_all()`, opens a second Session, calls `seed_data(db)` | **✅ Yes** | — | Must not touch production DB on boot — gate on env before pilot | Backend owner | Gate both calls behind `EMS_ALLOW_STARTUP_MUTATION=True` or equivalent local-dev condition; keep production startup read-only |
| 2 | `DATABASE_URL` missing silently falls back to local SQLite (`database.py`) | High — masks broken production deployment; pilot data stored locally instead of centralized PostgreSQL | Lines 10-14: `if not DATABASE_URL:` falls back to SQLite with stderr print, no crash | **✅ Yes** (warn loudly) | — | In production/pilot, fallback must be a hard error | Backend owner | Raise RuntimeError on missing DATABASE_URL in production/pilot; loud stderr warning with clear exit code in all cases |
| 3 | ENV vs ENVIRONMENT inconsistency (env var split) | High — `security.py` uses `ENV` while `settings.py` uses `ENVIRONMENT`; two separate gates hiding behind different env vars produce inconsistent production detection | `security.py:71`: `env("ENV", ...)`, `settings.py:118`: `env("ENVIRONMENT", ...)` | **✅ Yes** | — | Before pilot to ensure consistent production checks | Backend owner | Unify to `ENVIRONMENT` everywhere; keep `ENV` as a backwards-compat fallback only, not the primary check |
| 4 | `validate_production_secrets()` uses `ENV` not `ENVIRONMENT` | High — if `ENVIRONMENT=production` is set but `ENV` is unset, `is_prod` evaluates `False` and secrets are never validated at startup | `security.py:71`: `env("ENV", "development")` | **✅ Yes** | — | Before pilot | Backend owner | Align `validate_production_secrets()` to check `ENVIRONMENT` first, with `ENV` as fallback |
| 5 | Login returns bearer token in response body (`auth.py`) | High — token is already in HttpOnly cookie; response body exposes a second copy that can be accidentally logged or stored in localStorage by misconfigured frontend | `routers/auth.py` login handler | Yes (safelocal-dev) | — | Before pilot — remove response body token return; cookie is sufficient | Backend owner | Do not set a hard cryptographic risk low; optionally remove token from response body or add a strong warning to frontend not to store it in localStorage; keep Bearer header for API scripts |
| 6 | `/health` endpoint access policy not enforced as documented | Medium — docstring says admin/internal; implementation does not enforce boundary | `routers/health.py` | Defer | — | After pilot or when document is updated | Backend owner | Either enforce admin-only or update docstring to match actual behavior; defer to not disrupt pilot smoke test access |
| 7 | Auth and permission logic split across `auth_utils.py` and `permissions.py` | Medium — creates policy drift risk | Both files contain role logic | Defer | Defer | Post-pilot | Backend owner | Consolidate toward one authoritative permission surface after pilot validates bridge behavior |
| 8 | `cmu_sso.py` stub path decision not made | High — real CMU OAuth integration (OIT credentials); existing stub is inactive and conflicts with Laravel bridge | `backend/cmu_sso.py` | Defer (do not activate until bridge decision) | **After contract** | After contract verified | Backend + Laravel owner | Decide after Laravel auth bridge option selected; do not activate stub independently |
| 9 | Login returns bearer token in response body (duplicate of #5) | Same | — | — | — | — | — | Grouped with #5 |

---

## Triage Summary

| Category | Count | Items |
|----------|-------|-------|
| **Fix before pilot** — safe, isolated, no dependency on Laravel contract | **4** | #1 create_all()/seed, #2 SQLite fallback, #3 ENV/ENVIRONMENT, #4 validate_production_secrets env check |
| **Fix after contract verified** | **2** | #8 cmu_sso path decision; auth bridge gate must clear first |
| **Defer to post-pilot** | **3** | #5 token return body (safe as warning now, fix properly after), #6 /health access policy, #7 permission logic splits |
| **Documentation only** | 0 | — |

**Fix now items (#1-4) are all independent of the Laravel contract** and can safely be addressed ahead of the pilot environment designation. They are gating on production safety gate checks, not on any auth contract answers.

---

**End of HIGH_RISK_HARDENING_TRIAGE.md**  
The "Fix now" items (1-4) are ready for implementation review in SAFE_CODE_HARDENING_PLAN.md and Phase 7 if conditions are met. Items 5-9 remain in their respective phases.