# Screenshot Capture Report

## Summary

This report records the first real screenshot pass for the EMS humanization package.

- Capture date: May 20, 2026
- Frontend target: `http://127.0.0.1:3000`
- Backend health target: `http://127.0.0.1:8000/health`
- Output root: `docs/humanization/screenshot-atlas/images/`

## Pages Captured

### Public entry

- `/role-selection`
- `/login`

### Admin workspace

- `/dashboard`
- `/admin-intelligence-dashboard`
- `/workload-duty-analytics`
- `/optimizer`
- `/optimizer-trace`
- `/exports-center`
- `/import`
- `/historical-schedules`
- `/platform-config`
- `/settings`
- `/rooms-v2`
- `/schedule`
- `/printreview`
- `/submissions`

### Staff-facing capture

- `/dashboard`
- `/duty-workload`
- `/attendance`
- `/checkins`
- `/schedule`

Note:
The first attempt with a seeded staff account redirected back to role selection because the current backend reported `workspace_not_assigned` for that user. The final staff screenshots were captured through a valid admin session using the existing `view-as` capability for the `staff` role.

### Teacher workspace

- `/dashboard`
- `/my-workload`
- `/myexam`
- `/submissions`
- `/schedule`

### Governance / executive workspace

- `/governance`
- `/operational-health`
- `/audit-explorer`
- `/analytics`

### Print-shop workspace

- `/print-queue`

## Roles Used

- Admin: `mathawee.m`
- Teacher: `pailin.phu`
- Governance / executive: `napaporn.ph`
- Print shop: `printshop.ops`
- Staff final capture path: admin session with `view-as = staff`

## Screenshot Files Created

- `admin/` - 40 PNG files
- `staff/` - 10 PNG files
- `teacher/` - 14 PNG files
- `executive/` - 2 PNG files
- `governance/` - 10 PNG files
- `print-shop/` - 2 PNG files
- `intelligence/` - 0 PNG files reserved for future routed intelligence pages

Total:
- 78 PNG files

Variants created:
- `-viewport.png`
- `-full.png`
- `-tablet.png` for responsive subset
- `-mobile.png` for responsive subset

## Captured With Issues

### Admin Intelligence Dashboard

- Route: `/admin-intelligence-dashboard`
- Status: reachable, but rendered a load-error state in the local stack
- Visible issue: `dashboard.admin.loadErrorTitle`
- Operational note: useful as an honest screenshot of the current failure mode, but not a healthy analytics capture

### Executive Analytics

- Route: `/analytics`
- Status: reachable, but rendered `Error loading executive analytics: Not Found`
- Operational note: treated as a captured error state, not a successful dashboard render

### Platform Configuration

- Route: `/platform-config`
- Status: reachable, but remained in a visible loading state during the local pass
- Operational note: captured as a route-presence screenshot rather than a fully rendered configuration board

### Governance Cockpit

- Route: `/governance`
- Status: rendered
- Visible issue: untranslated keys such as `governance.healthScore`, `governance.blockers`, `governance.pendingApprovals`

### Workload and room-operation pages

- `/workload-duty-analytics`
- `/duty-workload`
- `/my-workload`
- `/attendance`
- `/audit-explorer`

Status:
These were valid captures, but the local data for this pass was mostly empty-state or no-record state.

Operational note:
The empty-state screens are still valuable because they document the current UX for real no-data conditions.

## Pages Not Captured

The following humanization guides do not have a matching live route in the current frontend build, so no real screenshots were created for them:

- `predictive-intelligence`
- `national-intelligence`
- `futures-intelligence`
- `alert-systems`

Reason:
The current app route map does not expose dedicated pages for those guide titles.

## Console Errors Found

### Meaningful findings

- Missing i18n key: `dashboard.admin.loadErrorTitle`
- Missing i18n keys: `governance.blockers`, `governance.overrides`, `governance.rollbacks`, `governance.escalations`, `governance.pendingApprovals`, `governance.healthScore`
- Missing i18n keys: `status.submitted`, `status.approved`, `status.rejected`, `status.released`, `status.swap_open`, `status.confirmed`
- Executive Analytics route returned a local load error (`Not Found`)
- Admin Intelligence route surfaced a local load-error path

### Transient capture-noise findings

The first bulk headless pass generated many `net::ERR_INSUFFICIENT_RESOURCES` request failures. Those were reduced by targeted recapture for the most important pages and should be treated as a headless-pass stress artifact rather than a user-facing browser finding by default.

## Missing i18n Found In Visuals

- `dashboard.admin.loadErrorTitle`
- `governance.healthScore`
- `governance.blockers`
- `governance.overrides`
- `governance.rollbacks`
- `governance.escalations`
- `governance.pendingApprovals`
- `status.submitted`
- `status.approved`
- `status.rejected`
- `status.released`
- `status.swap_open`
- `status.confirmed`

## Follow-up Fixes Needed

1. Fix the admin-intelligence load-error path and localize its error-state title.
2. Fix the executive-analytics backend/data route returning `Not Found`.
3. Add the missing governance and generic status translation keys.
4. Re-run a second screenshot pass for `Admin Intelligence` and `Executive Analytics` after those runtime fixes land.
5. Re-run a true staff-account capture once workspace assignments in the local backend are stable again.
