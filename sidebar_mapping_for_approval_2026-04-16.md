# Sidebar Mapping For Approval (2026-04-16)

Purpose: page-by-page mapping for 5 roles showing what is missing, extra, or should be renamed before full rollout.

## Target Menus

### Staff
- Dashboard
- Exam Schedule
- Swap Requests
- Room Attendance
- Check-ins

### Teacher
- Submission
- Dashboard
- Exam Schedule
- Swap Requests
- Room Attendance
- Check-ins

### Supervisor
- Branch Audit Logs
- Dashboard
- Exam Schedule
- Swap Requests
- Room Attendance
- Check-ins
- Faculty Data Management
- Dept Supervisor Reports
- Supervisor Submission Oversight

### ESQ
- ESQ Logistics & Cost Approval
- ESQ Financial & Personnel Master Oversight

### Admin
- Dashboard
- Exam Schedule
- Swap Requests
- Room Attendance
- Check-ins
- Admin Audit Logs & Statistics
- Admin System Health
- Admin User Management (Excel Import)
- Admin Check-in Feed (Operational)
- Admin Student Management (Excel-First Enrollment)
- Admin Submissions Oversight (Branch & Degree Level)
- Admin Logistics Control Center
- Faculty Exam Printing Oversight
- Admin Course Management (with Edit Actions)
- Admin Room Availability & Management
- Admin Financial Oversight & Payouts
- Admin Comprehensive Attendance Report
- Admin Operations Command Dashboard
- Admin Optimization Dashboard (Calendar View)
- Admin Manual Subject Assignment
- Admin Venue & Staff Allocation Matrix
- Admin Settings (Term Management)
- Admin Check-in Feed (Time-Locked)
- Admin Swap Analytics Dashboard
- Admin Attendance Anomaly Report
- Admin Attendance Audit Log
- Admin Audit & Compliance Dashboard

## Teacher Mapping

### Updated in this pass
1. stitch_role_based_exam_platform/teacher_dashboard/code.html
- Before: Dashboard, Submissions, Exam Schedule
- After: Dashboard, Submissions, Exam Schedule, Swap Requests, Room Attendance, Check-ins
- Action: Added missing 3 items
- Low-risk removed: language toggle + header settings icon

2. stitch_role_based_exam_platform/teacher_exam_schedule/code.html
- Before: Dashboard, Submissions, Exam Schedule
- After: Dashboard, Submissions, Exam Schedule, Swap Requests, Room Attendance, Check-ins
- Action: Added missing 3 items

3. stitch_role_based_exam_platform/teacher_swap_management/code.html
- Before: Dashboard, Submissions, Exam Schedule, Check-ins
- After: Dashboard, Submissions, Exam Schedule, Swap Requests, Room Attendance, Check-ins
- Action: Added Swap Requests + Room Attendance and normalized labels
- Low-risk removed: Start Exam CTA (non-core/ambiguous utility)

4. stitch_role_based_exam_platform/teacher_attendance_report/code.html
- Before: Dashboard, Submissions, Exam Schedule, Check-ins
- After: Dashboard, Submissions, Exam Schedule, Swap Requests, Room Attendance, Check-ins
- Action: Added missing 2 items and set Room Attendance as active

5. stitch_role_based_exam_platform/teacher_check_in_feed_1/code.html
- Before: Dashboard, Check-ins, Exam Schedule
- After: Dashboard, Submissions, Exam Schedule, Swap Requests, Room Attendance, Check-ins
- Action: Added missing 3 items
- Low-risk removed: language icon in topbar

### Remaining teacher variants not yet normalized (approval needed)
- teacher_dashboard_refactored
- teacher_exam_schedule_calendar_view
- teacher_exam_schedule_personalized_view
- teacher_exam_schedule_staff_assignments
- teacher_check_in_feed_2
- teacher_time_locked_check_in_feed
- teacher_attendance_report_refined
- teacher_room_check_in_attendance_report
- teacher_check_in_attendance_report
- all teacher_submissions_* variants

## Staff Mapping

### Updated in this pass
1. stitch_role_based_exam_platform/staff_dashboard_refactored/code.html
- Before: Dashboard, Exam Schedule, Venue Logistics, Attendance, Swaps, Check-ins
- After: Dashboard, Exam Schedule, Swap Requests, Room Attendance, Check-ins
- Action: Removed Venue Logistics, renamed Swaps, renamed Attendance
- Low-risk removed: TH/EN text toggle in header

2. stitch_role_based_exam_platform/staff_exam_schedule_refactored/code.html
- Before: Dashboard, Schedule, Submissions, Swaps, Check-ins
- After: Dashboard, Exam Schedule, Swap Requests, Room Attendance, Check-ins
- Action: Renamed Schedule/Swaps and replaced Submissions with Room Attendance
- Low-risk removed: language icon in header

3. stitch_role_based_exam_platform/staff_swap_requests_resolution/code.html
- Before: Dashboard, Schedule, Submissions, Swaps, Check-ins, Student Search
- After: Dashboard, Exam Schedule, Swap Requests, Room Attendance, Check-ins
- Action: Removed Submissions + Student Search; renamed labels
- Low-risk removed: header settings icon

4. stitch_role_based_exam_platform/staff_attendance_report/code.html
- Before: Dashboard, Exam Schedule, Check-ins, Venue Logistics, Swaps, Attendance
- After: Dashboard, Exam Schedule, Swap Requests, Room Attendance, Check-ins
- Action: Removed Venue Logistics, renamed Swaps, renamed Attendance
- Low-risk removed: language icon in header

5. stitch_role_based_exam_platform/staff_check_ins/code.html
- Before: Dashboard, Schedule, Submissions, Swaps, Check-ins, Student Search
- After: Dashboard, Exam Schedule, Swap Requests, Room Attendance, Check-ins
- Action: Removed Submissions + Student Search; normalized labels
- Low-risk removed: EN/TH toggle and header settings icon

### Remaining staff variants not yet normalized (approval needed)
- staff_dashboard_room_overview
- staff_review_dashboard*
- staff_exam_schedule_1
- staff_exam_schedule_2
- staff_swap_requests_1
- staff_swap_requests_2
- staff_swap_management_refactored
- staff_swaps_refactored
- staff_swaps_standardized
- staff_room_overview*
- staff_room_check_in_management
- staff_check_ins_* variants
- staff_time_locked_check_in_feed
- staff_venue_* variants
- staff_operational_statistics*
- staff_schedule_logistics

## Supervisor Mapping (for approval before patch)

Representative pages checked:
- dept_supervisor_dashboard
- dept_supervisor_branch_audit_logs
- dept_supervisor_reports
- dept_supervisor_schedule
- dept_supervisor_swap_management
- dept_supervisor_attendance_report
- dept_supervisor_check_in_feed
- dept_supervisor_submissions_tracking

### Missing
- Faculty Data Management (no dedicated dept_supervisor menu item)
- Supervisor Submission Oversight label consistency is not unified
- Room Attendance naming is inconsistent across pages

### Extra/Fragmented
- Student Search appears in some supervisor sidebars but not target list
- Settings/Logout blocks vary by page
- Multiple alternate menu architectures across supervisor pages

### Rename candidates
- Schedule -> Exam Schedule
- Swaps -> Swap Requests
- Attendance -> Room Attendance

## ESQ Mapping (for approval before patch)

Representative pages checked:
- esq_governance_dashboard
- esq_logistics_cost_approval
- esq_financial_personnel_master_oversight

### Gap
- Current ESQ sidebars are governance-style multi-menu.
- Target requires only 2 explicit menu entries:
  - ESQ Logistics & Cost Approval
  - ESQ Financial & Personnel Master Oversight

### Decision needed
- Confirm hard simplification to 2-item sidebar for all ESQ pages.

## Admin Mapping (for approval before patch)

Representative pages checked:
- admin_dashboard
- admin_audit_logs_statistics
- admin_submissions_oversight_branch_degree_level
- admin_exam_schedule_calendar
- admin_check_in_feed_operational
- admin_attendance_report_room_level_1

### Gap
- Admin currently has multiple sidebar architectures.
- Target requires one unified 27-item menu model (as listed above).

### Missing/fragmented behavior
- Many target entries exist as pages but are not consistently present in each sidebar.
- Label conventions differ by page (Schedule vs Exam Schedule, Swaps vs Swap Requests, Attendance variants).

### Decision needed
- Confirm single canonical admin sidebar order and whether sidebar should support scroll + section grouping.

## Low-Risk Button Cleanup Applied in this pass

### Removed
- Header language toggles in selected Teacher/Staff core pages
- Header settings icon where duplicate shell-level action existed

### Kept intentionally
- Notifications
- Primary flow actions in page body (Filter, Export, Submit/Approve/Reject)

## Approval Checklist

1. Approve Teacher/Staff changes as baseline for remaining variants.
2. Approve Supervisor canonical sidebar order (9 items).
3. Approve ESQ simplification to exactly 2 sidebar entries.
4. Approve Admin canonical 27-item menu with section grouping.
5. Approve whether Settings/Logout remain in footer area outside core menu list.
