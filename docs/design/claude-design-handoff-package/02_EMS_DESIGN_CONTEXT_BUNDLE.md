# EMS Design Context Bundle

This bundle condenses the real EMS design sources into one readable file for Claude Design.

## 1. `docs/architecture/UI_UX_CONSISTENCY_REPORT.md`

- Status: missing
- Summary: requested primary UI consistency source not present in the real EMS root.
- Design implications: do not invent a consistency report; use the real substitute audit.
- Preserve: the expectation that EMS should remain role-aware, bilingual, and operationally legible.
- Redesign: the current generic-dashboard feeling on some pages.
- Risks / warnings: do not pull in outside-workspace content as if it were part of EMS.

## 2. `docs/architecture/EMS_DESIGN_CONSISTENCY_CHECKLIST.md`

- Status: missing
- Summary: requested checklist not present in the real EMS root.
- Design implications: there is no checklist document to attach; rely on the actual audits and atlas.
- Preserve: the design intent that EMS should be consistent across roles and surfaces.
- Redesign: inconsistent role presentation and mixed page maturity.
- Risks / warnings: missing source means the design handoff must be explicit about the gap.

## 3. `docs/architecture/UX_UI_HUMANIZATION_AUDIT.md`

- Status: exists
- Summary:
  - Real-root substitute for the missing UI consistency report.
  - Says EMS already has a role-aware shell, bilingual dictionaries, role manuals, screenshot atlas material, and humanization docs.
  - Notes the main weaknesses as uneven legacy-page consistency, cognitive load on large pages, raw string drift, and the absence of a dedicated current UI consistency report.
  - Says print shop is already isolated as a narrow operational role.
  - Says mobile and tablet readiness exists but still needs device validation.
- Design implications: this is the best high-level UX audit to anchor the redesign.
- Preserve: role-aware shell, bilingual clarity, humanization foundation, separate print-shop lane.
- Redesign: large-page cognitive load, legacy/V2 confusion, and surfaces that still read as generic admin UI.
- Risks / warnings: avoid assuming every translated surface is equally mature; some pages still need simplification.

## 4. `docs/architecture/FRONTEND_SUPERIOR_ENGINEER_AUDIT.md`

- Status: exists
- Summary:
  - Frontend is a real React 18 SPA with React Router, React Query, centralized API access, and centralized i18n dictionaries.
  - Role-aware routing and AppShell are strong.
  - Active V2 pages coexist with legacy tracked pages.
  - Platform/faculty config surfaces are partially wired.
  - There is limited application-level automated UI coverage in repo source.
- Design implications: do not design against stale route ownership or unfinished config surfaces.
- Preserve: shell consistency, route gating, auth bootstrap, table/empty-state primitives.
- Redesign: legacy/V2 drift and pages that visually imply more completeness than the backend supports.
- Risks / warnings: bundle size and missing app tests matter later, but they should not dominate the visual redesign brief.

## 5. `docs/architecture/EMS_FULL_SYSTEM_SUPERIOR_DEVELOPER_REVIEW.md`

- Status: exists
- Summary:
  - Backend test coverage is strong.
  - The system has broad architectural maturity and role-aware app structure.
  - The audit flags backend startup/schema creation, SQLite fallback risk, unverified Laravel auth contract, and some frontend surfaces that look more complete than backend support really is.
- Design implications: the UI must not oversell backend maturity or hide pending contract work.
- Preserve: the institutional seriousness of the platform and the existing role/system breadth.
- Redesign: any page that visually looks ready for live Faculty LAN operation when it is still provisional.
- Risks / warnings: backend-only production gaps should not distract from the visual handoff.

## 6. `docs/humanization/screenshot-atlas/major-pages.md`

- Status: exists
- Summary:
  - Documents role selection, login, admin dashboard, staff dashboard, teacher dashboard, workload analytics, and governance cockpit.
  - Uses real screenshots with viewport/full/responsive variants where available.
  - Explains the first scan target and the operational meaning of each screen.
  - Captures known error states for admin intelligence and other routes.
  - Flags empty-state captures as valid and meaningful.
- Design implications: this is the visual truth set for the current UI.
- Preserve: page hierarchy, role-specific screen meaning, and callout structure.
- Redesign: layouts that do not respect the operational reading order already established in the atlas.
- Risks / warnings: some pages are intentionally captured in error or empty states and should not be treated as ideal UI.

## 7. `docs/humanization/screenshot-atlas/SCREENSHOT_CAPTURE_REPORT.md`

- Status: exists
- Summary:
  - First real screenshot pass dated May 20, 2026.
  - Captured admin, staff, teacher, governance/executive, and print-shop pages.
  - Records that admin intelligence rendered a load-error state and executive analytics returned a not-found error.
  - Records visible untranslated keys in governance and status labels.
  - Notes empty-state captures for workload and room-operation pages.
- Design implications: the handoff must be honest about what is healthy and what is broken.
- Preserve: valid empty states, role-specific screenshot coverage, and the capture methodology.
- Redesign: raw-key leakage, error-state clarity, and any route that currently fails in the atlas.
- Risks / warnings: some screenshots are intentionally evidence of failure, not design targets.

## 8. `docs/humanization/screenshot-atlas/images/`

- Status: exists
- Summary:
  - Contains the real PNG screenshot set for admin, staff, teacher, governance, executive, and print-shop pages.
  - Includes viewport, full-page, tablet, and mobile variants for many screens.
  - Provides the best current visual evidence for page composition and density.
- Design implications: use the actual screenshots as direct references for page-by-page redesign planning.
- Preserve: patterns that already help comprehension, especially where role cues and action hierarchy are clear.
- Redesign: screens that are too dense, too generic, or visually underpowered.
- Risks / warnings: Claude Design should not pretend all screenshots are current or healthy; verify against the capture report.

Screenshot atlas note:

- Image folder path: `docs/humanization/screenshot-atlas/images/`
- Known screenshot report: `docs/humanization/screenshot-atlas/SCREENSHOT_CAPTURE_REPORT.md`
- Freshness: useful and real, but some routes need recapture after runtime fixes and some pages captured as error states must be treated as evidence only.

## 9. `docs/humanization/dashboard-guides/README.md`

- Status: exists
- Summary:
  - Explains that dashboard guides should describe risk, urgency, readiness, and next action.
  - Defines a standard guide structure and interpretation rules.
  - Tells designers not to treat colors as decoration.
- Design implications: dashboard pages should communicate operational meaning, not just chart data.
- Preserve: urgency hierarchy, escalation logic, and governance meaning.
- Redesign: any dashboard UI that feels like a generic KPI wall.
- Risks / warnings: do not turn the guide into a purely technical chart legend.

## 10. `docs/humanization/journeys/README.md`

- Status: exists
- Summary:
  - Defines workflow journeys as screen sequences with decision points and escalation paths.
  - Emphasizes that screenshots should follow the workflow order.
  - Includes teacher, staff, governance, workload, operational health, and predictive/intelligence journeys.
- Design implications: redesign pages in a workflow context, not as isolated surfaces.
- Preserve: the sequence-of-operations mindset.
- Redesign: screens that do not clearly explain what happens next.
- Risks / warnings: isolated screens without a journey narrative are not enough.

## 11. `docs/operations/DEMO_SCOPE_AND_BOUNDARIES.md`

- Status: exists
- Summary:
  - Defines what the demo is and is not.
  - Explicitly says the demo is not production, not Faculty LAN live deployment, and not completed auth integration.
  - Names the allowed demo capabilities and what must not be claimed.
- Design implications: the UI must support honest framing and not imply false readiness.
- Preserve: transparency about provisional features and local demo context.
- Redesign: any visual element that implies the system is already production-grade when it is not.
- Risks / warnings: do not obscure blockers for admin/executive users who need honest status.

## 12. `docs/operations/DEMO_USER_JOURNEY_SCRIPT.md`

- Status: exists
- Summary:
  - Provides a staged demo narrative from login to admin dashboard, role switching, workload analytics, schedule/submissions, governance, operational health, audit explorer, teacher workflow, and print shop.
  - Includes demo account reference and what not to say.
- Design implications: the UI should make the demo path obvious and smooth.
- Preserve: role-based storytelling and operational sequencing.
- Redesign: screens that make the demo hard to narrate or easy to misrepresent.
- Risks / warnings: the script assumes local demo accounts and local auth, not the pending Faculty LAN bridge.

## 13. `docs/operations/DEMO_ROUTE_SMOKE_MAP.md`

- Status: exists
- Summary:
  - Ranks routes from critical to optional.
  - Lists current issues such as load errors, untranslated keys, and empty-state-tolerant pages.
  - Marks redirect and hidden routes that are not demo critical.
- Design implications: use this to decide which pages deserve the most design attention first.
- Preserve: route priority hierarchy.
- Redesign: critical routes that are still weak or inconsistent.
- Risks / warnings: hidden and redirect routes should not steal attention from the core demo pages.

## 14. `docs/operations/DEMO_ACCOUNT_AND_DATA_READINESS.md`

- Status: exists
- Summary:
  - Describes seed data, demo account coverage, and workspace assignment caveats.
  - Shows that most core roles exist but some flows rely on view-as or stable workspace assignment.
  - Calls out pages that may be empty-state in the demo.
- Design implications: empty states must be intentional and readable.
- Preserve: role coverage and seeded demo pathways.
- Redesign: screens that look broken when the real issue is simply empty data.
- Risks / warnings: do not paper over data gaps with fake visuals.

## 15. `docs/deployment/PILOT_ROUTE_AND_AUTH_MAPPING.md`

- Status: exists
- Summary:
  - Draft route mapping for Faculty LAN deployment.
  - Marks all route assumptions as preliminary.
  - Explains the current conceptual auth flow and open questions about mounting and middleware.
- Design implications: login and route hierarchy should remain provisional where the contract is not verified.
- Preserve: backend-authoritative permission framing.
- Redesign: any login flow that pretends the bridge is finished.
- Risks / warnings: route names and mounting assumptions may still change.

## 16. `docs/architecture/HYBRID_AUTH_MODEL_CMU_AND_PRINT_SHOP.md`

- Status: exists
- Summary:
  - Separates internal CMU/POLSCI users from external print-shop users.
  - Says print-shop users must not be modeled as fake CMU students or staff.
  - Defines allowed and forbidden permissions for lane B.
- Design implications: the partner lane must be visibly distinct and limited.
- Preserve: the separate identity model and least-privilege framing.
- Redesign: any UI that collapses the two lanes into one identity concept.
- Risks / warnings: external access must remain constrained and auditable.

## 17. `docs/architecture/PRINT_SHOP_AUTH_OPTIONS_MATRIX.md`

- Status: exists
- Summary:
  - Compares local EMS print-shop accounts, Laravel external partner accounts, signed links, and staff-mediated fallback.
  - Recommends different options for demo, controlled pilot, and long-term use.
- Design implications: the login and access design should reflect the selected horizon, not assume a final solution.
- Preserve: the notion that the print shop is a controlled partner lane.
- Redesign: any auth visual that implies the final identity model is already chosen.
- Risks / warnings: demo fallback should not be mistaken for long-term architecture.

## 18. `docs/deployment/POLSCI_OAUTH_FLOW_ANALYSIS.md`

- Status: exists
- Summary:
  - Records the observed POLSCI OAuth login URL and callback pattern.
  - Says the current callback appears to belong to the faculty portal, not EMS.
  - Lists unknowns about callback payload, token lifecycle, and session shape.
- Design implications: do not visually promise a direct EMS callback unless the contract is verified.
- Preserve: the distinction between gateway login and EMS session ownership.
- Redesign: any auth screen that implies EMS already owns the full OAuth flow.
- Risks / warnings: the callback contract is still open and must remain explicit in the docs.

## 19. `docs/deployment/FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md`

- Status: exists
- Summary:
  - Integration spec for Faculty Laravel + CMU auth.
  - Makes it clear the contract is still draft and unverified.
  - Documents session, token, logout, and audit questions that must be answered before integration code exists.
- Design implications: login redesign must stay honest about what is pending.
- Preserve: the server-side identity boundary and DB-authoritative role mapping.
- Redesign: any auth experience that behaves like the bridge is complete.
- Risks / warnings: avoid exposing or implying trust in unverified client-side identity claims.

## 20. `docs/architecture/DEMO_READINESS_SOURCE_REVIEW.md`

- Status: exists
- Summary:
  - Cross-checks which source docs matter for demo versus production.
  - Identifies the demo-blocking gaps in the screenshot report and what can be deferred.
  - Recommends the order of gaps to fix before a demo.
- Design implications: useful as a demo-honesty backstop.
- Preserve: the distinction between demo blockers and production-only issues.
- Redesign: nothing directly, but it helps prevent overpromising in the handoff brief.
- Risks / warnings: this is supporting context, not a primary visual source.
