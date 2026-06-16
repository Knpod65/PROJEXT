# EMS Full Route Visual Acceptance Matrix

Date: 2026-06-16

## Result

Overall result: `CERTIFIED_WITH_DOCUMENTED_P2`

Summary:

- 176 browser evidence captures
- 172 accepted captures
- 4 documented P2 captures
- 0 unresolved P0 defects
- 0 unresolved P1 defects
- 50 route declarations inventoried from `frontend/src/App.tsx`
- 47 renderable destinations/states directly represented in the evidence matrix, including blocked states and direct secretary evidence

## Acceptance Rules Applied

Each certified page/state was checked for:

- Exactly one visible primary `h1`
- No document-level horizontal overflow
- No raw i18n keys or raw backend error strings
- No raw enum/status-token presentation in the visible UI sample
- Correct `data-role` role accent where authenticated
- Universal status colors remaining independent of role accents
- Payment/document pages preserving draft-only and no-final-authorization boundaries

## Evidence Matrix

| Family | Role | Route | Evidence | Languages | Result | Representative Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| auth-public | guest | `/login` | 390,1024,1366,1600 | en,th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/guest-login-1600-th.png` |
| auth-public | guest | `/role-selection` | 390,1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/guest-role-selection-1600-th.png` |
| auth-public | public | `/student-search` | 390,1024,1366,1600 | en,th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/public-student-search-1600-th.png` |
| blocked | print_shop | `/payment-document-settings` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/print_shop-unauthorized-settings-1600-th.png` |
| blocked | teacher | `/invigilation-payment-document-draft` | 390,1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/teacher-unauthorized-payment-draft-1600-th.png` |
| dashboard | admin | `/admin-intelligence-dashboard` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-admin-intelligence-dashboard-1600-th.png` |
| dashboard | admin | `/dashboard` | 390,1024,1366,1600 plus reduced motion | en,th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-dashboard-1600-th.png` |
| dashboard | esq_head | `/analytics` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/esq_head-analytics-1600-th.png` |
| exam | admin | `/import` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-import-1600-th.png` |
| exam | admin | `/import-audit` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-import-audit-1600-th.png` |
| exam | dept_supervisor | `/exammanager` | 1024,1366,1600 | en,th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/dept_supervisor-exammanager-1600-th.png` |
| exam | teacher | `/myexam` | 390,1024,1366,1600 | en,th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/teacher-myexam-1600-th.png` |
| exam | teacher | `/sections` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/teacher-sections-1600-th.png` |
| exam | teacher | `/submissions` | 390,1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/teacher-submissions-1600-th.png` |
| governance | admin | `/historical-schedules` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-historical-schedules-1600-th.png` |
| governance | esq_head | `/governance` | 1024,1366,1600 | en,th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/esq_head-governance-1600-th.png` |
| governance | esq_head | `/workflow` | 1024,1366,1600 plus reduced motion | en,th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/esq_head-workflow-1600-th.png` |
| operations | admin | `/coexam` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-coexam-1600-th.png` |
| operations | admin | `/optimizer` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-optimizer-1600-th.png` |
| operations | admin | `/optimizer-trace` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-optimizer-trace-1600-th.png` |
| operations | admin | `/rooms-v2` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-rooms-v2-1600-th.png` |
| operations | admin | `/schedule` | 390,1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-schedule-1600-th.png` |
| operations | admin | `/staff-availability` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-staff-availability-1600-th.png` |
| operations | admin | `/venues-v2` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-venues-v2-1600-th.png` |
| operations | esq_head | `/printreview` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/esq_head-printreview-1600-th.png` |
| operations | print_shop | `/print-queue` | 1024,1366,1600 | en,th | CERTIFIED_WITH_P2 | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/print_shop-print-queue-1600-th.png` |
| operations | staff | `/attendance` | 390,1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/staff-attendance-1600-th.png` |
| operations | staff | `/checkins` | 390,1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/staff-checkins-1600-th.png` |
| operations | staff | `/copy` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/staff-copy-1600-th.png` |
| operations | staff | `/exports-center` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/staff-exports-center-1600-th.png` |
| operations | staff | `/external` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/staff-external-1600-th.png` |
| operations | teacher | `/swaps` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/teacher-swaps-1600-th.png` |
| payment | admin | `/invigilation-payment-document-draft` | 1024,1366,1600 plus reduced motion | en,th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-invigilation-payment-document-draft-1600-th.png` |
| payment | esq_head | `/payment-document-settings` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/esq_head-payment-document-settings-1600-th.png` |
| payment | staff | `/invigilation-advance-batch-preview` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/staff-invigilation-advance-batch-preview-1600-th.png` |
| payment | staff | `/invigilation-rate-rules` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/staff-invigilation-rate-rules-1600-th.png` |
| people | admin | `/students-v2` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-students-v2-1600-th.png` |
| people | admin | `/users` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-users-1600-th.png` |
| secretary-direct | secretary | `/analytics` | 1366 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/secretary-analytics-1366-th.png` |
| secretary-direct | secretary | `/attendance` | 1366 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/secretary-attendance-1366-th.png` |
| secretary-direct | secretary | `/dashboard` | 1366 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/secretary-dashboard-1366-th.png` |
| secretary-direct | secretary | `/duty-workload` | 1366 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/secretary-duty-workload-1366-th.png` |
| secretary-direct | secretary | `/governance` | 1366 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/secretary-governance-1366-th.png` |
| secretary-direct | secretary | `/payment-document-settings` | 1366 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/secretary-payment-document-settings-1366-th.png` |
| secretary-direct | secretary | `/printreview` | 1366 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/secretary-printreview-1366-th.png` |
| secretary-direct | secretary | `/schedule` | 1366 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/secretary-schedule-1366-th.png` |
| secretary-direct | secretary | `/sections` | 1366 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/secretary-sections-1366-th.png` |
| secretary-direct | secretary | `/submissions` | 1366 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/secretary-submissions-1366-th.png` |
| secretary-direct | secretary | `/workflow` | 1366 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/secretary-workflow-1366-th.png` |
| system | admin | `/period` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-period-1600-th.png` |
| system | admin | `/platform-config` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-platform-config-1600-th.png` |
| system | admin | `/settings` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-settings-1600-th.png` |
| system | esq_head | `/audit-explorer` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/esq_head-audit-explorer-1600-th.png` |
| system | esq_head | `/operational-health` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/esq_head-operational-health-1600-th.png` |
| system | guest | `/definitely-not-a-real-route` | 390,1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/guest-not-found-1600-th.png` |
| workload | admin | `/workload-duty-analytics` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/admin-workload-duty-analytics-1600-th.png` |
| workload | staff | `/duty-workload` | 1024,1366,1600 | en,th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/staff-duty-workload-1600-th.png` |
| workload | teacher | `/my-workload` | 1024,1366,1600 | th | CERTIFIED | `docs/operations/demo-smoke-screenshots/full-route-visual-certification/teacher-my-workload-1600-th.png` |

## Redirects And Aliases

Redirect aliases were inventoried but not screenshot as separate visual destinations:

- `/` redirects to the active role default route or public entry route.
- `/swaps-v2` redirects to `/swaps`.
- `/workflow-v2` redirects to `/workflow`.
- `/settings-v2` redirects to `/settings`.
- `/users-v2` redirects to `/users`.

## Remaining P2

`/print-queue` is certified with documented P2 because the automated sweep observed a browser log event on the print queue route. A focused live probe only reproduced normal Vite/React development console messages and no visible page failure. The visual acceptance criteria still passed: one primary heading, zero overflow, correct print-shop role theme, no raw keys, and no payment-safety risk.
