# UI System Alignment Source Review

**Date**: 2026-06-05  
**Scope**: EMS frontend visual consistency pass  
**Status**: implementation alignment in progress

## Sources Read

- `docs/architecture/UX_UI_HUMANIZATION_AUDIT.md`
- `docs/architecture/FRONTEND_SUPERIOR_ENGINEER_AUDIT.md`
- `docs/architecture/EMS_FULL_SYSTEM_SUPERIOR_DEVELOPER_REVIEW.md`
- `docs/humanization/screenshot-atlas/major-pages.md`
- `docs/humanization/screenshot-atlas/SCREENSHOT_CAPTURE_REPORT.md`
- `docs/architecture/UI_DIRTY_TREE_RESOLUTION_REPORT.md`
- `docs/architecture/UI_RESIDUAL_AUDIT_EXPLORER_HOTFIX_REPORT.md`
- `docs/architecture/INVIGILATION_RATE_RULE_SIMPLE_DAY_TYPE_MODEL.md`
- `docs/architecture/ADVANCE_BATCH_PREVIEW_AMOUNT_VALIDATION_LOG.md`
- `docs/architecture/ADVANCE_BATCH_OFFICIAL_DOCUMENT_OUTPUT_REQUIREMENTS.md`
- `docs/architecture/OFFICIAL_PAYMENT_DOCUMENT_DRAFT_VALIDATION_LOG.md`
- `docs/architecture/OFFICIAL_PAYMENT_DOCUMENT_DRAFT_MANUAL_SMOKE_RESULTS.md`
- `docs/operations/DEMO_LIMITATIONS_AND_DISCLOSURE.md`
- `docs/operations/FINAL_DEMO_READINESS_CERTIFICATE.md`

Missing requested historical sources:

- `docs/architecture/UI_UX_CONSISTENCY_REPORT.md`
- `docs/architecture/EMS_DESIGN_CONSISTENCY_CHECKLIST.md`

## Current Visual Problems

- Several newer payment pages already use EMS primitives but still had raw input/grid utility classes.
- Some governance and audit surfaces used ad hoc white cards, Tailwind-like utility classes, or hand-written tables.
- Document/payment pages needed a stronger shared safety banner pattern to prevent final-payment misunderstanding.
- Some table columns combined multiple official document concepts into one column, reducing similarity to the 2/2568 sample table.
- Platform/configuration and staff availability pages had inconsistent first-screen hierarchy.

## Affected Feature Areas

- Payment/document draft preview.
- Advance batch preview.
- Invigilation rate configuration.
- Audit and governance review pages.
- Operational health and platform configuration.
- Staff availability and export center surfaces.

## Safety Boundaries

- Payment approval added: NO.
- Final payment authorization added: NO.
- Official export, PDF, or Excel added: NO.
- Payment calculation or rate logic changed: NO.
- Advance batch inclusion logic changed: NO.
- Auth bridge or Laravel integration changed: NO.
- Teaching workload / Work H / opencourse / coinstruc touched: NO.

## Target UI Direction

Use one minimal institutional EMS page pattern: shared page hero, status/safety banner, section cards, summary cards, wrapped tables, consistent form fields, and status chips. Reuse the existing EMS primitives first and add only tiny wrappers where they reduce repetition.

