# FACULTY_WEB_HARDENING_SOURCE_REVIEW.md

**Date**: 2026-05-25  
**Pass**: EMS FACULTY WEB PORTAL ROOT ASSUMPTION + API BASE HARDENING PASS  
**Pre-flight**: Confirmed real EMS root `C:\Users\DELL\Desktop\PROJEXT\opt\ems_system`, main at d2ac628 (exactly as required), clean working tree, no WIP merged, no git add ., no production/auth bridge/visual changes attempted.

## 1. Documents Read (All 10 Required)

- `FACULTY_WEB_SUBPATH_SMOKE_SOURCE_REVIEW.md` — prior subpath smoke pass summary (Vite + Router + API env support added in 635e5f8)
- `FACULTY_WEB_SUBPATH_BUILD_VALIDATION_LOG.md` — root + /ems builds validated; assets correctly prefixed; i18n PASS; proxy SPA fallback required
- `FACULTY_WEB_ROOT_ASSUMPTION_AUDIT.md` — 41 matches; critical window.location + direct /api in useExportCenterPage, Schedule, Login, ErrorBoundary, services
- `FACULTY_WEB_API_BASE_PATH_AUDIT.md` — central api.ts good; direct bypasses in 5+ files remain
- `FACULTY_WEB_PORTAL_ENV_EXAMPLES.md` — clear defaults vs /ems + /ems-api examples
- `FACULTY_WEB_PROXY_REQUIREMENTS.md` — full SPA fallback + API proxy + headers + cookie notes
- `BACKEND_PROXY_ROOT_PATH_REVIEW.md` — backend ready for proxy headers/root_path; no code changes needed
- `FACULTY_WEB_PORTAL_100_PERCENT_READINESS_SCORE.md` — 38/100 overall (auth contract blocker dominant; frontend base/API at 85)
- `FACULTY_WEB_PORTAL_DEPLOYMENT_CHECKLIST.md` — mount path, proxy, auth, DB items tracked
- `FACULTY_WEB_PORTAL_IMPLEMENTATION_ROADMAP.md` — Stage 2 explicitly calls for this hardening pass after contract (but safe config work can proceed in parallel per notes)

## 2. What Was Validated Previously (Pre-Hardening)

- VITE_APP_BASE_PATH + VITE_API_BASE_URL support implemented and non-breaking for local dev (commit 635e5f8)
- BrowserRouter `basename` wired to env
- Central `frontend/src/services/api.ts` respects VITE_API_BASE_URL (default "/api")
- Root build: PASS (identical to demo-validated state)
- /ems + /ems-api subpath build: PASS (correct asset prefixes in dist/index.html)
- i18n checks: PASS in root mode
- Full proxy requirements, env examples, checklists, and roadmap documented
- No auth bridge, no Laravel assumptions, no production deployment

## 3. What Remains (Residual Risks Identified in Prior Audits)

**Root Path Assumptions (High Risk Under Subpath):**
- Direct `window.location.href = "/..."` and `window.open("/api/...")` in:
  - `frontend/src/hooks/domain/useExportCenterPage.ts`
  - `frontend/src/pages/Schedule.tsx`
  - `frontend/src/pages/Login.tsx` (SSO)
- `<a href="/dashboard">` in `frontend/src/components/layout/ErrorBoundary.tsx`
- Hardcoded internal paths in navigation/redirects that may ignore basename

**Direct API Calls (Bypass Central Helper):**
- Literal `"/api/..."` strings outside api.ts in:
  - useExportCenterPage.ts
  - Schedule.tsx
  - documents.service.ts
  - historicalSchedule.service.ts
  - Login.tsx (SSO)
- These will **not** receive VITE_API_BASE_URL unless centralized

**Safe / Low Risk:**
- Most `useNavigate("/...")`, `<Link to="...">`, and router-based navigation (respect basename)
- External links and intentional full-origin URLs

## 4. What This Pass Will Fix (Scope)

- Fresh complete inventory via rg + targeted file inspection (PHASE 2 + 5)
- Create `frontend/src/utils/appPaths.ts` helper (getAppBasePath, withAppBasePath) — only if low-risk and useful (PHASE 3)
- Minimal safe fixes for internal root redirects/links using helper or React Router (PHASE 4)
- Centralize **safe** direct application API calls via api.ts exports (add getApiBaseUrl / buildApiUrl if missing) (PHASE 6)
- Dedicated export/download URL review (PHASE 7)
- Re-run full root + subpath builds + i18n after changes (PHASE 8)
- Honest updates to readiness scorecards, checklist, roadmap (PHASE 9) — modest score lift possible
- Strict separation: docs commit first, then any code changes; explicit git add paths only; no . 

**Rules Strictly Observed:**
- Preserve local default "/" and "/api" behavior
- No route deletion, no permission changes, no auth bridge, no hard-coded /ems or portal.mis.pol... in source
- No visual redesign
- No backend changes expected
- No git add . ever

## 5. What Remains Blocked by IT/Auth Contract (Cannot Be Fixed in This Pass)

- Exact final mount paths (/ems vs other) — only example values used for validation
- Laravel / POLSCI OAuth contract (session("USS"), cmu_at, ServiceUrl, callback behavior, identity payload)
- Cookie domain / SameSite / Path policy under real faculty web domain
- Real reverse proxy (Nginx/Laravel) configuration and SPA fallback testing
- PostgreSQL target provisioning and ownership
- Print shop external lane final integration model under portal
- Any production or pilot deployment

These are explicitly documented as "DEFER UNTIL IT PATH CONFIRMED" or "NEEDS HUMAN REVIEW / CONTRACT" in the new audit tables.

## 6. Expected Outcomes of This Pass

- Reduced number of root-absolute assumptions in source
- Increased % of API calls going through central configurable helper
- Clear audit tables classifying every finding (FIX NOW / SAFE AS IS / FALSE POSITIVE / DEFER / NEEDS REVIEW)
- Updated validation log with post-hardening root + /ems builds
- Modest, honest improvement in "Route / Mount Path Readiness" and "Frontend Base Path + API Proxy Readiness" dimensions (still far from 100 due to auth gate)
- All changes small, testable, and preserving standalone demo at 98/100

## 7. Non-Goals (Explicitly Out of Scope)

- Implementing any part of the auth bridge
- Assuming any specific Laravel session behavior
- Hardcoding production portal URL or final subpath in runtime code
- Broad refactoring of routing or services
- Claiming production readiness or "100% portal ready"

---

**Status After This Pass**: "HARDENED WITH DOCUMENTED RESIDUALS" — frontend is more robust for subpath deployment once IT confirms paths and auth contract. Auth and hosting contract remain the immovable gate.

*Next atomic step: PHASE 2 — execute root assumption inventory with rg and create detailed audit table.*
