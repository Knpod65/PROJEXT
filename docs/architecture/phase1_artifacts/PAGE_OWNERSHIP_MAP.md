# Page Ownership Map
## Phase 1 Concrete Artifact

Source of truth:
- docs/architecture/EMS_ARCHITECTURE_MAP.md (Page-to-Router Correspondence)
- docs/architecture/UI_SYSTEM_AND_ROLE_THEME_GUIDE.md

This map assigns frontend pages to backend ownership and expected authorization surface.

| Frontend Page | Backend Router(s) | Domain Owner | Primary Access Roles (Current) | Notes |
|---|---|---|---|---|
| Dashboard.tsx | backend/routers/dashboard.py | Staff Operations | admin, dept_supervisor, staff, teacher | Operational summary surface |
| Schedule.tsx | backend/routers/schedule.py | Exam Scheduling | admin, dept_supervisor, staff, teacher | Scheduling read/write split |
| Optimizer.tsx | backend/routers/optimize_workflow.py | Staff Operations | admin | Session initialization and orchestration |
| WorkflowV2.tsx | backend/routers/optimize_workflow.py | Staff Operations | admin, esq_head, secretary | Sign workflow path |
| SwapsV2.tsx | backend/routers/swaps_v2.py | Staff Operations | admin, staff, teacher | Swap window constrained |
| Checkins.tsx | backend/routers/checkins.py | Staff Operations | admin, dept_supervisor, staff, teacher | Pickup management is stricter subset |
| Submissions.tsx | backend/routers/submissions.py | Submission and Approval | admin, esq_head, secretary, dept_supervisor, teacher | Teacher ownership plus governance review |
| ExamManager.tsx | backend/routers/exam_manager.py | Submission and Approval | admin | Ownership reassignment |
| ImportV2.tsx | backend/routers/imports_v2.py | Academic Data | admin | High-impact mutation workflow |
| ExportCenter.tsx | backend/routers/exports.py, backend/routers/exports_excel.py | Export Center | admin, staff, esq_head, secretary (endpoint-specific) | Endpoint-level role differences |
| Period.tsx | backend/routers/period.py | Term Lifecycle | admin | Lifecycle transition control |
| SettingsV2.tsx | backend/routers/settings.py | Term Lifecycle | admin | Configuration governance |
| UsersV2.tsx | backend/routers/users.py | Identity and Auth | admin | User governance surface |

## Implementation Notes

1. Page-level route gating belongs in App route definitions via GuardedPage.
2. Feature-level gating inside pages should move to semantic permission checks.
3. Role matrix changes must update this map and ROLE_PERMISSION_MATRIX.md together.
