# FACULTY_WEB_ROOT_PATH_HARDENING_AUDIT.md

**Date**: 2026-05-25  
**Pass**: EMS FACULTY WEB PORTAL ROOT ASSUMPTION + API BASE HARDENING PASS  
**Pre-flight**: main@d2ac628, clean tree, all rules followed.

## Inventory Method
- rg searches executed via available codebase search tools for:
  - `window.location`
  - `location.href`
  - `href="/` and `href='/`
  - `navigate("/` and `navigate("/`
  - `to="/` and `to='/`
- Targeted inspection of files flagged in prior audit + current search results:
  - frontend/src/components/layout/ErrorBoundary.tsx
  - frontend/src/pages/ExportCenter.tsx (via hook)
  - frontend/src/pages/Schedule.tsx
  - frontend/src/pages/Login.tsx
  - frontend/src/components/layout/Sidebar.tsx
  - frontend/src/App.tsx
  - frontend/src/config/navigation.ts
  - frontend/src/hooks/domain/useExportCenterPage.ts
  - frontend/src/services/api.ts
  - frontend/src/store/auth.store.tsx

## Full Findings Table

| # | File | Pattern | Line(s) | Current Risk under /ems | Safe Fix? | Action (This Pass) | Classification | Notes |
|---|------|---------|---------|---------------------------|-----------|--------------------|----------------|-------|
| 1 | frontend/src/hooks/domain/useExportCenterPage.ts | `window.location.href = "/copy"` | 109 | High — bypasses basename, lands at root /copy instead of /ems/copy | Yes (use withAppBasePath or router) | FIX: wrap with helper or replace with navigate (preferred) | **FIX NOW** | Internal app page for admin. Low-risk change. |
| 2 | frontend/src/hooks/domain/useExportCenterPage.ts | `window.location.href = "/workflow"` | 116 | High | Yes | FIX: use helper or navigate | **FIX NOW** | Admin-only internal link from Export Center |
| 3 | frontend/src/hooks/domain/useExportCenterPage.ts | `window.location.href = "/external"` | 121 | High | Yes | FIX: use helper or navigate | **FIX NOW** | Admin-only |
| 4 | frontend/src/hooks/domain/useExportCenterPage.ts | `window.location.href = "/historical-schedules"` | 126 | High | Yes | FIX: use helper or navigate | **FIX NOW** | Admin-only |
| 5 | frontend/src/components/layout/ErrorBoundary.tsx | `<a href="/dashboard">` | 84 | Medium — recovery link after crash | Yes (React Router Link or helper) | FIX: replace with Link to="/dashboard" (or withBase helper) | **FIX NOW** | Simple, safe, improves resilience |
| 6 | frontend/src/pages/Schedule.tsx | `window.open("/api/exports/schedule-excel", ...)` | 108 | API download — risk is API base, **not** app root path | Yes (central API helper) | Defer to PHASE 5/6 (API hardening) | DEFER (API) | Intentional browser download trigger |
| 7 | frontend/src/pages/Schedule.tsx | `window.open("/api/exports/schedule", ...)` | 116 | Same as above | Yes | Defer to PHASE 5/6 | DEFER (API) | Same |
| 8 | frontend/src/pages/Login.tsx | `window.location.href = \`/api/auth/sso/login...\`` | 155 | SSO redirect to backend auth — API/auth path | Yes (central API) | Defer to PHASE 5/6 | DEFER (API) | Must hit real backend SSO endpoint; will be covered by VITE_API_BASE_URL centralization |
| 9 | frontend/src/services/documents.service.ts | `new URL("/api/documents/export-pdf", window.location.origin)` | 37 | Direct /api in URL constructor | Yes (use buildApiUrl) | Defer to PHASE 5/6 | DEFER (API) | Export URL builder |
| 10 | frontend/src/services/api.ts | `new URL(..., window.location.origin)` (only for origin) | 33 | Correct use of origin to build absolute URL from relative API path | No risk | SAFE AS IS | **SAFE AS IS** | The `${API_BASE}` already comes from VITE_API_BASE_URL |
| 11 | frontend/src/store/auth.store.tsx | `window.location.pathname` | 128 | Reading current path for redirect logic | None — pathname reading is always relative to current base | SAFE AS IS | **SAFE AS IS** | Used for post-login redirect preservation |
| 12 | All `navigate("/xxx")` calls (Dashboard, Login, RoleSelection, RoomAttendance, etc. ~16 sites) | `navigate("/dashboard")` etc. | various | None — React Router `navigate` + `basename` on BrowserRouter handles subpath automatically | N/A | SAFE AS IS | **SAFE AS IS** | Already protected by prior basename wiring (635e5f8) |
| 13 | `<Navigate to="..." />` in App.tsx (v2 redirects) | `<Navigate replace to="/swaps" />` etc. | 253,286,383,440 | Low — RR Navigate respects basename for absolute paths starting with / | N/A | SAFE AS IS | **SAFE AS IS** | Internal v2→current route aliases |
| 14 | Sidebar NavLink + navigation.ts paths | `to={page.path}` where path="/dashboard" etc. | many | None — NavLink respects basename | N/A | SAFE AS IS | **SAFE AS IS** | All page.path values are router paths |
| 15 | Any other root-absolute strings | (none found in additional broad searches) | — | — | — | — | **FALSE POSITIVE** | No additional raw href="/ or window.location to root paths outside the 5 listed above |

## Classification Summary

- **FIX NOW**: 5 items (4 window.location.href internal in useExportCenterPage.ts + 1 <a href> in ErrorBoundary.tsx)
- **SAFE AS IS**: All React Router navigation (navigate, Link/NavLink, Navigate), pathname reads, and correct origin usage in api.ts
- **DEFER (API)**: 4 direct /api strings — handled in PHASE 5/6 (export/download + SSO)
- **FALSE POSITIVE**: 0 additional after full search
- **NEEDS HUMAN REVIEW / DEFER UNTIL IT PATH CONFIRMED**: 0 for pure root-path navigation (auth contract items are in separate API/auth audits)

## Risk Reduction After This Pass

Before: 5+ direct root-absolute navigation paths that would break under any subpath mount.

After planned fixes: 0 direct root-absolute internal app navigation using window.location or raw <a href>.

All remaining navigation will go through React Router (basename-aware) or the new centralized appPaths helper for the few unavoidable full-reload cases.

## Recommendations for Future (Documented, Not In Scope)

- Prefer `useNavigate()` + `Link` everywhere for SPA navigation.
- Reserve `window.location` / full reload only for true cross-app or post-auth full resets (and always wrap via helper).
- Once auth contract is known, review the SSO Login redirect path carefully (it may legitimately need the proxied API prefix).

---

**Status**: Inventory complete. 5 actionable root-path fixes identified for PHASE 4. All router-based navigation already safe. API-related items moved to PHASE 5/6.

*Next: PHASE 3 — evaluate + create appPaths.ts helper (low risk, high value for the 5 fixes).*
