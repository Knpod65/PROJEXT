# EMS UI Consolidation Route Matrix

**Date**: 2026-06-15  
**Registered declarations**: 50  
**Visual destinations**: 43

| Batch | Routes | Final classification |
|---|---|---|
| Routing/system | `/`, `*`, redirects: `/swaps-v2`, `/workflow-v2`, `/settings-v2`, `/users-v2` | `ALREADY_CANONICAL`; routing behavior unchanged |
| Auth/public | `/role-selection`, `/login`, `/student-search` | `ALIGNED_BY_SHARED_SYSTEM_STATE`; authenticated redirects and public state audited |
| Dashboards | `/dashboard`, `/admin-intelligence-dashboard`, `/analytics` | `RENOVATED_AND_VALIDATED` |
| Workload analytics | `/workload-duty-analytics`, `/duty-workload`, `/my-workload` | `REMEDIATED_AND_FIXED_VIEWPORT_VALIDATED`; shared page composition repaired without changing workload calculations |
| Cognitive load | `/checkins`, `/myexam`, `/optimizer`, `/workflow`, `/import` | `RENOVATED_OR_ALREADY_CANONICAL`; actions unchanged |
| Core operations | `/schedule`, `/submissions`, `/attendance`, `/swaps`, `/sections`, `/copy`, `/print-queue`, `/coexam`, `/staff-availability`, `/printreview`, `/external`, `/period`, `/rooms-v2`, `/venues-v2`, `/students-v2`, `/users`, `/exammanager` | `ALIGNED_AND_VALIDATED` |
| Governance/intelligence | `/governance`, `/audit-explorer`, `/operational-health`, `/optimizer-trace`, `/platform-config`, `/historical-schedules`, `/import-audit`, `/exports-center`, `/settings` | `/optimizer-trace` is `REMEDIATED_AND_FIXED_VIEWPORT_VALIDATED`; other classifications are unchanged |
| Payment/document | `/invigilation-advance-batch-preview`, `/invigilation-rate-rules`, `/invigilation-payment-document-draft`, `/payment-document-settings` | `ALIGNED_AND_VALIDATED`; draft-only gates unchanged |

## Legacy Not Routed

`Import.tsx`, `Settings.tsx`, `Swaps.tsx`, `Users.tsx`, and `Workflow.tsx` are superseded by active V2 routes and are `LEGACY_NOT_ROUTED`. `RoleDashboard.tsx` remains a shared/legacy page implementation and is not directly routed.

## Validation Columns

During each route batch, record before evidence, after evidence, role access, Thai/English result, desktop/narrow result, overflow, raw-key/enum result, focus result, and final validation status in the batch validation log. Existing atlas images may be used as before evidence only when still representative.

## Previous Final Route Audit Invalidated

The previous 43-route audit and its claims of zero raw i18n keys, zero overflow findings, and completed visual consolidation are invalidated by the authenticated 2026-06-15 remediation diagnosis. Current source and computed DOM reproduce raw-key, duplicated-heading, inert-grid, and page-composition failures on Optimization Trace and Workload Analytics.

Route rendering and HTTP success remain useful smoke evidence, but they are not visual acceptance evidence. Corrected route classifications and after evidence will be recorded by the visual consolidation remediation pass.

See `UI_VISUAL_CONSOLIDATION_FAILURE_DIAGNOSIS.md`.

The remediation pass validated the two diagnosed target surfaces and their confirmed shared causes. It does not reinstate a blanket claim that all 43 visual destinations are visually complete.
