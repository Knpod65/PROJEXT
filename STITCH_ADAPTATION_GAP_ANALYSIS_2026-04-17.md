# Stitch Adaptation Gap Analysis (2026-04-17)

Purpose: compare the current `opt/ems_system` app with the `stitch_role_based_exam_platform` prototype library, then identify what should be preserved, redesigned, added, or split by role before adapting the UI into the existing PROJEXT/EMS codebase.

## Executive Summary

The current EMS app already has a usable domain foundation:
- Auth and role gating
- Dashboard data
- Schedule listing
- Submission messaging
- Swap response flow
- GPS check-ins
- Period management
- User list
- Co-exam, external exam, workflow, optimizer, exam manager, public student search

The main gap is not raw backend capability. The main gap is product structure and UI depth:
- The React app has about 20 routes, while the Stitch library represents many role-specific variants and operational subpages.
- The current frontend uses one generic shell for almost every role.
- Many advanced admin, supervisor, and ESQ pages from Stitch do not exist yet as React routes.
- Some sections exist in backend APIs but only have a thin frontend wrapper.

Recommendation:
- Preserve the current EMS data model, permissions, and API relationships.
- Replace the current generic shell and generic page variants with role-aware UI templates inspired by Stitch.
- Do not copy all 175 Stitch HTML screens literally.
- Instead, extract 8-10 canonical page families and map the prototypes into those families.

## Important Findings From Current Code

### Keep As Core System Logic
- `frontend/src/App.tsx` already provides protected routing and role gating.
- `frontend/src/store/auth.store.tsx` already supports login, logout, refresh, and admin `view-as`.
- Backend routers already expose useful operational endpoints for submissions, swaps, workflow, external exams, users, periods, imports, and exports.
- The existing app is a better source of truth for data relationships than the Stitch HTML files.

### Immediate Gaps
- Teacher does not currently have access to `/dashboard`, even though the Stitch target model expects a teacher dashboard.
- There is no dedicated React route for `Room Attendance`.
- Supervisor target pages are only partially represented.
- ESQ navigation in the real app is completely different from the approved 2-item Stitch target.
- Admin-specific oversight sections are mostly absent from the React app.
- `secretary` exists in the real role model but is not part of the current Stitch target matrix, so this needs a product decision.

### Low-Risk Fix Applied
- `frontend/src/pages/Schedule.tsx`
  - Fixed export buttons to use the actual backend routes:
  - Excel: `/api/exports/schedule-excel`
  - PDF: `/api/exports/schedule`

## Preserve vs Redesign

### Preserve
- Backend models and routers in `backend/routers/*`
- Existing permission model in `frontend/src/utils/roles.ts`
- Auth/session flow
- Period context
- Submission, swap, and check-in business rules
- Public student search logic
- Existing service layer in `frontend/src/services/*`

### Redesign
- Sidebar, topbar, and mobile navigation
- Role-specific entry points
- Page density, hierarchy, and information grouping
- Dashboard composition per role
- Schedule visualization
- Submission workflow UI
- Attendance/check-in reporting surfaces
- Admin oversight and reporting pages

## Section-By-Section Review

## 1. App Shell And Navigation

Current EMS status:
- One generic sidebar and one generic topbar for almost all authenticated users.
- Navigation is driven by `frontend/src/config/navigation.ts`.
- Mobile navigation only exposes 5 generic keys.

Best Stitch references:
- `admin_dashboard_refined_oversight`
- `admin_master_exam_schedule_enhanced_oversight`
- `teacher_submissions_refactored`
- `staff_dashboard_refactored`
- `dept_supervisor_dashboard`

What is missing:
- Role-specific navigation models.
- Grouped admin navigation matching the approved 27-item target.
- Simplified 2-item ESQ shell.
- Supervisor-specific 9-item shell.
- Role-specific search, notifications, quick actions, and page context.
- Better active-state hierarchy and sidebar scrolling/grouping.

Recommendation:
- Build one config-driven shell per role family: `admin`, `teacher`, `staff`, `dept_supervisor`, `esq`.
- Use Stitch as the visual reference, but keep route ownership in React.

## 2. Login And Role Entry

Current EMS status:
- One generic login page with username/password and CMU SSO.
- No role-selection landing between login and destination.

Best Stitch references:
- `admin_login`
- `staff_login`
- `supervisor_login`
- `esq_authority_login`
- `ems_mandatory_role_selection`
- `role_selection_1`
- `role_selection_2`

What is missing:
- Standardized role-branded login variants.
- Password visibility toggle.
- Optional remember-me behavior.
- Unified "secure portal access" structure from the UI spec.
- Dedicated role selection or role-switch landing experience.

Recommendation:
- Keep the current auth logic.
- Redesign only the login presentation and entry selection flow.

## 3. Dashboard

Current EMS status:
- `frontend/src/pages/Dashboard.tsx` shows stats, admin-only analytics charts, and recent logs.
- Dashboard route is available to admin, ESQ, secretary, supervisor, and staff.
- Teacher has no dashboard route.

Best Stitch references:
- `admin_dashboard_refined_oversight`
- `admin_dashboard_personnel_oversight`
- `staff_dashboard_refactored`
- `teacher_dashboard_refactored`
- `dept_supervisor_dashboard`
- `esq_governance_dashboard`

What is missing:
- Teacher dashboard entirely.
- Role-specific cards and summaries.
- Upcoming sessions table/grid.
- Alert panel and operational feed.
- Quick actions tied to each role.
- Visual separation between oversight metrics and execution tasks.

Recommendation:
- Split the current dashboard into role-aware variants instead of one shared layout.

## 4. Schedule / Master Schedule

Current EMS status:
- `frontend/src/pages/Schedule.tsx` is a grouped list view with room/status filters and exports.
- Strong enough as a data baseline, but visually and functionally thin.

Best Stitch references:
- `admin_master_exam_schedule_enhanced_oversight`
- `admin_exam_schedule_calendar`
- `admin_master_schedule_calendar_grid`
- `teacher_exam_schedule_personalized_view`
- `teacher_exam_schedule_calendar_view`
- `staff_exam_schedule_refactored`
- `dept_supervisor_master_exam_schedule_refined`

What is missing:
- Calendar view.
- Timeline/grid toggle.
- Conflict alerts and density indicators.
- Room/venue utilization overlays.
- Invigilator/staff assignment controls.
- Personalized schedule view for teacher/staff.
- Department or branch schedule variants.
- Drill-down session detail drawer/panel.

Recommendation:
- Turn the current schedule page into a shared data source with multiple role-specific visual modes.

## 5. Submissions

Current EMS status:
- `frontend/src/pages/Submissions.tsx` supports status tabs and message threads.
- No upload form, no version history UI, no release/approval surface.

Best Stitch references:
- `teacher_submissions_refactored`
- `teacher_submissions_refactored_consistency`
- `teacher_submissions_advanced_configuration_1`
- `teacher_submissions_advanced_configuration_2`
- `teacher_submissions_advanced_file_ocr_config`
- `admin_submissions_oversight_branch_degree_level`
- `supervisor_submission_oversight`

What is missing:
- New submission creation flow.
- File upload and print specification steps.
- Review/approve/reject flow UI.
- Version history and rollback UI.
- OCR/equipment/material options.
- Bulk admin/supervisor oversight view.
- Rich filtering, sorting, and submission analytics.

Important backend note:
- `backend/routers/submissions.py` already exposes much more than the current UI uses.

Recommendation:
- This is one of the best candidates for "preserve backend, rebuild frontend."

## 6. Swaps

Current EMS status:
- `frontend/src/pages/Swaps.tsx` supports waiting/mine/all and approve/reject/cancel.
- `createSwap()` exists in the service layer but is not surfaced in the UI.

Best Stitch references:
- `teacher_swap_management`
- `staff_swap_requests_resolution`
- `dept_supervisor_swap_management_refined`
- `admin_swap_management_system_wide`
- `admin_swap_analytics_dashboard`
- `admin_swap_oversight_conflict_focus`

What is missing:
- Create swap request flow.
- Available-user picker.
- Conflict-first admin oversight.
- Analytics and operational summaries.
- Emergency substitute UI.
- Baseline lock indicators and workflow status context.

Important backend note:
- `backend/routers/swaps_v2.py` already supports available users, create/respond/cancel, emergency sub, and admin lock-baseline.

## 7. Room Attendance

Current EMS status:
- There is no dedicated `Room Attendance` route in the React app.
- Attendance concepts are split between `Checkins.tsx` and some reporting concepts that do not yet exist in UI.

Best Stitch references:
- `teacher_room_check_in_attendance_report`
- `teacher_check_in_attendance_report`
- `staff_room_overview_standardized`
- `staff_room_check_in_management`
- `dept_supervisor_attendance_report`
- `admin_comprehensive_attendance_report`
- `admin_attendance_anomaly_report`
- `admin_attendance_audit_log`

What is missing:
- Dedicated route.
- Room-level attendance records.
- Attendance variance and anomaly views.
- Aggregate and room-level reports.
- Audit and correction workflow.
- Role-specific attendance perspectives.

Recommendation:
- This should become a first-class navigation item before trying to fully match the Stitch menu matrix.

## 8. Check-Ins

Current EMS status:
- `frontend/src/pages/Checkins.tsx` supports today-only schedules, GPS capture, notes, and event history.
- Good baseline but limited operational visibility.

Best Stitch references:
- `admin_check_in_feed_operational`
- `admin_check_in_feed_time_locked`
- `admin_visual_oversight_check_in_feed_refined`
- `admin_time_locked_check_in_feed_visual_oversight`
- `staff_check_ins_enhanced_monitoring`
- `teacher_time_locked_check_in_feed`
- `dept_supervisor_check_in_feed`

What is missing:
- Global feed view.
- Time-locked operational view.
- Dual confirmation UI.
- Branch/faculty filtering.
- Live anomaly indicators.
- Absent/late breakdown.
- Role-specific operational summaries.

Important backend note:
- `confirmCheckin()` exists in `frontend/src/services/checkin.service.ts` but is not used by the UI.

## 9. Public Student Search

Current EMS status:
- `frontend/src/pages/StudentSearch.tsx` is functional and already role-safe.

Best Stitch references:
- `public_student_search`
- `public_student_search_with_result_modal_1`
- `public_student_search_with_result_modal_2`

What is missing:
- Richer result presentation.
- Modal or expandable detail pattern.
- Empty-state guidance and search history affordances.
- Better public landing integration and visual polish.

Recommendation:
- Low functional risk, high UX upside.

## 10. Users, Settings, Period, Import

Current EMS status:
- `Users.tsx` is list + deactivate only.
- `Settings.tsx` is raw key/value editing.
- `Period.tsx` is create/activate only.
- `Import.tsx` is history only.

Best Stitch references:
- `admin_user_management_excel_import`
- `admin_user_management_personnel_assignment`
- `admin_settings_term_management`
- `admin_settings_view_as_mode`
- `admin_settings_view_as_mode_with_exit`
- `admin_student_management_excel_first_enrollment`

What is missing:
- User create/edit/import UI.
- Role/personnel assignment UI.
- Grouped settings pages.
- Term management UX.
- View-as switcher UX.
- Import upload wizard.
- Import summary and validation issue review.

Important backend note:
- The backend already supports more actions than the UI exposes in users, period, and import domains.

## 11. Course / Section / Room / Venue Management

Current EMS status:
- `Sections.tsx` is a basic table.
- There is no dedicated course management, room management, venue allocation, or room availability UI.

Best Stitch references:
- `admin_course_management_with_edit_actions`
- `admin_course_management_refined`
- `admin_room_availability_management`
- `admin_room_management`
- `admin_venue_allocation_matrix`
- `admin_venue_allocation_final_confirmation`
- `admin_venue_staff_allocation_matrix_1`
- `admin_venue_staff_allocation_matrix_2`
- `admin_venue_utilization_schedule`
- `admin_manual_subject_assignment`

What is missing:
- Course CRUD experience.
- Room CRUD and availability controls.
- Venue utilization and allocation matrix.
- Manual assignment workflows.
- Final confirmation UI for venue/staff allocation.

Recommendation:
- This is a large admin-only cluster and should be built as a grouped area, not as unrelated pages.

## 12. Workflow / Optimizer / Exam Manager / Co-Exam / External

Current EMS status:
- `Workflow.tsx` is functional but minimal.
- `Optimizer.tsx` is functional but minimal.
- `ExamManager.tsx` and `MyExam.tsx` are summary-only.
- `CoExam.tsx` is list + auto-detect only.
- `External.tsx` is list-only.
- `PrintReview.tsx` is still a placeholder.

Best Stitch references:
- `admin_optimization_dashboard`
- `admin_optimization_dashboard_calendar_view_1`
- `admin_optimization_dashboard_calendar_view_2`
- `admin_optimization_dashboard_calendar_view_3`
- `admin_operations_command_dashboard`
- `faculty_exam_printing_oversight`
- `admin_printing_shop_management`
- `print_shop_queue_dashboard_refined`

What is missing:
- Constraint editing and scenario comparison.
- Suggestion review.
- Room unavailability and staff pool controls.
- Material and printing management.
- PDF preview/batch print workflow.
- External exam create/edit/assign flows.
- Exam manager proposal/confirm/reassign UI.
- Co-exam member editing and conflict review.

Important backend note:
- Workflow, exam manager, external exam, and documents APIs already expose more capability than the UI currently surfaces.

## 13. Reporting, Audit, Finance, Logistics, System Health

Current EMS status:
- These areas are mostly absent from the React app as standalone pages.

Best Stitch references:
- `admin_audit_logs_statistics`
- `admin_audit_compliance_dashboard`
- `admin_system_health`
- `admin_financial_oversight_payouts`
- `admin_logistics_control_center`
- `admin_material_logistics_feed`
- `admin_printing_cost_management`
- `admin_subject_cost_analysis_withdrawal_report`
- `esq_logistics_cost_approval`
- `esq_financial_personnel_master_oversight`

What is missing:
- Audit log UI.
- Compliance dashboard UI.
- System health UI.
- Finance and payout UI.
- Logistics control center UI.
- ESQ oversight surfaces.

Important backend note:
- Audit/export/workflow/scheduler endpoints exist, but the oversight UI layer is still largely missing.

## Role Coverage Summary

### Admin
- Current status: partial foundation only.
- Missing most of the approved 27-item navigation model.
- Biggest opportunity for Stitch-driven redesign.

### Teacher
- Current status: has schedule, submissions, swaps, check-ins, my exam.
- Missing dashboard and room attendance route.
- Submission UX is far behind Stitch.

### Staff
- Current status: workable for dashboard, schedule, swaps, check-ins.
- Missing room attendance as a true section.
- Current UI still feels generic and not operational enough.

### Dept Supervisor
- Current status: can reach some shared pages but lacks the dedicated oversight surface expected by Stitch.
- Missing branch audit logs, faculty data management, supervisor reports, and submission oversight as explicit pages.

### ESQ
- Current status: route model does not match the approved 2-item target.
- Needs a dedicated shell and dedicated pages, not reuse of generic schedule/submissions pages.

## Recommended Build Order

1. Lock the canonical role navigation model in React, not in prototype HTML.
2. Add the missing `Room Attendance` route and define its data contract.
3. Split dashboard into role-specific variants.
4. Rebuild `Submissions` around the richer backend endpoints.
5. Expand `Schedule` into list + calendar + timeline modes.
6. Expand `Swaps` to include creation, oversight, and analytics.
7. Build admin-only management clusters:
   - users/settings/period/import
   - course/room/venue
   - logistics/printing
   - audit/system health/finance
8. Build the ESQ 2-page shell and supervisor 9-item shell.

## Suggested Canonical Page Families

Instead of porting every Stitch HTML file one-by-one, consolidate them into reusable React families:

- Shell page family
- Dashboard page family
- Schedule page family
- Submission page family
- Swap page family
- Attendance/check-in page family
- Data management page family
- Oversight/reporting page family
- Settings/login/public entry page family

## Validation Notes

- Frontend build could not be executed in this environment because `node`/`npm` are not installed in the current shell.
- The repository has unrelated existing changes in `opt/ems_system` that were not modified as part of this audit.
