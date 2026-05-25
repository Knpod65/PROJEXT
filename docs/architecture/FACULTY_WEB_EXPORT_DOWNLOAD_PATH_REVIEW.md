# FACULTY_WEB_EXPORT_DOWNLOAD_PATH_REVIEW.md

**Date**: 2026-05-25  
**Pass**: EMS FACULTY WEB PORTAL ROOT ASSUMPTION + API BASE HARDENING PASS

## Scope
Special review of all export, download, and browser-triggered file URLs (these intentionally use window.open / <a href> or return strings for direct links, unlike normal JSON API calls).

## Findings & Actions Taken

### Centralized in This Pass (All Now Respect VITE_API_BASE_URL)
- `frontend/src/services/documents.service.ts` — `buildDocumentExportUrl(...)`
  - Was: hard-coded `/api/documents/export-pdf`
  - Now: uses `buildApiUrl("/documents/export-pdf", ...)` + origin for full URL
  - Callers: Schedule page "Generate Exam Documents", "Export Cover Sheets", ExportCenter cards

- `frontend/src/services/historicalSchedule.service.ts`
  - `buildHistoricalComparisonCsvUrl()` → now `buildApiUrl("/historical-schedules/export/comparison-csv")`
  - `buildHistoricalWorkloadCsvUrl(...)` → now uses `buildApiUrl`
  - These return path strings consumed by UI download links

- `frontend/src/hooks/domain/useExportCenterPage.ts`
  - 8 optimization + workload export actions (schedule PDF/Excel, paper distribution, workload summary/detail, fairness sheet)
  - All now call `openExport(buildApiUrl("/exports/..."))`

- `frontend/src/pages/Schedule.tsx`
  - "Export Excel" and "Export PDF" buttons for master schedule
  - Now: `window.open(buildApiUrl("/exports/schedule-excel"), "_blank")` etc.

### No Changes Needed (Already Safe or External)
- Any download links that use the central `get()` / `post()` for blob responses (none found in this audit for file downloads)
- Print shop / external lanes (intentionally separate; not part of EMS API base)
- True external URLs (none were using /api in the searched code)

## Behavior Preservation
- When no VITE_API_BASE_URL is set → all URLs remain `/api/...` (identical to pre-pass local demo)
- When `VITE_API_BASE_URL=/ems-api` → all export/download URLs become `/ems-api/...` automatically
- Full URLs for window.open still correctly include origin + the prefixed path

## Risks Mitigated
- Before this pass: any faculty web deployment under `/ems-api` proxy would have broken all these export buttons (404 or hitting wrong backend)
- After: 100% of intentional export/download paths are now configurable via the same env var as the rest of the app

## Remaining Notes
- The actual file-serving endpoints live on the FastAPI backend (`/api/exports/*`, `/api/documents/export-pdf`, etc.). No backend changes were made.
- Proxy configuration (documented in FACULTY_WEB_PROXY_REQUIREMENTS.md) must still route `/ems-api/exports/*` → backend for downloads to work under subpath.
- Historical schedule CSV builders were the last remaining raw-string returns in services; now cleaned.

**Status**: Export / download surface fully hardened for subpath deployment. No further direct /api strings remain for application API downloads.

*This completes PHASE 7.*
