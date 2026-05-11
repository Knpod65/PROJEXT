# Route Ownership Map
## Phase 1 Concrete Artifact

Source of truth:
- docs/architecture/EMS_ARCHITECTURE_MAP.md
- docs/architecture/DOMAIN_BOUNDARY_MAP.md

This map assigns each API route group to a bounded context owner.

| Domain Owner | Router File | Prefix | Primary Business Responsibility | Notes |
|---|---|---|---|---|
| Identity and Auth | backend/routers/auth.py | /api/auth | Login, logout, session, role selection | Includes view-as behavior |
| Identity and Auth | backend/cmu_sso.py | /api/auth/sso | CMU SSO token exchange and callback | External identity sidecar |
| Identity and Auth | backend/routers/users.py | /api/users | User CRUD and teacher catalog | Admin-governed |
| Term Lifecycle | backend/routers/period.py | /api/period | Exam period lifecycle transitions | Lock and archive boundaries |
| Term Lifecycle | backend/routers/settings.py | /api/settings | Operational deadlines and policy flags | Includes retention controls |
| Term Lifecycle | backend/routers/scheduler.py | /api/scheduler | Internal timed jobs and maintenance triggers | Operational entrypoint |
| Academic Data | backend/routers/courses.py | /api/courses | Course and section management | Imports and section ownership adjacency |
| Academic Data | backend/routers/imports_v2.py | /api/import/v2 | Canonical import pipeline | Parse, validate, normalize, commit |
| Academic Data | backend/routers/imports.py | /api/import | Legacy import endpoints | Migration/deprecation path |
| Exam Scheduling | backend/routers/schedule.py | /api/schedule | Exam date/time/room assignments | High complexity hotspot |
| Exam Scheduling | backend/routers/co_exam.py | /api/co-exam | Co-exam grouping and member linkage | Cross-section coordination |
| Exam Scheduling | backend/routers/external_exams.py | /api/external | External exam schedule and assignment | Separate path from core schedule |
| Submission and Approval | backend/routers/submissions.py | /api/submissions | Teacher submission wizard and approval state | Status machine dependent |
| Submission and Approval | backend/routers/exam_manager.py | /api/exam-manager | Section exam ownership assignment | Ownership governance |
| Submission and Approval | backend/routers/documents.py | /api/documents | Exam document generation and previews | Document pipeline |
| Staff Operations | backend/routers/optimize_workflow.py | /api/workflow | Optimization sessions and signer workflow | Contains signer-order coupling |
| Staff Operations | backend/routers/swaps_v2.py | /api/swaps2 | Swap request lifecycle | Depends on workflow state |
| Staff Operations | backend/routers/checkins.py | /api/checkins | Attendance and pickup check-ins | Object-level auth gap tracked |
| Staff Operations | backend/routers/dashboard.py | /api/dashboard | Operations dashboards and analytics endpoints | Will expand in Phase 5 |
| Print Queue | backend/routers/printing.py | /api/printing | Print queue lifecycle | print_shop role core surface |
| Export Center | backend/routers/exports.py | /api/exports | PDF export endpoints | Contains period resolver duplication |
| Export Center | backend/routers/exports_excel.py | /api/exports | Excel export endpoints | Same prefix as exports router |
| Export Center | backend/routers/pdf.py | /api/pdf | Tokenized PDF access | Print security path |
| Public and Historical | backend/routers/public.py | /api/public | Public student-facing schedule lookup | Unauthenticated constrained read |
| Public and Historical | backend/routers/historical_schedules.py | /api/historical-schedules | Historical schedule analytics | Write-once archive domain |

## Ownership Rules

1. New route handlers must be added under the owning domain router above.
2. Cross-domain logic should be delegated through shared services/utilities, not copied.
3. A route changing ownership must update this file and DOMAIN_BOUNDARY_MAP.md in the same PR.
