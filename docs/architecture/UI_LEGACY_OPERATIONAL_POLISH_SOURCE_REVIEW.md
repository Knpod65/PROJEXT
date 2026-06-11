# UI Legacy Operational Polish Source Review

**Date**: 2026-06-11  
**Scope**: selected non-workload operational P2 presentation drift

## Sources Read

- `UI_DESIGN_SOURCE_RECOVERY_REPORT.md`
- `EMS_AUTHORITATIVE_PAGE_TEMPLATE_STANDARD.md`
- `UI_FULL_ROUTE_TEMPLATE_INVENTORY.md`
- `UI_FULL_ROUTE_DEFECT_BACKLOG.md`
- `UI_FULL_ROUTE_SCREENSHOT_CAPTURE_REPORT.md`
- `UI_NARROW_P2_POLISH_SOURCE_REVIEW.md`
- `UI_NARROW_P2_POLISH_PLAN.md`
- `UI_ROLE_BASED_VISUAL_EVIDENCE_REPORT.md`
- `UI_PAYMENT_EXPORT_SAFETY_VISUAL_AUDIT.md`
- `UI_SYSTEM_ALIGNMENT_VALIDATION_LOG.md`
- `FRONTEND_100_PERCENT_READINESS_SCORE.md`
- demo disclosure and certificate documents

## Selected Safe-Fix Routes

| Route | Main visible drift | Decision |
|---|---|---|
| `/submissions` | Raw English hero, metrics, tabs, table, message, empty, and toast copy | `SAFE_FIX_NOW` |
| `/swaps` | Raw English statuses/actions/modals plus visible mojibake separators | `SAFE_FIX_NOW` |
| `/printreview` | Raw English review, print-readiness, detail, filter, and action copy | `SAFE_FIX_NOW` |
| `/external` | Raw English forms, statuses, assignment preview, metrics, empty states, and toasts | `SAFE_FIX_NOW` |
| `/rooms-v2` | Raw English room, availability, table, modal, slot, and toast copy | `SAFE_FIX_NOW` |
| `/period` | Missing route-level page header, raw lifecycle status/options/actions, weak state presentation | `SAFE_FIX_NOW` |

## Deferred Routes

- Workload routes: `DEFER_WORKLOAD_SCOPE`; no workload presentation or logic edits.
- Analytics, optimizer, optimizer trace, historical schedules, and teacher-specific exam workflow:
  `DEFER_REQUIRES_PRODUCT_DECISION` because their data-heavy states need separate focused passes.
- Attendance, check-ins, workflow, import audit, and exam manager: `NO_ACTION_ACCEPTABLE` for this tranche.

## Planned Frontend Files

- Selected six active route page components.
- Supporting submission, swap, and room modal/table components used only by those routes.
- `frontend/src/i18n/en.ts` and `frontend/src/i18n/th.ts`.

## Safety Boundaries

- No backend, API contract, route, permission, mutation, calculation, payment, export, review, or settings behavior changes.
- No workload, Work H, opencourse, coinstruc, or teaching-workload files.
- Payment/settings pages receive regression verification only.
- Existing shared primitives and styles remain authoritative; no new design system is introduced.

