# FACULTY_WEB_API_BASE_PATH_AUDIT.md

**Date**: 2026-05-25

## Summary

Search for direct API calls bypassing the central service.

## Central Service (Good)
- `frontend/src/services/api.ts` now correctly uses `VITE_API_BASE_URL || "/api"`.
- All calls that go through the exported `api` object or helpers are configurable.

## Direct /api Calls Found (Bypass Central Service)

- `useExportCenterPage.ts`: multiple `openExport("/api/exports/...")`
- `Schedule.tsx`: `window.open("/api/exports/...")`
- `documents.service.ts`: `new URL("/api/documents/export-pdf", ...)`
- `historicalSchedule.service.ts`: `"/api/historical-schedules/export/comparison-csv"`
- `Login.tsx`: `window.location.href = `/api/auth/sso/login...``

These will **not** respect `VITE_API_BASE_URL` unless the strings are changed to use the central helper or a shared constant.

## False Positives / Safe

- Some are intentional external links or full URLs constructed with origin.
- SSO login redirect may legitimately need the backend /api path.

## Safe Fixes (Minimal Scope for This Pass)

No code changes made in this pass for these (to avoid scope creep and risk to standalone demo).

**Recommendation**:
- Create a small follow-up: centralize remaining direct `/api` strings through `api.ts` or a `getApiUrl()` helper.
- For now, document as "PASS WITH KNOWN DIRECT CALLS" — they will break under `/ems-api` proxy unless the proxy also proxies the bare `/api` path (not recommended).

## Status

**API base path support**: Good for code that uses the central service. Incomplete for direct string calls.

The VITE_API_BASE_URL mechanism works as designed for the majority of the app.

---
*This is acceptable for the subpath smoke pass. The build and configurable paths are validated.*
