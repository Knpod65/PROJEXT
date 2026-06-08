# Payment Document Settings Draft Integration Source Review

**Date**: 2026-06-08
**Status**: implementation source review completed

## Sources Read

- `PAYMENT_DOCUMENT_SETTINGS_IMPLEMENTATION_VALIDATION_LOG.md`
- `PAYMENT_DOCUMENT_SETTINGS_API_CONTRACT.md`
- `PAYMENT_DOCUMENT_CONFIGURABLE_SETTINGS_MODEL.md`
- `PAYMENT_DOCUMENT_REVIEW_WORKFLOW_MODEL.md`
- `PAYMENT_DOCUMENT_REVIEW_IMPLEMENTATION_VALIDATION_LOG.md`
- `ADVANCE_BATCH_OFFICIAL_DOCUMENT_OUTPUT_REQUIREMENTS.md`
- `OFFICIAL_PAYMENT_DOCUMENT_DATA_GAP_AUDIT.md`
- `RATE_AND_PAPER_DISTRIBUTION_DECISION_CAPTURE.md`
- `DEMO_LIMITATIONS_AND_DISCLOSURE.md`
- `FINAL_DEMO_READINESS_CERTIFICATE.md`

## Code Findings

- The official draft service previously hardcoded weekday/weekend rates at `120/200`.
- The draft page separately loaded `PaymentDocumentSettings` for display context, but the preview API did not use them.
- Advance-batch roster eligibility is independent from payment-document settings and remains the invigilation count source.
- Manual paper-distribution rows are request-only draft inputs and are not persisted.
- Persistent review records are separate from calculation and remain required.

## Integration Decision

- Resolve settings from the selected term using request filters first and period metadata as fallback.
- Only `ACTIVE_FOR_DRAFT_PREVIEW` settings with complete required fields calculate draft amounts.
- Missing settings return `PENDING_SETTINGS`.
- Inactive, archived, or malformed settings return `INCOMPLETE_SETTINGS`.
- Blocked previews retain grouped duty counts while rate and amount fields are null.
- The draft response carries source status, rates, unit, responsible group/person, calculation status, and issues.

## Safety Boundaries

- Document status remains `DRAFT_NOT_AUTHORIZED`.
- Review workflow and review records remain unchanged.
- Payment authorization and final export flags remain false.
- Active simple rates are not read or changed.
- No PDF, Excel, official export, final truth, approval, or final authorization is added.
- Teaching workload, Work H, opencourse, coinstruc, and check-in gating remain out of scope.
