# DEMO_ROUTE_SMOKE_MAP.md

**Date**: 2026-05-22
**Purpose**: Map every EMS route to its expected demo state. This is the route inventory used by the demo script and preflight checks.

---

## Route Inventory

| Route | Role | Expected State | Demo Priority | Current Status | Issue | Action |
|-------|------|---------------|---------------|---------------|-------|--------|
| `/` | Any | Redirect to role-selection or dashboard | HIGH | REVIEW | Known redirect path | Verify after login |
| `/role-selection` | Public | Role selection landing page | HIGH | REVIEW | Public entry | Verify load |
| `/login` | Public | Login page | HIGH | REVIEW | Should work | Verify load |
| `/student-search` | Public | Public student schedule lookup | MEDIUM | REVIEW | Public route | Verify load |
| `/dashboard` | All roles | Main role-aware dashboard | CRITICAL | REVIEW | Core demo route | Verify data loads |
| `/admin-intelligence-dashboard` | admin | Admin 10-group intelligence | HIGH | MAY NEED FIX | Service positional-arg issue may cause load error | Fix before demo |
| `/workload-duty-analytics` | admin | Admin workload analytics | HIGH | REVIEW | Core analytics route | Verify data loads |
| `/duty-workload` | staff/dept/esq/secretary | Staff workload analytics | HIGH | REVIEW | Core analytics route | Verify data loads |
| `/my-workload` | teacher | Teacher workload analytics | HIGH | REVIEW | Core analytics route | Verify data loads |
| `/analytics` | admin/esq/secretary | Executive Analytics | HIGH | MAY NEED FIX | Error message in local build | Verify |
| `/governance` | admin/esq/secretary | Governance Cockpit | HIGH | REVIEW | Untranslated i18n keys | Verify translate fallback |
| `/operational-health` | admin/esq_head | System health page | HIGH | REVIEW | Backend endpoint exists | Verify data loads |
| `/audit-explorer` | admin/esq_head | Audit log explorer | HIGH | REVIEW | Backend route exists | Verify data loads |
| `/schedule` | All roles | Exam schedule listing | HIGH | REVIEW | Core operational route | Verify |
| `/submissions` | Most roles | Submission listing | HIGH | REVIEW | Core operational route | Verify |
| `/attendance` | All roles | Room attendance | MEDIUM | REVIEW | Empty state ok | Verify |
| `/checkins` | admin/dept/staff/teacher | Check-in QR | MEDIUM | REVIEW | Empty state ok | Verify |
| `/swaps` | admin/dept/staff/teacher | Swap requests | MEDIUM | REVIEW | Empty state ok | Verify |
| `/myexam` | teacher | Teacher exam work | HIGH | REVIEW | Core teacher route | Verify |
| `/workflow` | admin/esq/secretary | Workflow/pipeline | MEDIUM | REVIEW | Route exists | Verify |
| `/optimizer` | admin | Scheduling optimizer | MEDIUM | REVIEW | Route exists | Verify |
| `/optimizer-trace` | admin | Optimization trace | MEDIUM | REVIEW | Route exists | Verify |
| `/optimizer-trace/{id}` | admin | Optimization trace detail | MEDIUM | REVIEW | Route exists | Verify |
| `/copy` | admin/staff | Copy count | MEDIUM | REVIEW | Empty state ok | Verify |
| `/print-queue` | print_shop | Print shop queue | LOW | REVIEW | print_shop role only | Verify |
| `/printreview` | admin/esq/secretary | Print review | MEDIUM | REVIEW | Route exists | Verify |
| `/coexam` | admin | Co-exam planning | LOW | REVIEW | admin only | Verify |
| `/exports-center` | admin/staff | Export hub | MEDIUM | REVIEW | Route exists | Verify |
| `/historical-schedules` | admin | Historical schedule import | MEDIUM | REVIEW | Route exists | Verify |
| `/import` | admin | Import data | MEDIUM | REVIEW | Route exists; V2 page |
| `/import-audit` | admin | Import audit trail | MEDIUM | REVIEW | Route exists | Verify |
| `/sections` | All roles | Section listing | MEDIUM | REVIEW | Core route | Verify |
| `/users` | admin | User management | HIGH | REVIEW | V2 page in use | Verify |
| `/period` | admin | Exam period management | MEDIUM | REVIEW | Route exists | Verify |
| `/settings` | admin | System settings | MEDIUM | REVIEW | V2 page in use; settingsV2Page | Verify |
| `/platform-config` | admin | Platform config board | MEDIUM | REVIEW | May have loading state | Verify |
| `/rooms-v2` | admin | Room management | MEDIUM | REVIEW | V2 page in use | Verify |
| `/venues-v2` | admin (hidden) | Venue mgmt | LOW | HIDDEN | Hidden route | Verify if demo needed |
| `/students-v2` | admin (hidden) | Student records | LOW | HIDDEN | Hidden route | Verify if demo needed |
| `/coexam-v2` | Redirect | → `/coexam` | LOW | REDIRECT | Not demo critical | Skip |
| `/swaps-v2` | Redirect | → `/swaps` | LOW | REDIRECT | Not demo critical | Skip |
| `/users-v2` | Redirect | → `/users` | LOW | REDIRECT | Not demo critical | Skip |
| `/settings-v2` | Redirect | → `/settings` | LOW | REDIRECT | Not demo critical | Skip |
| `/staff-availability` | admin | Staff availability | MEDIUM | REVIEW | Route exists | Verify |
| `/external` | admin/staff | External exams | MEDIUM | REVIEW | Route exists | Verify |
| `/exammanager` | admin/dept_supervisor | Course ownership | MEDIUM | REVIEW | Route exists | Verify |

---

## Route Status Summary

| Status | Count | Notes |
|--------|-------|-------|
| CRITICAL / Must work | 5 | /dashboard, /submissions, /schedule, /login, /myexam |
| HIGH / Should work | 8 | /admin-intelligence, /workload-*, /analytics, /governance, /operational-health, /audit-explorer, /users, /settings |
| MEDIUM / Nice to have | 16 | /optimizer, /checkins, /printreview, etc. |
| REDIRECT / Skip | 4 | /swaps-v2, /coexam-v2, /users-v2, /settings-v2 |
| HIDDEN / Optional | 2 | /venues-v2, /students-v2 |
| NOT YET CONFIRMED | 0 | — |

---

**End of DEMO_ROUTE_SMOKE_MAP.md**
