# Payment Document Review Implementation Source Review

**Date**: 2026-06-08  
**Status**: implementation pass source review  
**Document status preserved**: `DRAFT_NOT_AUTHORIZED`

## Source Docs Read

- `docs/architecture/PAYMENT_DOCUMENT_REVIEW_WORKFLOW_MODEL.md`
- `docs/architecture/PAYMENT_DOCUMENT_CONFIGURABLE_SETTINGS_MODEL.md`
- `docs/architecture/PAYMENT_DOCUMENT_REVIEW_IMPLEMENTATION_DECISION_GATE.md`
- `docs/operations/SUPERVISOR_FINANCE_REVIEW_DECISION_FORM.md`
- `docs/operations/RATE_AND_PAPER_DISTRIBUTION_DECISION_CAPTURE.md`
- `docs/architecture/OFFICIAL_PAYMENT_DOCUMENT_DRAFT_REVIEW_DECISION_GATE.md`
- `docs/operations/OFFICIAL_PAYMENT_DOCUMENT_DRAFT_REVIEW_CHECKLIST.md`
- `docs/architecture/ADVANCE_BATCH_OFFICIAL_DOCUMENT_OUTPUT_REQUIREMENTS.md`
- `docs/architecture/OFFICIAL_PAYMENT_DOCUMENT_DATA_GAP_AUDIT.md`
- `docs/operations/DEMO_LIMITATIONS_AND_DISCLOSURE.md`
- `docs/operations/FINAL_DEMO_READINESS_CERTIFICATE.md`

## Implementation Decision

The prior decision intake accepted the draft format and required a persistent review/comment workflow. This pass implements durable review records and an in-app review panel for the existing official payment document draft page.

Implemented document type for the current page:

- `ADVANCE_PAYMENT_DRAFT_SUMMARY`

Documented future types remain review-model capable but do not create payment approval or final export:

- `PAYMENT_RECONCILIATION_DRAFT`
- `ABSENCE_EXPLANATION_REQUEST`
- `REFUND_OFFSET_TRACKING_DRAFT`

## Safety Boundaries

- `ACCEPTED_FOR_DRAFT_EXPORT` means draft-export workflow design may be considered later; it is not final payment authorization.
- `payment_authorization_enabled` remains `false`.
- `final_export_enabled` remains `false`.
- The review table is separate from draft calculation and payment truth.
- Manual paper-distribution rows remain request-only draft inputs and are not persisted as payable truth.
- No active rate, payment calculation, approval, PDF, Excel, official export, teaching workload, Work H, opencourse, or coinstruc behavior is changed.

## Validation Plan

- Backend compile/import smoke.
- Focused payment-document review router tests.
- Full backend tests, with unrelated failures documented honestly if any.
- Frontend build and required i18n checks.
- Optional browser smoke for `/invigilation-payment-document-draft` if browser access is available.
