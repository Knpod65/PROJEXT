# Claude Design Attachment List

This is the attachment set Claude Design should read before any EMS redesign work.

## A. MUST ATTACH FOR FULL REDESIGN

- `docs/design/EMS_DESIGN_HANDOFF_BRIEF.md`
- `docs/design/CLAUDE_DESIGN_MASTER_PROMPT.md`
- `docs/architecture/UX_UI_HUMANIZATION_AUDIT.md`
- `docs/architecture/FRONTEND_SUPERIOR_ENGINEER_AUDIT.md`
- `docs/humanization/screenshot-atlas/major-pages.md`
- `docs/humanization/screenshot-atlas/SCREENSHOT_CAPTURE_REPORT.md`
- `docs/humanization/screenshot-atlas/images/`

Why this group is needed:

- It gives Claude Design the visual truth set, the current UX critique, and the live frontend maturity context.
- It keeps the redesign anchored to actual EMS screens instead of generic dashboard patterns.

What Claude Design should extract:

- Current page structure and role-aware shell behavior.
- Current strengths that should be preserved.
- Broken or incomplete screens that must not be mistaken for final UI.
- Real screenshot evidence, including empty states and known error states.

What Claude Design should ignore:

- Any broken runtime state that should not be converted into a design trend.
- Old assumptions about page ownership that no longer match live routes.

## B. SHOULD ATTACH FOR DEMO-FOCUSED REDESIGN

- `docs/operations/DEMO_SCOPE_AND_BOUNDARIES.md`
- `docs/operations/DEMO_USER_JOURNEY_SCRIPT.md`
- `docs/operations/DEMO_ROUTE_SMOKE_MAP.md`
- `docs/operations/DEMO_ACCOUNT_AND_DATA_READINESS.md`
- `docs/humanization/dashboard-guides/README.md`
- `docs/humanization/journeys/README.md`
- `docs/architecture/DEMO_READINESS_SOURCE_REVIEW.md`

Why this group is needed:

- It defines the demo story, the route priority, the honest limits, and the data readiness gaps.
- It helps Claude Design prioritize what a stakeholder is most likely to see first.

What Claude Design should extract:

- Which routes are demo-critical.
- Which roles need polished and clear experiences first.
- Which empty states are acceptable versus which screens need seeded content.
- What the demo may and may not claim.

What Claude Design should ignore:

- Any promise of production readiness that is not actually verified.
- Any idea that empty states can be hidden instead of designed clearly.

## C. ATTACH IF REDESIGNING LOGIN / AUTH / PRINT SHOP

- `docs/deployment/PILOT_ROUTE_AND_AUTH_MAPPING.md`
- `docs/architecture/HYBRID_AUTH_MODEL_CMU_AND_PRINT_SHOP.md`
- `docs/architecture/PRINT_SHOP_AUTH_OPTIONS_MATRIX.md`
- `docs/deployment/POLSCI_OAUTH_FLOW_ANALYSIS.md`
- `docs/deployment/FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md`

Why this group is needed:

- It defines the current and future login/auth boundaries.
- It prevents the redesign from collapsing external print-shop users into a fake CMU identity.

What Claude Design should extract:

- The difference between internal CMU/POLSCI users and external partner users.
- Which auth assumptions are still provisional.
- Which login flows are only planned, not complete.

What Claude Design should ignore:

- Any claim that the Laravel bridge is already implemented.
- Any login pattern that trusts unverified tokens or query parameters.

## D. DO NOT ATTACH UNLESS ASKED

- Backend-only audits.
- Database-only audits.
- Queue/blob internals.
- Production secret or environment-variable hardening docs.
- Test logs and build logs.
- Migration details and other implementation-only notes.

Why these should stay out:

- They do not materially change the visual redesign brief.
- They can distract Claude Design from the operational UX and make the handoff noisy.

What Claude Design should still know:

- These docs may matter later for implementation, but they are not the first attachment set for a design pass.
