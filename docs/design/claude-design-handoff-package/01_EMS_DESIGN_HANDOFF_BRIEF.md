# EMS Design Handoff Brief

## 1. What EMS Is

EMS is the Exam Management System for the Faculty of Political Science and Public Administration at Chiang Mai University.

It is an operational platform for:

- exam scheduling
- submission handling
- workload and duty tracking
- governance and audit visibility
- operational health monitoring
- print queue and print-shop handling

It is used by:

- admin
- staff
- teacher
- supervisor
- executive / governance
- print_shop
- student

## 2. Current Design State

- The app already has a shared AppShell and a role-aware navigation structure.
- Thai/English i18n already exists and is part of the current UX foundation.
- There are dashboard pages, workload analytics, schedule pages, governance pages, and audit surfaces already in the system.
- The screenshot atlas documents real screens and their current states.
- Humanization docs and journey docs already explain how the system should be read operationally.
- Prior UI consistency and humanization work has already pushed EMS beyond a generic admin template.

## 3. Current Visual Problems

- Some surfaces still feel like generic dashboards instead of EMS-specific operational tools.
- The system needs a clearer institutional identity.
- Role distinction exists, but it can fragment the interface if overdone.
- Some demo and pilot constraints are still visible in the runtime and should be acknowledged honestly, not hidden.
- The print-shop lane needs to feel like an external partner lane, not a fake internal CMU user.

## 4. Desired New Visual Identity

Quiet Institutional Command Center for Exam Operations

Keywords:

- minimal institutional operations
- quiet control
- paper flow intelligence
- exam logistics cockpit
- role-aware governance dashboard
- human-centered audit trail
- subtle Thai university administrative calm
- not generic SaaS
- not flashy AI dashboard

## 5. Role Color System

Suggested role accents should remain restrained, readable, and accessible.

| Role | Purpose | Suggested Accent Color | Where It Should Appear | Accessibility Warning |
|---|---|---|---|---|
| admin | full operational control and oversight | deep indigo or slate blue | role badge, nav accent, hero edge | do not rely on color alone for critical admin-only state |
| staff | daily execution and room operations | teal | work queues, room tasks, staff cards | keep teal dark enough for white text contrast |
| teacher | submission and exam work | warm blue-green or muted cyan | assignment cards, personal work panels | avoid using pale cyan on white backgrounds |
| supervisor | departmental coordination | amber-gold | escalation chips, scoped oversight panels | amber must stay dark enough for text readability |
| executive/governance | policy, audit, and health review | burgundy or dark plum | governance indicators, health score, audit surfaces | ensure it is never used as a decorative-only signal |
| print_shop | external partner queue operations | graphite with copper or rust accent | queue tray, job cards, partner lane | keep the external lane visually separate from CMU roles |
| student | limited lookup / end-user view | forest green or muted green | public entry and student-safe surfaces | do not overuse green for success states everywhere |

## 6. Layout System Requirements

The redesigned system should support these reusable layout patterns:

- AppShell
- PageHero
- Metric strip
- Command/filter bar
- Schedule board
- Workload chart card
- Audit timeline
- Print queue tray
- Empty/loading/error states

## 7. Accessibility Requirements

- Maintain strong contrast on all role colors.
- Preserve keyboard accessibility throughout the app.
- Make focus states obvious and consistent.
- Support Thai text wrapping without layout breakage.
- Do not encode meaning by color alone.
- Keep tables readable on staff and tablet workflows.
- Respect responsive behavior for operations on smaller screens.

## 8. Demo Context

- The demo is not production.
- Faculty LAN / Laravel auth is still pending contract verification.
- Print-shop auth is still pending final ownership and contract decisions.
- The con-1 queue issue is a separate operational topic and should not be mixed into the design story.
- Do not hide blockers in the docs.
- Do not show scary production blockers to normal demo users unless the page is admin/executive facing and the context is explicit.

## 9. Auth / Print Shop Context

- POLSCI OAuth is planned.
- The Laravel callback contract is still pending.
- CMU users should be mapped by `cmu_email` after server-side verification.
- Print-shop users may not have a CMU email.
- Print-shop users must remain a separate limited-access lane.

## 10. What Must Not Be Broken

- existing routes
- i18n
- role permissions
- current dashboard logic
- backend contracts
- current demo flow
- print_shop limitation
- admin / staff / teacher separation

## 11. What Claude Design Should Produce

- A visual direction for the whole system.
- Token recommendations.
- A component system proposal.
- Page-by-page redesign descriptions.
- A demo journey design.
- Implementation phases and sequencing.

## 12. Design Instruction

Before designing, read the attached EMS design reference docs, screenshot atlas, and design context bundle. Do not ignore the existing EMS structure.
