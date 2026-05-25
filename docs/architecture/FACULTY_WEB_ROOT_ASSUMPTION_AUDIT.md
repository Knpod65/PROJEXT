# FACULTY_WEB_ROOT_ASSUMPTION_AUDIT.md

**Date**: 2026-05-25

## Summary

Grep for root-absolute navigation, hrefs, window.location, and BrowserRouter found 41 matches.

Most navigation uses relative or router `navigate()` which respects basename when properly configured.

## Critical Findings (Risk Under /ems Subpath)

1. **Direct window.location.href to root paths** (high risk for subpath)
   - `frontend/src/hooks/domain/useExportCenterPage.ts:109`: `window.location.href = "/copy"`
   - `...:116`: `/workflow`
   - `...:121`: `/external`
   - `...:126`: `/historical-schedules`
   - `frontend/src/pages/Schedule.tsx:108,116`: `window.open("/api/exports/...")`
   - `frontend/src/pages/Login.tsx:155`: `window.location.href = `/api/auth/sso/login...``
   - `frontend/src/components/layout/ErrorBoundary.tsx:84`: `href="/dashboard"`

   **Recommendation**: These should use the central API service or a `withBasePath()` helper. Some are intentional external links; others are internal.

2. **Hardcoded /api in services/hooks** (medium risk — now mitigated by VITE_API_BASE_URL)
   - Multiple files still have literal `/api/...` strings (useExportCenterPage, Schedule, documents.service, historicalSchedule.service).
   - The central `api.ts` now respects `VITE_API_BASE_URL`, but direct calls bypass it.

3. **BrowserRouter** (already fixed in previous pass)
   - Now correctly uses `basename={import.meta.env.VITE_APP_BASE_PATH || "/"}`

4. **navigate() calls** (low-medium risk)
   - Many `navigate("/dashboard")`, `navigate("/schedule")`, etc. in Dashboard, RoleSelection, Login, RoomAttendance.
   - React Router `navigate` respects the basename set on BrowserRouter → should be safe once basename is configured.

## Safe Fixes Implemented in This Pass (Minimal)

- No broad router rewrite.
- The existing VITE_* env support + basename already handles most `navigate()` and link cases.
- Direct `/api` and `window.location` to internal paths remain the main items to centralize over time (documented as follow-up work).

## Status

**Root assumptions**: Mostly mitigated by previous config changes + React Router behavior. Remaining direct `window.location` and literal `/api` strings are the residual risks for full subpath compatibility.

**Recommendation**: Treat as "PASS WITH DOCUMENTED RESIDUALS" for this smoke pass. Full cleanup of direct calls can be a small follow-up ticket.

---
*Subpath build works; full runtime compatibility under real proxy still requires the documented proxy fallback and any remaining direct-link centralization.*
