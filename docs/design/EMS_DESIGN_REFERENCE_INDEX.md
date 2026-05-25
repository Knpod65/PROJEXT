# EMS Design Reference Index

This index groups the real EMS design-context sources into the order Claude Design should use them.

## 1. Primary UI/UX Design Sources

### `docs/architecture/UX_UI_HUMANIZATION_AUDIT.md`

- Purpose: current real-root replacement for the missing UI consistency report.
- Why it matters: it explains the strongest UX strengths, the remaining inconsistencies, and the humanization gaps that still need attention.
- How Claude Design should use it: treat it as the baseline critique of the current interface; preserve the role-aware shell, bilingual infrastructure, and screenshot/manual foundation.

### `docs/architecture/FRONTEND_SUPERIOR_ENGINEER_AUDIT.md`

- Purpose: engineering-side view of the frontend, including route drift, legacy/V2 coexistence, shell consistency, and load/build health.
- Why it matters: the design cannot ignore route reality, unfinished surfaces, or maintenance drift.
- How Claude Design should use it: use it to avoid redesigning the wrong page family, and to understand which surfaces are canonical versus historical.

### `docs/architecture/EMS_DESIGN_CONSISTENCY_CHECKLIST.md`

- Status: missing in the real EMS root.
- Why it matters: it was requested as a primary source but is not available for direct attachment.
- How Claude Design should use it: do not rely on it; use the real-root substitute documents instead.

### `docs/architecture/UI_UX_CONSISTENCY_REPORT.md`

- Status: missing in the real EMS root.
- Why it matters: this was expected to be the canonical UI consistency source.
- How Claude Design should use it: do not fabricate or infer its contents; use the substitute audit and screenshot evidence.

## 2. System Maturity / Engineering Context

### `docs/architecture/EMS_FULL_SYSTEM_SUPERIOR_DEVELOPER_REVIEW.md`

- What it says about frontend maturity: the frontend is strong in shell, i18n, and role-aware routing, but still has legacy/V2 drift, some large pages, and limited app-level automated test coverage.
- Which risks matter for design: visible route drift, incomplete surfaces, and places where the UI may imply more maturity than the backend actually supports.
- Which risks are backend-only and should not distract design: database hardening, backup/restore, production secret handling, and other deployment readiness gaps that do not change the visual redesign brief.

## 3. Screenshot Evidence Sources

### `docs/humanization/screenshot-atlas/major-pages.md`

- Purpose: visual index of the first real screenshot pass.
- Why it matters: it shows what the current screens look like and what each page means operationally.
- How Claude Design should use it: preserve the operational reading order of each screen and note which variants already exist.

### `docs/humanization/screenshot-atlas/SCREENSHOT_CAPTURE_REPORT.md`

- Purpose: capture log for the screenshot pass.
- Why it matters: it explicitly marks current issues, empty states, and pages that rendered errors or partial states.
- How Claude Design should use it: separate healthy UI from captured failure states, and do not treat broken screenshots as design inspiration.

### `docs/humanization/screenshot-atlas/images/`

- Purpose: real screenshot evidence folder.
- Why it matters: this is the visual truth set for the current EMS UI.
- How Claude Design should use it: inspect the actual filenames and variants, then decide what must be preserved, simplified, or recaptured later.

### What is likely stale or needs recapture later

- Admin intelligence and executive analytics are known to have runtime issues in the capture report.
- Platform configuration was captured in a loading state, so that screenshot should be treated as a route-presence artifact rather than a finished design reference.
- Empty-state captures are still useful, but they should be recaptured after seeded data or UX polish if the redesign changes the data density.

## 4. Humanization / Journey Sources

### `docs/humanization/dashboard-guides/README.md`

- Purpose: explains how dashboard screens should be interpreted in operational terms.
- Why it matters: it keeps the redesign focused on urgency, risk, readiness, and next action rather than chart decoration.
- How Claude Design should use it: preserve the operational hierarchy of each dashboard and its role-specific meaning.

### `docs/humanization/journeys/README.md`

- Purpose: defines workflow-based visual journeys.
- Why it matters: EMS is not a static dashboard app; it is a workflow system.
- How Claude Design should use it: redesign screens in workflow order, not as isolated panels.

### `docs/operations/DEMO_USER_JOURNEY_SCRIPT.md`

- Purpose: presenter-facing narrative for the demo flow.
- Why it matters: it shows which screens are expected to be shown first and how stakeholders will mentally traverse the system.
- How Claude Design should use it: prioritize screens that support the scripted demo path and make those transitions obvious.

### `docs/operations/DEMO_SCOPE_AND_BOUNDARIES.md`

- Purpose: explicit honesty boundary for demo claims.
- Why it matters: the redesign must not visually imply production readiness, live Faculty LAN deployment, or completed auth integration.
- How Claude Design should use it: keep the interface honest about provisional status and avoid hiding blockers from admin/executive surfaces.

## 5. Demo Readiness / Route Sources

### `docs/operations/DEMO_ROUTE_SMOKE_MAP.md`

- Purpose: route priority and expected demo state map.
- Why it matters: it tells you which pages are demo-critical and which are optional.
- How Claude Design should use it: design the most polished experience first for the critical routes, then polish the supporting routes.

### `docs/operations/DEMO_ACCOUNT_AND_DATA_READINESS.md`

- Purpose: account and seeded-data readiness audit.
- Why it matters: it explains which pages may appear empty and which roles may require view-as or seeded accounts to work.
- How Claude Design should use it: design clean empty states and avoid relying on fake density to make the interface look complete.

## 6. Auth / Print Shop / Faculty LAN Context

### `docs/deployment/PILOT_ROUTE_AND_AUTH_MAPPING.md`

- Purpose: preliminary Faculty LAN route mapping and auth flow sketch.
- Why it matters: it defines the current routing assumptions and the pending Laravel integration boundary.
- How Claude Design should use it: keep login, route hierarchy, and protected-lane semantics aligned with the real deployment plan.

### `docs/architecture/HYBRID_AUTH_MODEL_CMU_AND_PRINT_SHOP.md`

- Purpose: separates internal CMU/POLSCI users from external print-shop users.
- Why it matters: the design must preserve two distinct identity lanes.
- How Claude Design should use it: do not design print shop as a fake CMU user; keep partner access visibly separate.

### `docs/architecture/PRINT_SHOP_AUTH_OPTIONS_MATRIX.md`

- Purpose: compares safe external-auth options for the print shop lane.
- Why it matters: it constrains what the login and partner-access UX should imply.
- How Claude Design should use it: only surface the auth pattern that the current deployment phase can honestly support.

### `docs/deployment/POLSCI_OAUTH_FLOW_ANALYSIS.md`

- Purpose: records the observed POLSCI login path and unknown callback contract.
- Why it matters: it prevents the redesign from pretending the callback is already verified.
- How Claude Design should use it: keep the auth bridge visually provisional until the Laravel owner confirms the contract.

### `docs/deployment/FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md`

- Purpose: integration boundary for Faculty Laravel + CMU auth.
- Why it matters: it is the clearest warning that the bridge is still pending verification.
- How Claude Design should use it: design login as a future integration point, not a completed product promise.

## 7. Files Not Needed for Design

- Backend-only audits, service deep-dives, queue/blob internals, and hardening checklists should not be attached unless the redesign explicitly touches the related user-visible surface.
- Database-only, migration-only, and production-secret documents are out of scope for visual redesign.
- Test logs, build logs, and low-level incident logs should be ignored unless they explain a visible UI failure.
- Route/runtime implementation notes that do not affect visible layout or workflow should remain context-only.

## 8. Practical Reading Order for Claude Design

1. Read the attachment list and the design handoff brief.
2. Read the screenshot atlas and the screenshot capture report.
3. Read the humanization and journey docs.
4. Read the auth/print-shop docs only if redesigning login, entry flow, or external partner access.
5. Use the engineering audits only to avoid designing against stale routes or unsupported surfaces.
