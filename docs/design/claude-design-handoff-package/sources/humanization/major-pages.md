# Screenshot Atlas: Major Pages

## Purpose

This file turns the first live screenshot pass into a working atlas.

Each section points to a real EMS screen capture, tells the reader what to notice first, and explains what the page means operationally.

## Role Selection

Screenshot:
![Role Selection](images/admin/role-selection-viewport.png)

Full page:
[role-selection-full.png](images/admin/role-selection-full.png)

Responsive variants:
[role-selection-tablet.png](images/admin/role-selection-tablet.png) · [role-selection-mobile.png](images/admin/role-selection-mobile.png)

Route:
`/role-selection`

Role:
Public entry

Look here first:
The workspace cards and the `Continue to sign in` button.

What matters operationally:
This screen prevents users from entering the wrong workspace before authentication.

Advanced or optional:
`Public Student Search` is the only non-authenticated path in the entry shell.

Common confusion:
Users often think role switching happens after sign-in. In EMS, workspace intent is declared first.

Callouts:
1. Role/workspace cards
2. EMS role validation note
3. Continue button
4. Public Student Search

## Login

Screenshot:
![Login](images/admin/login-viewport.png)

Full page:
[login-full.png](images/admin/login-full.png)

Responsive variants:
[login-tablet.png](images/admin/login-tablet.png) · [login-mobile.png](images/admin/login-mobile.png)

Route:
`/login`

Role:
Any authenticated role after workspace selection

Look here first:
The selected workspace banner and the username/password form.

What matters operationally:
This page confirms the chosen workspace and binds the authenticated session to the matching operational role.

Advanced or optional:
`Change role` returns the user to the role-selection step without leaving the entry flow.

Common confusion:
If the wrong workspace is selected, valid credentials can still fail with a workspace-assignment error.

Callouts:
1. Selected workspace summary
2. Username field
3. Password field
4. Change role

## Admin Dashboard

Screenshot:
![Admin Dashboard](images/admin/admin-dashboard-overview-viewport.png)

Full page:
[admin-dashboard-overview-full.png](images/admin/admin-dashboard-overview-full.png)

Responsive variants:
[admin-dashboard-overview-tablet.png](images/admin/admin-dashboard-overview-tablet.png) · [admin-dashboard-overview-mobile.png](images/admin/admin-dashboard-overview-mobile.png)

Route:
`/dashboard`

Role:
Admin

Look here first:
The hero summary, the top metric cards, and the command highlights list.

What matters operationally:
This is the fastest way for an admin to decide whether the active period needs immediate intervention or deeper inspection in a specialized page.

Advanced or optional:
Recent activity and lower-page workload/copy charts support confirmation after the first scan.

Common confusion:
A high top-line number is not automatically urgent. The dashboard is a prioritization surface, not a blame surface.

Callouts:
1. Page title and current role
2. `Open master schedule`
3. Top metric cards
4. Submission and unscheduled-section alerts
5. Lower-page workload summaries

## Staff Dashboard

Screenshot:
![Staff Dashboard](images/staff/staff-dashboard-overview-viewport.png)

Full page:
[staff-dashboard-overview-full.png](images/staff/staff-dashboard-overview-full.png)

Route:
`/dashboard`

Role:
Staff

Look here first:
The hero actions and the command highlights panel.

What matters operationally:
The staff variant narrows the control center to venue readiness, room activity, copy workload, and the next operational handoff.

Advanced or optional:
Left-nav links to `Duty Workload`, `Copy Count`, `Export Center`, and `External Exams` are useful after the top scan.

Common confusion:
This is the same route as the admin dashboard, but it is intentionally role-shaped and should not be read as a missing-admin screen.

Callouts:
1. Staff role badge
2. `Open master schedule`
3. `Room attendance`
4. Command highlights
5. Staff-facing nav group

## Teacher Dashboard

Screenshot:
![Teacher Dashboard](images/teacher/teacher-dashboard-overview-viewport.png)

Full page:
[teacher-dashboard-overview-full.png](images/teacher/teacher-dashboard-overview-full.png)

Responsive variants:
[teacher-dashboard-overview-tablet.png](images/teacher/teacher-dashboard-overview-tablet.png) · [teacher-dashboard-overview-mobile.png](images/teacher/teacher-dashboard-overview-mobile.png)

Route:
`/dashboard`

Role:
Teacher

Look here first:
The hero action, the assignment summary cards, and the first actionable work item.

What matters operationally:
The teacher dashboard should answer one question quickly: what is my next submission or exam-related responsibility?

Advanced or optional:
The dashboard links onward to `My Workload` and `My Exam Work` when detail is needed.

Common confusion:
An empty submission list is not always a problem. It may reflect no matching records for the active filter state.

Callouts:
1. Teacher role badge
2. Primary action button
3. Summary cards
4. First item in the work queue

## Admin Intelligence Dashboard

Screenshot:
![Admin Intelligence Dashboard](images/admin/admin-intelligence-dashboard-viewport.png)

Full page:
[admin-intelligence-dashboard-full.png](images/admin/admin-intelligence-dashboard-full.png)

Route:
`/admin-intelligence-dashboard`

Role:
Admin

Look here first:
The page currently shows the local error state instead of the intended analytics cards.

What matters operationally:
This capture is still valuable because it documents the runtime gap seen during the screenshot pass: the admin intelligence route shell rendered, but the local stack returned a load-error state.

Advanced or optional:
Use the screenshot together with [SCREENSHOT_CAPTURE_REPORT.md](SCREENSHOT_CAPTURE_REPORT.md) to trace the related backend and i18n follow-up items.

Common confusion:
The visible `dashboard.admin.loadErrorTitle` text is not normal UI copy. It is a missing translation key exposed by the current error path.

Callouts:
1. Route shell title and subtitle
2. Current load-error state
3. Sidebar link that reaches the page successfully

## Workload Duty Analytics

Screenshot:
![Workload Duty Analytics](images/admin/workload-duty-analytics-viewport.png)

Full page:
[workload-duty-analytics-full.png](images/admin/workload-duty-analytics-full.png)

Responsive variants:
[workload-duty-analytics-tablet.png](images/admin/workload-duty-analytics-tablet.png) · [workload-duty-analytics-mobile.png](images/admin/workload-duty-analytics-mobile.png)

Route:
`/workload-duty-analytics`

Role:
Admin

Look here first:
The empty-state message in the center of the page.

What matters operationally:
This is a real empty-state capture. The route, shell, and role wiring are correct, but the current filter scope returned no workload rows during capture.

Advanced or optional:
The staff and teacher variants of this page were also captured at `/duty-workload` and `/my-workload`.

Common confusion:
`No workload data available for the current filters.` is not a route failure. It is the intended empty-state behavior for a valid but empty result.

Callouts:
1. Page title and role context
2. Empty-state warning icon
3. Empty-state message
4. Sidebar entry for the workload view

## Governance Cockpit

Screenshot:
![Governance Cockpit](images/governance/governance-cockpit-viewport.png)

Full page:
[governance-cockpit-full.png](images/governance/governance-cockpit-full.png)

Responsive variants:
[governance-cockpit-tablet.png](images/governance/governance-cockpit-tablet.png) · [governance-cockpit-mobile.png](images/governance/governance-cockpit-mobile.png)

Route:
`/governance`

Role:
ESQ Head / Secretary / Admin

Look here first:
The risk-band area and the top-risk / recent-event sections.

What matters operationally:
The page rendered real governance structure, but the current local capture also surfaced untranslated governance keys. That makes this screenshot useful both as a guide and as evidence of a remaining localization gap.

Advanced or optional:
The left navigation places this page next to `Executive Analytics` and `Workflow`, reinforcing that it is a release-governance screen rather than a daily operations screen.

Common confusion:
Visible raw labels such as `governance.healthScore` are not intentional copy. They indicate missing i18n coverage in the current runtime.

Callouts:
1. Governance title and role context
2. Risk-band section
3. Blocker / approval counters
4. Top risks
5. Recent events

## Operational Health

Screenshot:
![Operational Health](images/governance/operational-health-viewport.png)

Full page:
[operational-health-full.png](images/governance/operational-health-full.png)

Responsive variants:
[operational-health-tablet.png](images/governance/operational-health-tablet.png) · [operational-health-mobile.png](images/governance/operational-health-mobile.png)

Route:
`/operational-health`

Role:
ESQ Head / Admin

Look here first:
Backend Health, Analytics Health, and Integration Readiness.

What matters operationally:
This page tells the team whether the stack is stable enough to trust the surrounding dashboards and workflows.

Advanced or optional:
The auto-refresh note matters when the team is watching live degradation or recovery.

Common confusion:
A score of `0 / 100` in the current local capture should be read as a warning to investigate, not as a final governance verdict by itself.

Callouts:
1. Backend Health
2. Analytics Health
3. Integration Readiness
4. Last-check / auto-refresh cues

## Audit Explorer

Screenshot:
![Audit Explorer](images/governance/audit-explorer-viewport.png)

Full page:
[audit-explorer-full.png](images/governance/audit-explorer-full.png)

Route:
`/audit-explorer`

Role:
Admin / ESQ Head

Look here first:
The three timeline tabs and the current empty-state panel.

What matters operationally:
This capture shows a valid empty audit state: the explorer loaded correctly, but there were no recorded events in the current local environment.

Advanced or optional:
The `Governance Timeline` and `Lifecycle Timeline` tabs matter when the team is proving sequence, ownership, or exception handling.

Common confusion:
`No audit events recorded` is not a crash. It is a meaningful absence of evidence and should be interpreted differently from a loading failure.

Callouts:
1. `Audit Events` tab
2. `Governance Timeline` tab
3. `Lifecycle Timeline` tab
4. Empty-state message

## Executive Analytics

Screenshot:
![Executive Analytics](images/executive/executive-analytics-viewport.png)

Full page:
[executive-analytics-full.png](images/executive/executive-analytics-full.png)

Route:
`/analytics`

Role:
Admin / ESQ Head / Secretary

Look here first:
The local capture shows the route shell and the current error message.

What matters operationally:
This page was reachable during the pass, but the local runtime returned `Error loading executive analytics: Not Found`. The screenshot is therefore documentation of the failure state rather than the intended analytics board.

Advanced or optional:
Cross-check this failure against the capture report before relying on the page for leadership guidance.

Common confusion:
Because the sidebar link works, users may assume the analytics data is also healthy. The screenshot shows that route availability and data availability are not the same thing.

Callouts:
1. Executive analytics route title
2. Current load-error message
3. Sidebar entry that still resolves

## Optimization Dashboard

Screenshot:
![Optimization Dashboard](images/admin/optimization-dashboard-viewport.png)

Full page:
[optimization-dashboard-full.png](images/admin/optimization-dashboard-full.png)

Route:
`/optimizer`

Role:
Admin

Look here first:
The pre-optimization setup, run controls, and assignment-results area.

What matters operationally:
This page is where an admin validates staffing and room-assignment assumptions before trusting an optimizer run.

Advanced or optional:
The lower results tabs and the trace route matter after the first pass through the setup form.

Common confusion:
A clean-looking setup page is not the same thing as a safe publishable schedule. The result still has to be reviewed.

Callouts:
1. Pre-optimization setup
2. Academic year / semester / exam type controls
3. `Run optimizer`
4. Assignment results tabs

## Optimization Trace

Screenshot:
![Optimization Trace](images/admin/optimization-trace-viewport.png)

Full page:
[optimization-trace-full.png](images/admin/optimization-trace-full.png)

Route:
`/optimizer-trace`

Role:
Admin

Look here first:
The session summary and the candidate count.

What matters operationally:
This capture shows a real trace-empty state. The route loaded, but the chosen session had no candidate records available during capture.

Advanced or optional:
Quality scoring becomes meaningful only when a run has produced candidate lineage.

Common confusion:
`No candidates in this session` is not equivalent to a failed optimizer route. It means the selected trace context currently has no recorded alternatives.

Callouts:
1. Session label
2. Quality score area
3. Candidate count
4. Empty-candidate message

## Export Center

Screenshot:
![Export Center](images/admin/export-center-viewport.png)

Full page:
[export-center-full.png](images/admin/export-center-full.png)

Route:
`/exports-center`

Role:
Admin / Staff

Look here first:
The summary cards and the export-channel families.

What matters operationally:
This page consolidates schedule, workload, optimization, workflow, and external-exam exports into one operational handoff hub.

Advanced or optional:
The lower `Historical schedule review` card becomes important when reconciling imports and final adjusted plans.

Common confusion:
Users often expect copy/print exports to live here directly. The screenshot helps show that some printing actions still live in their dedicated workflow pages.

Callouts:
1. Export summary cards
2. Exam documents
3. Optimization results
4. Staff workload reports
5. Historical schedule review

## Import Data

Screenshot:
![Import Data](images/admin/import-data-viewport.png)

Full page:
[import-data-full.png](images/admin/import-data-full.png)

Route:
`/import`

Role:
Admin

Look here first:
The progress steps and the first-step import form.

What matters operationally:
This is the controlled entry point for loading term, section, and enrollment data into the current cycle.

Advanced or optional:
The row-review and validation-summary steps matter later, but the first decision is always whether the correct import type and term context have been selected.

Common confusion:
Users often expect data to be written immediately after upload. The screen makes it clear that commit happens only after review.

Callouts:
1. Progress steps
2. Active-period note
3. Import type selector
4. Academic year / semester / exam type fields

## Settings

Screenshot:
![Settings](images/admin/settings-viewport.png)

Full page:
[settings-full.png](images/admin/settings-full.png)

Route:
`/settings`

Role:
Admin

Look here first:
The `System settings preview` banner and the `View-As Mode` panel.

What matters operationally:
This page combines configuration preview with role-preview controls so an admin can understand how the shell behaves for each workspace.

Advanced or optional:
`Reset View-As` and the role-preview cards matter mainly when checking the UI impact of a role switch.

Common confusion:
Previewing another role here does not change the locked production role; it changes the admin's current view context only.

Callouts:
1. `Reset View-As`
2. `Save Draft`
3. Current preview banner
4. Role-preview cards

## Platform Configuration

Screenshot:
![Platform Configuration](images/admin/platform-configuration-viewport.png)

Full page:
[platform-configuration-full.png](images/admin/platform-configuration-full.png)

Route:
`/platform-config`

Role:
Admin

Look here first:
The current local capture shows the route shell and a loading state.

What matters operationally:
This screenshot documents that the page route is present and reachable, but the local pass did not finish rendering the D3 configuration content.

Advanced or optional:
The guide should be revisited after a stable render is available, because this page is intended to expose governance flow, workload policy, and analytics contracts.

Common confusion:
`Loading` here is not a conceptual placeholder in the manual. It is the real runtime state seen during the capture pass.

Callouts:
1. Platform Configuration title
2. Current loading state
3. Sidebar link location

## Schedule Overview

Screenshot:
![Schedule Overview](images/admin/schedule-overview-viewport.png)

Full page:
[schedule-overview-full.png](images/admin/schedule-overview-full.png)

Route:
`/schedule`

Role:
Admin / Staff / Teacher

Look here first:
The export actions, search and filter row, and the current empty-state message.

What matters operationally:
This is the reusable schedule board for inspecting sessions, exporting schedule artifacts, and checking whether filters are hiding the needed session.

Advanced or optional:
Grouping by date or exam room becomes useful once records are visible.

Common confusion:
`No schedule sessions match these filters.` is a working empty-state, not a page failure.

Callouts:
1. Export actions
2. Search and filter row
3. Grouping controls
4. Empty-state guidance

## Submissions Overview

Screenshot:
![Submissions Overview](images/admin/submissions-overview-viewport.png)

Full page:
[submissions-overview-full.png](images/admin/submissions-overview-full.png)

Route:
`/submissions`

Role:
Admin / ESQ Head / Secretary / Department Supervisor / Teacher

Look here first:
The summary counters, submission-state tabs, and the empty-state or result list.

What matters operationally:
This page is the shared submission-monitoring surface for roles that need to check review readiness, approval state, and revision demand.

Advanced or optional:
Search becomes useful when the list grows, but the first decision is usually state-based rather than keyword-based.

Common confusion:
An empty tab is not always a missing workflow. It may simply mean the current role and filters have no matching records.

Callouts:
1. Summary counters
2. Submission-state tabs
3. Search field
4. Empty-state guidance

## Print Review

Screenshot:
![Print Review](images/admin/print-review-viewport.png)

Full page:
[print-review-full.png](images/admin/print-review-full.png)

Route:
`/printreview`

Role:
Admin / ESQ Head / Secretary

Look here first:
The period strip, status counters, and the submissions filter row.

What matters operationally:
This page is the final pre-handoff checkpoint before printing. Even an empty queue is meaningful because it tells the team no submissions are ready in the current view.

Advanced or optional:
Search and release-state tabs matter when the queue starts to fill.

Common confusion:
An empty `Print Review` list is not automatically bad. It may simply mean nothing is approved for print yet.

Callouts:
1. `Submission review & print handoff`
2. Status counters
3. Submission-state tabs
4. Empty-state message

## Print Queue

Screenshot:
![Print Queue](images/print-shop/print-queue-viewport.png)

Full page:
[print-queue-full.png](images/print-shop/print-queue-full.png)

Route:
`/print-queue`

Role:
Print shop

Look here first:
Pending jobs, urgent queue, and dispatch-readiness guidance.

What matters operationally:
This is the live production-floor queue for dispatch and delivery. It is the clearest visual for the distribution workflow in the current build.

Advanced or optional:
`Export Manifest` and `Refresh Queue` are secondary controls compared with the queue-state panels themselves.

Common confusion:
The print queue is not the same thing as teacher submission review. It starts only after content is already approved for print.

Callouts:
1. Pending jobs
2. Urgent queue
3. Supply watch
4. Dispatch readiness
5. Manifest and refresh actions

## Teacher Exam Work

Screenshot:
![Teacher Exam Work](images/teacher/teacher-exam-work-viewport.png)

Full page:
[teacher-exam-work-full.png](images/teacher/teacher-exam-work-full.png)

Route:
`/myexam`

Role:
Teacher

Look here first:
Assigned responsibilities, pending count, and the first `Start submission` button.

What matters operationally:
This page is the clearest teacher-facing control surface for exam submission readiness and ownership.

Advanced or optional:
Course metadata, room hints, and schedule rows matter after the teacher has confirmed the correct record.

Common confusion:
Multiple similar section cards can make users open the wrong exam record if they scan by course title only.

Callouts:
1. Summary cards
2. Responsibility list
3. Submission status badge
4. `Start submission`

## Daily Room Attendance

Screenshot:
![Daily Room Attendance](images/staff/room-operations-attendance-viewport.png)

Full page:
[room-operations-attendance-full.png](images/staff/room-operations-attendance-full.png)

Route:
`/attendance`

Role:
Staff / Admin / Teacher / Department Supervisor

Look here first:
The operating-date filter and the empty-state guidance.

What matters operationally:
This is a real empty-state capture for room operations. It shows the route and action control working even when no attendance records exist for the chosen date.

Advanced or optional:
`Open check-ins` is the natural next drilldown when attendance data should exist but does not yet appear here.

Common confusion:
No attendance data does not always mean the exam failed. It can simply mean the selected date has not been recorded yet.

Callouts:
1. Operating date picker
2. `Open check-ins`
3. Empty-state message
