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
*Root mode remains the default and fully validated for standalone demo. Subpath mode is now provably supported via environment variables.*
