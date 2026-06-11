# UI Full Route Template Inventory

**Date**: 2026-06-11  
**Registered declarations**: `50`  
**Visual destinations**: `43`  
**Redirect/routing-only declarations**: `7`

| Route | Component/state | Access/navigation | Decision |
|---|---|---|---|
| `/` | authenticated/public redirect | public routing | ACCEPTABLE |
| `/role-selection` | `RoleSelectionPage` | public, hidden | ACCEPTABLE |
| `/login` | `LoginPage` | public, hidden | ACCEPTABLE |
| `/student-search` | `StudentSearchPage` | public/student, hidden | ACCEPTABLE |
| `/dashboard` | `DashboardPage` | multi-role, nav | ACCEPTABLE |
| `/admin-intelligence-dashboard` | `AdminIntelligenceDashboard` | admin, nav | P2_POLISH |
| `/schedule` | `SchedulePage` | multi-role | ACCEPTABLE |
| `/analytics` | `ExecutiveAnalytics` | admin/reviewer roles | P2_POLISH |
| `/workload-duty-analytics` | `WorkloadDutyAnalytics` | admin | DEFER_WITH_REASON |
| `/duty-workload` | `WorkloadDutyAnalytics` | staff/reviewer roles | DEFER_WITH_REASON |
| `/my-workload` | `WorkloadDutyAnalytics` | teacher | DEFER_WITH_REASON |
| `/governance` | `GovernanceCockpitPage` | admin/reviewer roles | ACCEPTABLE |
| `/submissions` | `SubmissionsPage` | multi-role | P2_POLISH |
| `/attendance` | `RoomAttendancePage` | multi-role | P2_POLISH |
| `/checkins` | `CheckinsPage` | operations roles | P2_POLISH |
| `/swaps` | `SwapsV2Page` | operations roles | P2_POLISH |
| `/swaps-v2` | redirect to `/swaps` | routing-only | ACCEPTABLE |
| `/sections` | `SectionsPage` | multi-role | ACCEPTABLE |
| `/copy` | `CopyPage` | admin/staff | ACCEPTABLE |
| `/print-queue` | `PrintQueuePage` | print shop | ACCEPTABLE |
| `/workflow` | `WorkflowV2Page` | admin/reviewer roles | P2_POLISH |
| `/workflow-v2` | redirect to `/workflow` | routing-only | ACCEPTABLE |
| `/coexam` | `CoExamPage` | admin | ACCEPTABLE |
| `/optimizer` | `OptimizerPage` | admin | P2_POLISH |
| `/optimizer-trace` | `OptimizationTraceExplorerPage` | admin | P2_POLISH |
| `/staff-availability` | `StaffAvailabilityPage` | admin | ACCEPTABLE |
| `/printreview` | `PrintReviewPage` | admin/reviewer roles | P2_POLISH |
| `/external` | `ExternalPage` | admin/staff | P2_POLISH |
| `/exports-center` | `ExportCenterPage` | admin/staff | ACCEPTABLE |
| `/invigilation-advance-batch-preview` | `AdvanceInvigilationBatchPreview` | admin/staff | ACCEPTABLE |
| `/invigilation-rate-rules` | `InvigilationRateRules` | admin/staff | ACCEPTABLE |
| `/invigilation-payment-document-draft` | draft/review/export states | admin/staff | P1_FIX_NOW -> FIXED_PENDING_VALIDATION |
| `/payment-document-settings` | editable/read-only states | admin/reviewer/staff | P1_FIX_NOW -> FIXED_PENDING_VALIDATION |
| `/historical-schedules` | `HistoricalSchedulesPage` | admin | P2_POLISH |
| `/import` | `ImportV2Page` | admin | ACCEPTABLE |
| `/import-audit` | `ImportAuditPage` | admin | P2_POLISH |
| `/period` | `PeriodPage` | admin | P2_POLISH |
| `/settings` | `SettingsV2Page` | admin, hidden | ACCEPTABLE |
| `/settings-v2` | redirect to `/settings` | routing-only | ACCEPTABLE |
| `/platform-config` | `PlatformConfigurationPage` | admin | P1_FIX_NOW -> FIXED_PENDING_VALIDATION |
| `/operational-health` | `OperationalHealthPage` | admin/esq head | ACCEPTABLE |
| `/audit-explorer` | `AuditExplorerPage` | admin/esq head | ACCEPTABLE |
| `/rooms-v2` | `RoomManagementV2Page` | admin | P2_POLISH |
| `/venues-v2` | `VenueManagementV2Page` | admin, hidden | ACCEPTABLE |
| `/students-v2` | `StudentsV2Page` | admin, hidden | ACCEPTABLE |
| `/users` | `UsersV2Page` | admin, hidden | ACCEPTABLE |
| `/users-v2` | redirect to `/users` | routing-only | ACCEPTABLE |
| `/myexam` | `MyExamPage` | teacher | P2_POLISH |
| `/exammanager` | `ExamManagerPage` | admin/supervisor | P2_POLISH |
| `*` | authenticated not-found/public redirect | routing-only | ACCEPTABLE |

## Notes

- Draft export is a gated state of `/invigilation-payment-document-draft`, not a separate route.
- Workload routes are documented as `DEFER_WITH_REASON`; no workload code is changed in this pass.
- P2 items are usable routes with custom or legacy presentation that should be handled in later narrow passes.

