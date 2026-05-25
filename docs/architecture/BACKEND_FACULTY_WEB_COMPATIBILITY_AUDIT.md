# BACKEND_FACULTY_WEB_COMPATIBILITY_AUDIT.md

**Date**: 2026-05-25  
**Pass**: EMS FACULTY WEB PORTAL DEPLOYMENT + SYSTEM COMPLETION PASS

## Files Inspected

- backend/main.py (FastAPI app, lifespan, CORS, routers registration)
- backend/config/settings.py (environment, allowed origins, etc.)
- backend/security.py (cookie handling, production secret validation)
- backend/routers/auth.py (login, token, cookie issuance)
- backend/database.py (PostgreSQL pooling, SQLite fallback)
- backend/.env.example and related config
- Health and public routers

## Key Findings

### Positive (Already Well-Positioned)
- FastAPI + Uvicorn/Gunicorn is standard for behind-proxy deployment.
- PostgreSQL support with pooling is production-grade.
- Hardened startup (gated create_all/seed, no SQLite fallback in non-dev) is excellent for web hosting.
- Existing CORS and security middleware can be extended.

### Risks / Gaps for Faculty Web Portal

1. **Reverse proxy / root_path**
   - No explicit handling of `root_path` or trusted proxy headers visible in main.py at quick inspection.
   - When behind faculty web reverse proxy (e.g. /ems-api), FastAPI needs to know the external prefix for correct URL generation (docs, redirects, OpenAPI).

2. **CORS / allowed origins**
   - Currently configured for local dev.
   - For web portal, origins will be the faculty web domain(s). Must be configurable and restrictive.

3. **Cookie settings for sub-path / proxy**
   - Secure, SameSite, domain, and path attributes on auth cookies become critical when the frontend lives under the faculty web domain or a sub-path.
   - Current auth.py issues cookies; these settings must be tunable per environment.

4. **Health and docs exposure**
   - /health and docs endpoints should probably be restricted or at least not advertise internal details when exposed through the faculty web tier.

5. **Auth boundary**
   - Still pending full contract answers (see updated questions). The backend is ready for a verified identity injection point (e.g. from Laravel proxy header or short-lived token), but nothing is implemented yet.

## Recommended Safe / Documentation Updates

- Document required reverse proxy headers (X-Forwarded-Proto, X-Forwarded-Host, X-Forwarded-Prefix or root_path).
- Add example configuration for `root_path` in FastAPI app when running behind faculty web proxy.
- Make CORS allowed origins and cookie settings clearly environment-driven (already partially done via settings).
- Add notes in .env.example and deployment docs for faculty web hosting.
- Consider adding a simple trusted-proxy middleware or using `uvicorn` with `--proxy-headers` (standard practice).

These are mostly documentation + configuration clarity — low risk.

## Blocked Until IT Answers

- Exact proxy prefix and header behavior from faculty web reverse proxy.
- Whether auth will arrive via trusted header, short-lived token from Laravel, or direct OAuth callback.
- Cookie domain / path policy when EMS is under faculty web.

## PostgreSQL Notes (Cross-Reference)

See new FACULTY_WEB_POSTGRESQL_DEPLOYMENT_PLAN.md (to be created in this pass). Separate EMS DB/schema is still strongly recommended.

---
*Backend is structurally ready for web portal deployment. The remaining items are standard proxy configuration and the still-pending auth contract answers.*
