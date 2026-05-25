# FACULTY_WEB_PROXY_REQUIREMENTS.md

**Date**: 2026-05-25

## Minimum Requirements for Faculty Web Reverse Proxy / Laravel

### Frontend (SPA under subpath)

Example mount: `/ems`

Nginx / Laravel route requirements:
- All requests to `/ems/*` must serve the built React assets from the `/ems` directory.
- SPA fallback: Any non-asset path under `/ems` (e.g. `/ems/dashboard`, `/ems/admin-intelligence-dashboard`) must return `/ems/index.html`.
- Static assets must be served with correct cache headers (immutable for hashed filenames).

### API Proxy

Recommended prefix: `/ems-api`

- `/ems-api/*` → proxy to EMS FastAPI backend (which serves at its own `/api` root).
- Or: keep the backend API prefix as `/api` and have the proxy rewrite `/ems-api` → `/api` internally.

### Required Headers (Forwarded by Proxy)

The reverse proxy **must** forward at minimum:
- `X-Forwarded-Proto`
- `X-Forwarded-Host`
- `X-Forwarded-For`
- `Host` (original host)

FastAPI should be started with `--proxy-headers` (Uvicorn) or equivalent trusted-proxy middleware so that `request.url` and redirects are generated correctly for the external portal domain.

### Cookie / Security Notes

- Auth cookies issued by EMS backend must have:
  - `Secure: true` (HTTPS only)
  - `SameSite: Lax` or `Strict` (depending on cross-route needs)
  - Correct `Domain` and `Path` (e.g. Domain=portal.mis.pol.cmu.ac.th, Path=/ or /ems)
- These values are environment-driven in the current EMS config and must be set appropriately for the portal deployment.

### CORS (If Not Same-Origin Proxy)

If the frontend and backend are on different origins (not recommended), CORS must explicitly allow the portal origin.

Prefer same-origin proxy via the faculty web layer.

### Health Check

- `/ems-api/health` (or equivalent) should be reachable through the proxy for monitoring.

### Example Conceptual Nginx Snippet (Illustrative Only)

```
location /ems/ {
    alias /var/www/ems/;
    try_files $uri $uri/ /ems/index.html;
}

location /ems-api/ {
    proxy_pass http://ems-backend:8000/;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Host $host;
}
```

**Do not copy this directly** — use it only for discussion with the faculty web / IT team.

---
*This document captures the standard requirements for any SPA + API subpath deployment behind a reverse proxy. It is not specific to one server.*
