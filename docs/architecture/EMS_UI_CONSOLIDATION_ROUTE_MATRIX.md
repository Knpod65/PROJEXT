# EMS UI Consolidation Route Matrix

**Date**: 2026-06-15  
**Registered declarations**: 50  
**Visual destinations**: 43

| Batch | Routes | Baseline decision |
|---|---|---|
| Routing/system | `/`, `*`, redirects: `/swaps-v2`, `/workflow-v2`, `/settings-v2`, `/users-v2` | `ALREADY_CANONICAL` routing-only |
| Auth/public | `/role-selection`, `/login`, `/student-search` | `NEEDS_COMPONENT_MIGRATION` |
| Dashboards | `/dashboard`, `/admin-intelligence-dashboard`, `/analytics` | `NEEDS_ROLE_THEME_ALIGNMENT` |
| Workload audit only | `/workload-duty-analytics`, `/duty-workload`, `/my-workload` | `DEFERRED_WITH_REASON`; validate, do not modify |
| Cognitive load | `/checkins`, `/myexam`, `/optimizer`, `/workflow`, `/import` | `NEEDS_COGNITIVE_LOAD_REDUCTION` |
| Core operations | `/schedule`, `/submissions`, `/attendance`, `/swaps`, `/sections`, `/copy`, `/print-queue`, `/coexam`, `/staff-availability`, `/printreview`, `/external`, `/period`, `/rooms-v2`, `/venues-v2`, `/students-v2`, `/users`, `/exammanager` | `NEEDS_COMPONENT_MIGRATION` or `NEEDS_I18N_CLEANUP` |
| Governance/intelligence | `/governance`, `/audit-explorer`, `/operational-health`, `/optimizer-trace`, `/platform-config`, `/historical-schedules`, `/import-audit`, `/exports-center`, `/settings` | `NEEDS_I18N_CLEANUP` or `NEEDS_COMPONENT_MIGRATION` |
| Payment/document | `/invigilation-advance-batch-preview`, `/invigilation-rate-rules`, `/invigilation-payment-document-draft`, `/payment-document-settings` | `NEEDS_COMPONENT_MIGRATION`; preserve all safety gates |

## Legacy Not Routed

`Import.tsx`, `Settings.tsx`, `Swaps.tsx`, `Users.tsx`, and `Workflow.tsx` are superseded by active V2 routes and are `LEGACY_NOT_ROUTED`. `RoleDashboard.tsx` remains a shared/legacy page implementation and is not directly routed.

## Validation Columns

During each route batch, record before evidence, after evidence, role access, Thai/English result, desktop/narrow result, overflow, raw-key/enum result, focus result, and final validation status in the batch validation log. Existing atlas images may be used as before evidence only when still representative.

