# EMS Full Route Visual Acceptance Source Review

Date: 2026-06-16

## Scope

This pass certifies current visual behavior only. It does not redesign route behavior and does not change backend APIs, calculations, authorization, payment/export/review/settings logic, or final-authorization boundaries.

## Preflight

- Working directory: `C:\Users\DELL\Desktop\PROJEXT\opt\ems_system`
- Branch: `main`
- Required history anchor present: `dd455a6 docs(ui): normalize remediation validation log`
- `git pull --ff-only origin main`: already up to date before certification work
- Backend health: `GET http://127.0.0.1:8000/api/health` returned HTTP 200 during certification
- Frontend dev server: `http://127.0.0.1:3000`
- Excel lock files: none found before capture
- Browser path: local Chrome DevTools Protocol was used because the in-app browser MCP was unavailable in this session

## Source Authorities Read

| Source | Use In This Pass |
| --- | --- |
| `frontend/src/App.tsx` | Authoritative route declaration inventory; 50 route declarations found |
| `frontend/src/config/navigation.ts` | Sidebar/mobile visibility, role metadata, hidden route cross-check |
| `frontend/src/utils/roles.ts` | Semantic role/default-route helpers and role guard behavior |
| `frontend/src/styles/tokens.css` | Canonical role/status/motion tokens |
| `frontend/src/components/layout/AppShell.tsx` | Runtime `data-role` and `data-density` source |
| `docs/architecture/EMS_UI_CONSOLIDATION_ROUTE_MATRIX.md` | Prior consolidation route context |
| `docs/architecture/UI_VISUAL_CONSOLIDATION_REMEDIATION_VALIDATION_LOG.md` | Remediation baseline for shell, trace, workload, and layout fixes |
| `docs/architecture/EMS_UI_PERMISSION_AND_ROLE_DRY_CONTRACT.md` | Role/permission model preservation |
| Payment safety docs and current payment UI pages | Draft-only and no-final-authorization visual checks |

## Drift Searches

Searches were run across `frontend/src` and relevant architecture docs for:

- Route declarations and navigation keys
- `data-role`, `data-density`, role accent tokens, universal status tokens
- `prefers-reduced-motion`, transitions, animation declarations
- Inline styles, hardcoded colors, `100vw`, sticky/fixed risks, blanket overflow hiding
- Raw technical labels such as `internal`, `boolean`, `session not found`
- Payment safety strings such as `DRAFT_NOT_AUTHORIZED` and `Final Authorization`

Findings:

- `tokens.css` remains the active canonical source for runtime role/status colors.
- `roleThemes.ts` still contains visual metadata constants, but this pass found no runtime mismatch in certified pages.
- Legacy hardcoded color utility rules remain in `components.css`; they are residual UI debt, not a new certification blocker.
- Two active visual blockers were confirmed and fixed in shared CSS only.
- No backend files, API schemas, route declarations, payment calculations, export bytes, review gates, or authorization blocks were changed.

## Route Declaration Inventory

| # | Route Declaration | Classification |
| --- | --- | --- |
| 1 | `/` | Redirect to role/default home |
| 2 | `/role-selection` | Renderable destination |
| 3 | `/login` | Renderable destination |
| 4 | `/student-search` | Renderable destination |
| 5 | `/dashboard` | Renderable destination |
| 6 | `/admin-intelligence-dashboard` | Renderable destination |
| 7 | `/schedule` | Renderable destination |
| 8 | `/analytics` | Renderable destination |
| 9 | `/workload-duty-analytics` | Renderable destination |
| 10 | `/duty-workload` | Renderable destination |
| 11 | `/my-workload` | Renderable destination |
| 12 | `/governance` | Renderable destination |
| 13 | `/submissions` | Renderable destination |
| 14 | `/attendance` | Renderable destination |
| 15 | `/checkins` | Renderable destination |
| 16 | `/swaps` | Renderable destination |
| 17 | `/swaps-v2` | Redirect to `/swaps` |
| 18 | `/sections` | Renderable destination |
| 19 | `/copy` | Renderable destination |
| 20 | `/print-queue` | Renderable destination |
| 21 | `/workflow` | Renderable destination |
| 22 | `/workflow-v2` | Redirect to `/workflow` |
| 23 | `/coexam` | Renderable destination |
| 24 | `/optimizer` | Renderable destination |
| 25 | `/optimizer-trace` | Renderable destination |
| 26 | `/staff-availability` | Renderable destination |
| 27 | `/printreview` | Renderable destination |
| 28 | `/external` | Renderable destination |
| 29 | `/exports-center` | Renderable destination |
| 30 | `/invigilation-advance-batch-preview` | Renderable destination |
| 31 | `/invigilation-rate-rules` | Renderable destination |
| 32 | `/invigilation-payment-document-draft` | Renderable destination |
| 33 | `/payment-document-settings` | Renderable destination |
| 34 | `/historical-schedules` | Renderable destination |
| 35 | `/import` | Renderable destination |
| 36 | `/import-audit` | Renderable destination |
| 37 | `/period` | Renderable destination |
| 38 | `/settings` | Renderable destination |
| 39 | `/settings-v2` | Redirect to `/settings` |
| 40 | `/platform-config` | Renderable destination |
| 41 | `/operational-health` | Renderable destination |
| 42 | `/audit-explorer` | Renderable destination |
| 43 | `/rooms-v2` | Renderable destination |
| 44 | `/venues-v2` | Renderable destination |
| 45 | `/students-v2` | Renderable destination |
| 46 | `/users` | Renderable destination |
| 47 | `/users-v2` | Redirect to `/users` |
| 48 | `/myexam` | Renderable destination |
| 49 | `/exammanager` | Renderable destination |
| 50 | `*` | Not-found/system state |

## Evidence Summary

- Screenshots captured: 176 PNG files
- Evidence directory: `docs/operations/demo-smoke-screenshots/full-route-visual-certification/`
- Roles covered: `admin`, `esq_head`, `secretary`, `dept_supervisor`, `staff`, `teacher`, `print_shop`, public/student search, guest/system states
- Viewports covered: `1600x900`, `1366x768`, `1024x768`, and selected mobile-critical `390x844`
- Languages: Thai for all primary coverage; English for representative route families and changed/payment-critical pages
- Reduced motion: dashboard, workflow, and payment draft sampled with reduced-motion mode

## Source Boundary Confirmation

Only frontend CSS, certification docs, and certification screenshots are in scope for this pass. Backend, route declarations, permission helpers, payment/export services, review/settings logic, optimizer/workload calculations, and final authorization behavior remain unchanged.
