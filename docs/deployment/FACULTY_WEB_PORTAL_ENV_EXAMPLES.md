# FACULTY_WEB_PORTAL_ENV_EXAMPLES.md

**Date**: 2026-05-25

## Environment Variable Examples for Faculty Web Portal Deployment

**Important**: These are examples only. Exact paths must be confirmed by the Faculty IT / web team.

### Local Development / Standalone Demo (Default — No Changes Needed)

No environment variables required. Defaults are used:

```
VITE_APP_BASE_PATH=/
VITE_API_BASE_URL=/api
```

Run normally:
cd frontend
npm run dev
npm run build

### Faculty Web Portal Subpath Example (Most Likely)

```
VITE_APP_BASE_PATH=/ems
VITE_API_BASE_URL=/ems-api
```

Build command (example):
```
VITE_APP_BASE_PATH=/ems VITE_API_BASE_URL=/ems-api npm run build
```

Resulting URLs:
- Frontend served at: https://portal.mis.pol.cmu.ac.th/ems
- API calls go to: https://portal.mis.pol.cmu.ac.th/ems-api/...

### Alternative Same-Origin Proxy (If IT Prefers)

Frontend and API under the same origin but different prefixes:
- Frontend: /ems
- API: /ems-api (proxied by Laravel/Nginx to the FastAPI backend)

Same env vars as above.

### Full Origin (Less Common)

If the proxy exposes the backend on a different origin:
```
VITE_API_BASE_URL=https://ems-api.pol.cmu.ac.th
```

Rare for this architecture.

## Notes

- Always keep root (`/`) + `/api` as the default for local development and the current standalone demo (98/100).
- Never commit real .env files with production values.
- The variables only affect the **frontend build/runtime**. Backend configuration is separate (see FACULTY_WEB_PORTAL_DEPLOYMENT_CHECKLIST.md).

---
*Use these examples when preparing builds for the Faculty Web Portal once paths are confirmed.*
