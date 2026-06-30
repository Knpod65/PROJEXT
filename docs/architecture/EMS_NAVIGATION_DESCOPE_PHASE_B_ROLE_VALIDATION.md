# EMS Navigation De-Scope Phase B Role Validation

## Validation Method

Role-menu validation was performed against the canonical navigation config, `frontend/src/config/navigation.ts`, and the sidebar filtering behavior in `frontend/src/components/layout/Sidebar.tsx`. Route guard validation was checked against unchanged route declarations in `frontend/src/App.tsx`.

The sidebar excludes any page where `hidden: true`, then applies the existing role filters through `hasRole`. Phase B changes sidebar visibility only; route guards remain unchanged. Five already-routed core workflow pages were also restored to the sidebar config so the main menu retains the expected exam-operation paths.

## Hidden Page Validation

| Hidden page | Route | Sidebar hidden | Direct route retained | Existing guard retained |
| ----------- | ----- | -------------- | --------------------- | ----------------------- |
| Admin Intelligence Dashboard | `/admin-intelligence-dashboard` | Yes | Yes | `admin` |
| Executive Analytics | `/analytics` | Yes | Yes | `admin`, `esq_head`, `secretary` |
| Governance Cockpit | `/governance` | Yes | Yes | `admin`, `esq_head`, `secretary` |
| Operational Health | `/operational-health` | Yes | Yes | `admin`, `esq_head` |
| Audit Explorer | `/audit-explorer` | Yes | Yes | `admin`, `esq_head` |
| Optimizer Trace | `/optimizer-trace` | Yes | Yes | `admin` |
| Platform Configuration | `/platform-config` | Yes | Yes | `admin` |
| Import Audit | `/import-audit` | Yes | Yes | `admin` |

## Role Menu Result

| Role | Result |
| ---- | ------ |
| `admin` | Sidebar no longer shows Admin Intelligence, Executive Analytics, Governance Cockpit, Optimizer Trace, Import Audit, Platform Configuration, Operational Health, or Audit Explorer. Core exam-operation entries remain visible. |
| `esq_head` | Sidebar no longer shows Executive Analytics, Governance Cockpit, Operational Health, or Audit Explorer. Dashboard, schedule, workload, submissions, attendance, print review, payment document settings, workflow, and sections remain visible. |
| `secretary` | Sidebar no longer shows Executive Analytics or Governance Cockpit. Dashboard, schedule, workload, submissions, attendance, print review, payment document settings, workflow, and sections remain visible. |
| `dept_supervisor` | No enterprise/dev Phase B entries are visible. Dashboard, schedule, sections, workload, swaps, submissions, check-in, attendance, and exam-manager entries remain visible. |
| `staff` | No enterprise/dev Phase B entries are visible. Dashboard, schedule, sections, workload, swaps, copy, check-in, attendance, payment draft/supporting, export, and external entries remain visible. |
| `teacher` | No enterprise/dev Phase B entries are visible. Dashboard, schedule, sections, workload, swaps, my exam, submissions, check-in, and attendance entries remain visible. |
| `print_shop` | Sidebar remains focused on print queue only. |
| public/student | Public student search remains hidden from authenticated sidebar and available through public routing. |

## Core Route Preservation

| Route family | Validation result |
| ------------ | ----------------- |
| Schedule and exam setup | `/schedule`, `/import`, `/rooms-v2`, `/period`, `/sections`, and `/exammanager` remain configured. |
| Invigilation | `/optimizer`, `/staff-availability`, workload routes, `/swaps`, and `/myexam` remain configured. |
| Paper handoff and print | `/submissions`, `/printreview`, `/copy`, `/print-queue`, `/checkins`, and `/attendance` remain configured. |
| Draft payment support | `/invigilation-rate-rules`, `/invigilation-payment-document-draft`, `/invigilation-advance-batch-preview`, and `/payment-document-settings` remain configured and draft/supporting only. |
| Export and history | `/exports-center`, `/workflow`, `/external`, `/coexam`, and `/historical-schedules` remain configured. |

## Visual Smoke

The Phase B code path is confined to sidebar filtering. Build validation confirms the application compiles with all routes still registered. Browser/session role validation should be repeated with real seeded accounts before pilot signoff if a live QA environment is available.

## Safety Result

| Safety check | Result |
| ------------ | ------ |
| No irrelevant enterprise/dev pages in normal sidebar | PASS |
| Core workflow pages remain available | PASS |
| Hidden pages keep direct URL route declarations | PASS |
| Route guards unchanged | PASS |
| Historical Schedules remains visible where previously visible | PASS |
