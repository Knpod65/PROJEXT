# FACULTY_WEB_API_BASE_HARDENING_AUDIT.md

**Date**: 2026-05-25  
**Pass**: EMS FACULTY WEB PORTAL ROOT ASSUMPTION + API BASE HARDENING PASS

## Inventory Method
- Broad searches for literal `"/api` and `'/api` strings across all .ts/.tsx
- Searches for `fetch(`, axios usage, and "api/" inside services/hooks/pages
- Targeted full-file review of every file containing direct strings (beyond the central api.ts)
- Cross-reference with prior audit (FACULTY_WEB_API_BASE_PATH_AUDIT.md from d2ac628)

## Central Service (Already Good)
- `frontend/src/services/api.ts` — `const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";`
- All internal `get`/`post`/`put`/`del` calls go through `request()` which correctly prefixes.
- Used by the vast majority of services and hooks.

## Direct /api Findings Table

| # | File | Pattern | Uses central API base? | Risk under /ems-api | Safe Fix? | Action (This Pass) | Classification | Notes |
|---|------|---------|------------------------|---------------------|-----------|--------------------|----------------|-------|
| 1 | frontend/src/hooks/domain/useExportCenterPage.ts (multiple) | `openExport("/api/exports/...")` — 8 different export endpoints (schedule, pdf, excel, workload, etc.) | No — passes raw string to openExport | High — will call bare /api instead of /ems-api | Yes | Centralize via buildApiUrl in PHASE 6 | **FIX NOW** | All are application API exports. openExport likely does window.open or <a>. |
| 2 | frontend/src/pages/Schedule.tsx | `window.open("/api/exports/schedule-excel", "_blank")` | No | High | Yes | Use centralized builder or buildApiUrl + window.open | **FIX NOW** | Direct download button |
| 3 | frontend/src/pages/Schedule.tsx | `window.open("/api/exports/schedule", "_blank")` | No | High | Yes | Same | **FIX NOW** | Same |
| 4 | frontend/src/services/documents.service.ts | `new URL("/api/documents/export-pdf", window.location.origin)` in `buildDocumentExportUrl` | No | High | Yes | Change to use API base + expose buildApiUrl or similar | **FIX NOW** | Used by Schedule page for "Generate Exam Documents" / "Export Cover Sheets" |
| 5 | frontend/src/services/historicalSchedule.service.ts | `return "/api/historical-schedules/export/comparison-csv"` in `buildHistoricalComparisonCsvUrl` | No | High | Yes | Make the builder use central base | **FIX NOW** | Returns URL string for direct download links in UI |
| 6 | frontend/src/services/historicalSchedule.service.ts | `` `/api/historical-schedules/export/workload-csv?...` `` | No | High | Yes | Same | **FIX NOW** | Same |
| 7 | frontend/src/hooks/useFacultyConfig.ts | `fetch(\`/api/platform/faculty-configs/${facultyId}\`)` | No | High | Yes | Replace with central get() or buildApiUrl + fetch (or better, move to platformConfig.service) | **FIX NOW** | Placeholder code; still a direct bypass |
| 8 | frontend/src/hooks/useFacultyPolicy.ts | Two `fetch(\`/api/platform/faculty-configs/.../\`)` | No | High | Yes | Same as above | **FIX NOW** | Placeholder; same family as #7 |
| 9 | frontend/src/hooks/useFacultyPolicy.ts | `fetch(policyUrl)` / `fetch(flowUrl)` where urls built with /api | No | High | Yes | Same | **FIX NOW** | Companion to the above |
| 10 | frontend/src/services/api.ts | Internal use of window.location.origin + `${API_BASE}...` (correct) | Yes (defines the base) | None | N/A | SAFE AS IS | **SAFE AS IS** | Authoritative implementation |
| 11 | All other services (most) | Use `get(...)`, `post(...)` etc. from api.ts | Yes | None | N/A | SAFE AS IS | **SAFE AS IS** | Correct usage |
| 12 | Login.tsx SSO button | `window.location.href = \`/api/auth/sso/login...\`` | No | High (auth path) | Yes | Centralize in PHASE 6 (special case — full redirect) | **FIX NOW** | SSO entry point; must respect proxy prefix |
| 13 | appPaths.ts (new) | Documentation comment + re-export of API_BASE_URL for convenience | N/A | None | N/A | SAFE AS IS (convenience only) | **SAFE AS IS** | Does not change behavior |

## Classification Summary (This Pass)

- **FIX NOW**: 9 direct bypass sites (useExportCenterPage exports, Schedule downloads, documents.service builder, historicalSchedule csv builders, two placeholder faculty config/policy hooks, Login SSO)
- **SAFE AS IS**: Central api.ts + all services that already call through get/post/put/del
- **DEFER / NEEDS HUMAN REVIEW**: None for pure API base (the auth contract questions are separate from path prefixing)
- **FALSE POSITIVE**: 0

## Key Observations

- The majority of the application already benefits from VITE_API_BASE_URL because it goes through the central client.
- The remaining direct strings are concentrated in:
  - Export / download flows (intentional browser-triggered downloads)
  - Two small placeholder hooks for future faculty config endpoints
  - The SSO login redirect (special full-page navigation to auth)
- All of the above are **safe and low-risk to centralize** using a small exported helper from api.ts (getApiBaseUrl + buildApiUrl) plus updating the builder functions.

## Planned PHASE 6 Scope (Minimal & Safe)

- Add to api.ts:
  ```ts
  export function getApiBaseUrl(): string { return API_BASE; }
  export function buildApiUrl(path: string): string { ... }
  ```
- Update the 9 sites above to use the new helpers (or the existing get() where the call is a normal JSON request).
- For the CSV / PDF builders that return strings for href/window.open: make them return the correctly prefixed full path (or full URL when needed).
- Preserve exact current behavior when no env var is set (default "/api").
- No change to request payloads, auth headers, or backend endpoints.

**Status**: Inventory complete. 9 safe centralization opportunities identified. All other API usage already correct.

*Next: PHASE 6 — implement the central helpers and apply the fixes.*
