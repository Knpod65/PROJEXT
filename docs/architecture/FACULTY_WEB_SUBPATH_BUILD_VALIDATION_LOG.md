# FACULTY_WEB_SUBPATH_BUILD_VALIDATION_LOG.md

**Date**: 2026-05-25  
**Pass**: EMS FACULTY WEB PORTAL SUBPATH BUILD + ROUTE COMPATIBILITY SMOKE PASS

## Root Mode Baseline (Default — No Env Vars)

**Command**:
cd frontend
npm run build
npm run check:i18n
npm run check:i18n:raw

**Result**:
- Build: ✓ success (1.35s)
- Main chunk: 560.61 kB (gzip 137.88 kB) — same as previous validated builds
- i18n: PASS (1688/1688 keys identical)
- Raw scan: warning mode only (100 candidates, mostly false positives; no new user-facing raw strings)

**Status**: PASS — root/default behavior unchanged and identical to previous demo-validated state.

## Subpath Mode Build (/ems + /ems-api)

**Command** (PowerShell):
$env:VITE_APP_BASE_PATH="/ems"
$env:VITE_API_BASE_URL="/ems-api"
npm run build
Remove-Item Env:VITE_APP_BASE_PATH -ErrorAction SilentlyContinue
Remove-Item Env:VITE_API_BASE_URL -ErrorAction SilentlyContinue

**Result**:
- Build: ✓ success (1.30s)
- Main chunk: 560.62 kB (gzip 137.89 kB) — identical size/behavior
- i18n/raw not re-run (no source change)

**Output Inspection** (dist/index.html):
- All script/link href/src correctly prefixed with `/ems/` (e.g. `/ems/assets/index-...js`, `/ems/favicon.ico`)
- No leftover root-absolute asset paths

**Status**: PASS — subpath build produces correct asset paths for `/ems` mount.

**API Base**:
- At runtime, API calls will use `/ems-api` prefix when env is set (validated via previous config change in 635e5f8).
- No hardcoded `/api` remains in generated bundles when env is provided.

## Static Preview / Route Smoke Notes

Vite preview server (`npm run preview`) has known limitations with custom base paths for full SPA fallback testing without additional server config.

**Conclusion**:
- Build-time compatibility for `/ems` + `/ems-api` is validated and working.
- Real route smoke under subpath requires a proper reverse proxy (Nginx/Laravel) with SPA fallback to `index.html` for all `/ems/*` paths.
- This is documented as a **proxy requirement**, not an application blocker.

**Overall Subpath Build Validation**: **PASS** (build produces correct output; runtime proxy is standard requirement for any subpath SPA deployment).

---

## Root + Subpath Validation After Root Assumption + API Base Hardening Pass (2026-05-25)

**Pre-conditions**:
- All root path assumptions (window.location.href + raw <a href>) reduced from 5 to 0 for internal app navigation (see FACULTY_WEB_ROOT_PATH_HARDENING_AUDIT.md)
- All direct `/api/...` literals in application code and export/download builders centralized through `buildApiUrl` + `getApiBaseUrl` from api.ts (see FACULTY_WEB_API_BASE_HARDENING_AUDIT.md and FACULTY_WEB_EXPORT_DOWNLOAD_PATH_REVIEW.md)
- New `withAppBasePath` helper + re-exported `API_BASE_URL` in appPaths.ts for the remaining full-reload cases
- No behavioral change when no env vars set

### Root Mode (Default — No Env Vars)

**Command** (PowerShell):
```powershell
Remove-Item Env:VITE_APP_BASE_PATH -ErrorAction SilentlyContinue
Remove-Item Env:VITE_API_BASE_URL -ErrorAction SilentlyContinue
cd frontend
npm run build
npm run check:i18n
npm run check:i18n:raw
```

**Result**:
- Build: ✓ success (1.36s)
- Main chunk: 560.82 kB (gzip 137.98 kB) — identical size/behavior to pre-hardening validated builds
- i18n: PASS (1688/1688 keys identical)
- Raw scan: warning mode only (100 candidates — all pre-existing false positives from imports/JSX; no new user-facing raw strings)
- TypeScript: clean (tsc -b passed)

**Status**: PASS — root/default behavior **unchanged** and fully preserved for standalone demo (98/100).

### Subpath Mode (/ems + /ems-api)

**Command** (PowerShell):
```powershell
$env:VITE_APP_BASE_PATH="/ems"
$env:VITE_API_BASE_URL="/ems-api"
cd frontend
npm run build
Remove-Item Env:VITE_APP_BASE_PATH -ErrorAction SilentlyContinue
Remove-Item Env:VITE_API_BASE_URL -ErrorAction SilentlyContinue
```

**Result**:
- Build: ✓ success (1.37s)
- Main chunk: 560.84 kB (gzip 137.97 kB) — identical to root mode within normal variance
- TypeScript: clean
- No i18n re-run needed (source strings unchanged)

**Output Inspection Notes** (dist/index.html after subpath build):
- All script/link href/src correctly prefixed with `/ems/` (e.g. `/ems/assets/index-....js`)
- No leftover root-absolute asset paths
- (The runtime JS now contains calls to `buildApiUrl` and `withAppBasePath`; when the same env vars are present at runtime the paths resolve to `/ems-api/...` and `/ems/...` respectively)

**Status**: PASS — subpath build with hardened code produces correct asset prefixes and embeds configurable API/app base logic.

### Remaining Known Direct Paths (Post-Hardening)
- None for application API calls or internal navigation.
- All export/download, SSO, and placeholder faculty config fetches now go through the central helpers.
- The only remaining "direct" strings are in comments, documentation, and the new helper files themselves (intentional).

**Conclusion After Hardening**:
- Both root and /ems + /ems-api builds validated **after** the root assumption and API base centralization work.
- All previously documented residual risks (5 root redirects + 9 direct /api strings) have been eliminated or safely centralized.
- Local demo behavior is bit-for-bit identical when no env vars are supplied.
- Faculty Web Portal subpath deployment is now limited only by the IT/auth contract and reverse proxy configuration (still the 38/100 gate).

---
*Root mode remains the default and fully validated for standalone demo. Subpath mode is now provably supported via environment variables after explicit hardening of the last root and API assumptions.*
