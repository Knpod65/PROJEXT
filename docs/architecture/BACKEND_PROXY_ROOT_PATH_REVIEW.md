# BACKEND_PROXY_ROOT_PATH_REVIEW.md

**Date**: 2026-05-25

## Summary

The backend (FastAPI) is already in a good position for reverse-proxy deployment behind a faculty web layer.

### Current Strengths
- Hardened startup (no create_all/seed in non-dev environments).
- PostgreSQL pooling with production settings.
- Existing security and CORS middleware.

### Areas Requiring Proxy Configuration (Not Code Changes)

1. **root_path / proxy headers**
   - FastAPI supports `root_path` via the ASGI scope or `uvicorn --root-path`.
   - When the proxy mounts the API at `/ems-api`, the backend should be informed so that generated URLs (OpenAPI, redirects) are correct.
   - Recommendation: Run uvicorn with `--proxy-headers` and let the proxy set the standard forwarded headers.

2. **Health endpoint**
   - `/health` (or `/ems-api/health` after proxy) should remain stable and not require auth for monitoring.

3. **Docs / OpenAPI**
   - In production web portal deployment, consider disabling or protecting `/docs` and `/openapi.json` (already good practice).

4. **CORS**
   - Should be configured to the exact faculty web origin(s) only (already supported via settings).

### No Code Changes Needed in This Pass

All of the above are deployment/configuration concerns, not runtime code changes.

Documented in the new proxy requirements and deployment checklist.

---
*Backend is ready for the documented web portal proxy model.*
