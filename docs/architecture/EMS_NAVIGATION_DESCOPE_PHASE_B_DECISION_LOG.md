# EMS Navigation De-Scope Phase B Decision Log

## Summary

Phase B hides non-core diagnostics and enterprise-style pages from the main EMS sidebar while keeping their routes, components, and existing guards active. It also restores missing canonical sidebar entries for already-routed core workflows so the visible menu still contains the primary exam-operation paths. This is a reversible navigation-only change after repository hygiene commit `44dfbb7` was pushed to `origin/main`.

## Pages Hidden From Main Navigation

| Page | Route | Navigation key | Route kept active | Reason |
| ---- | ----- | -------------- | ----------------- | ------ |
| Admin Intelligence Dashboard | `/admin-intelligence-dashboard` | `admin-intelligence-dashboard` | Yes | Demo/intelligence signal, not daily exam operations. |
| Executive Analytics | `/analytics` | `executive-analytics` | Yes | Enterprise trend analysis, not pilot exam workflow. |
| Governance Cockpit | `/governance` | `governance-cockpit` | Yes | Overlaps Dashboard and Workflow; enterprise framing. |
| Operational Health | `/operational-health` | `operational-health` | Yes | IT/dev monitoring, not faculty workflow. |
| Audit Explorer | `/audit-explorer` | `audit-explorer` | Yes | Compliance/dev audit tool, not daily operations. |
| Optimizer Trace | `/optimizer-trace` | `optimizer-trace` | Yes | Optimizer debug trace, too technical for normal sidebar. |
| Platform Configuration | `/platform-config` | `platform-configuration` | Yes | Deep platform/governance configuration, not daily exam ops. |
| Import Audit | `/import-audit` | `import-audit` | Yes | Useful admin review tool, but not a persistent sidebar item. |

## Routes Kept Active

No route declarations were removed from `frontend/src/App.tsx`. Direct URL access remains governed by the existing `GuardedPage` role lists:

| Route | Existing roles retained |
| ----- | ----------------------- |
| `/admin-intelligence-dashboard` | `admin` |
| `/analytics` | `admin`, `esq_head`, `secretary` |
| `/governance` | `admin`, `esq_head`, `secretary` |
| `/operational-health` | `admin`, `esq_head` |
| `/audit-explorer` | `admin`, `esq_head` |
| `/optimizer-trace` | `admin` |
| `/platform-config` | `admin` |
| `/import-audit` | `admin` |

## Visible Core Navigation Preserved

The following exam-operation areas remain visible through the existing navigation config and role filters:

| Area | Representative routes |
| ---- | --------------------- |
| Dashboard and schedule | `/dashboard`, `/schedule` |
| Import and exam setup | `/import`, `/period`, `/rooms-v2`, `/sections`, `/exammanager` |
| Invigilation work | `/optimizer`, `/staff-availability`, `/workload-duty-analytics`, `/duty-workload`, `/my-workload`, `/swaps`, `/myexam` |
| Paper and print handoff | `/submissions`, `/printreview`, `/copy`, `/print-queue`, `/checkins`, `/attendance` |
| Draft payment support | `/invigilation-rate-rules`, `/invigilation-payment-document-draft`, `/invigilation-advance-batch-preview`, `/payment-document-settings` |
| Exports and secondary review | `/exports-center`, `/workflow`, `/external`, `/coexam`, `/historical-schedules` |

Historical Schedules remains visible in the sidebar for its existing `admin` role and remains route-active at `/historical-schedules`.

The following already-routed core pages were missing from the canonical sidebar config before Phase B and were restored as visible nav entries with their existing route-guard role sets:

| Restored sidebar entry | Route |
| ---------------------- | ----- |
| Schedule | `/schedule` |
| Submissions | `/submissions` |
| Room Attendance | `/attendance` |
| Check-ins | `/checkins` |
| Swap Requests | `/swaps` |

## Roles Affected

| Role | Sidebar effect |
| ---- | -------------- |
| `admin` | Removes the eight non-core diagnostics/enterprise pages from normal sidebar. Core exam, print, payment draft, export, setup, and history entries remain visible according to existing role filters. |
| `esq_head` | Removes Executive Analytics, Governance Cockpit, Operational Health, and Audit Explorer from normal sidebar. Core dashboard, schedule, workload, submissions, print review, attendance, payment document settings, workflow, and exports remain visible. |
| `secretary` | Removes Executive Analytics and Governance Cockpit from normal sidebar. Core dashboard, schedule, workload, submissions, print review, attendance, payment document settings, workflow, and exports remain visible. |
| `dept_supervisor` | No hidden Phase B items were visible before; schedule, submissions, attendance, check-ins, and swaps are present as core sidebar entries. |
| `staff` | No hidden Phase B items were visible before; schedule, attendance, check-ins, and swaps are present as core sidebar entries. |
| `teacher` | No hidden Phase B items were visible before; schedule, submissions, attendance, check-ins, and swaps are present as core sidebar entries. |
| `print_shop` | No hidden Phase B items were visible before; print queue remains the only visible sidebar entry. |

## Safety Boundaries

| Boundary | Result |
| -------- | ------ |
| Routes removed | NO |
| Page files deleted | NO |
| Route guards changed | NO |
| Role permissions changed | NO |
| Backend changed | NO |
| Scheduling or optimization logic changed | NO |
| Payment/export/review/settings logic changed | NO |
| Final approval or authorization added | NO |

## Rollback

Revert the Phase B commit, or remove `hidden: true` from the eight navigation entries in `frontend/src/config/navigation.ts` and remove the five restored core sidebar entries if returning to the exact previous menu shape is required. Because routes and components are retained, rollback only affects sidebar visibility.
