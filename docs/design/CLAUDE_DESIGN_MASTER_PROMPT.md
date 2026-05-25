# Claude Design Master Prompt for EMS

Before designing, read the attached EMS design reference docs, screenshot atlas, and design context bundle. Do not ignore the existing EMS structure.

You are acting as:

- Senior Product Designer
- Design Systems Architect
- UX Strategist
- Frontend Design Engineer
- Accessibility Reviewer
- Institutional System Designer

## Mission

Redesign EMS as a distinctive minimal institutional operations platform for exam management.

## Context

EMS is the Exam Management System for Chiang Mai University Faculty of Political Science and Public Administration.

It handles:

- exam scheduling
- submissions
- workload analytics
- role-based operations
- governance and audit
- operational health
- print queue handling

The platform serves:

- admin
- staff
- teacher
- supervisor
- executive / governance
- print_shop
- student

Faculty LAN / POLSCI OAuth is still pending contract verification.
Print-shop auth is still pending final ownership and contract decisions.
The redesign must stay honest about those realities.

## Visual Direction

Design EMS as a:

Quiet Institutional Command Center for Exam Operations

The UI should feel:

- minimal
- calm
- institutional
- role-aware
- accessible
- authoritative without being flashy
- operational without feeling cluttered
- human and readable for Thai university administration

Do not make it feel like:

- a generic SaaS admin panel
- a neon data dashboard
- a flashy AI cockpit
- a decorative system that hides the real operations

## Design Principles

1. Minimal operational calm.
2. Role-aware color logic.
3. Data before decoration.
4. Accessibility by default.
5. Thai/English first.
6. No bolted-on pages.
7. Human operations, not just analytics.
8. Honest system state.

## Role Color System

Use restrained role accents that remain accessible and easy to scan.

| Role | Suggested Accent |
|---|---|
| admin | deep indigo or slate blue |
| staff | teal |
| teacher | warm blue-green or muted cyan |
| supervisor | amber-gold |
| executive / governance | burgundy or dark plum |
| print_shop | graphite with copper or rust accent |
| student | forest green or muted green |

Rules:

- Use color as a role cue, not as the only meaning channel.
- Maintain contrast for text and chips.
- Keep accents subtle and institutional.

## Page Groups To Redesign

1. Login / auth.
2. Dashboard.
3. Workload analytics.
4. Schedule / exam operations.
5. Teacher workflow.
6. Staff / room operations.
7. Print shop / external partner lane.
8. Governance / audit / health.
9. Import / export.

## Component System

Design or refine these EMS primitives:

- EMSPage
- EMSPageHero
- EMSRoleBadge
- EMSMetricCard
- EMSMetricStrip
- EMSStatusChip
- EMSCommandBar
- EMSFilterBar
- EMSEmptyState
- EMSErrorState
- EMSLoadingSkeleton
- EMSDataTable
- EMSAuditTimeline
- EMSScheduleBoard
- EMSWorkloadChartCard
- EMSQueueTray
- EMSPrintJobCard
- EMSGovernanceSignal
- EMSDemoBanner

## What You Must Respect

- Do not break existing routes.
- Do not redesign auth bridge as if it is already implemented.
- Do not make print shop a fake CMU user.
- Do not ignore Thai language.
- Do not ignore current EMS screenshot evidence.
- Do not hide current demo constraints.
- Do not change the existing EMS route structure in a way that breaks current navigation logic.

## Deliverables You Should Return

1. Design vision summary.
2. Token direction and role color recommendations.
3. Component library spec.
4. Page-by-page redesign plan.
5. Navigation model recommendations.
6. Demo journey design.
7. Figma / implementation prompt pack.
8. Accessibility checklist.
9. Implementation priority and sequencing.

## How To Work

- Start from the attached docs, not from a generic dashboard template.
- Use the screenshot atlas as the visual truth source.
- Treat the capture report as evidence for what is currently broken or incomplete.
- Treat the demo docs as a boundary for what can be honestly claimed.
- Treat the auth docs as provisional where the contract is still pending.

## Output Style

Return a concise but complete design package that helps the next frontend redesign phase.
Be specific about what to preserve, what to simplify, and what to recapture later.
