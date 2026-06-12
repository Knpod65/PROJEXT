# Payment Document In-System Review Checklist Source Review

**Date**: 2026-06-12
**Release candidate**: `EMS_DEMO_REVIEW_RC_1`
**Current human decision**: `HOLD_PENDING_ADDITIONAL_REVIEW`

## Sources Reviewed

- `EMS_SUPERVISOR_FINANCE_DRAFT_XLSX_DECISION_RECORD.md`
- `PAYMENT_DOCUMENT_DRAFT_XLSX_FORMAT_DECISION_GATE.md`
- `EMS_POST_RC1_NEXT_PHASE_DECISION_MATRIX.md`
- `EMS_SUPERVISOR_FINANCE_DEMO_SCRIPT_RC1.md`
- `EMS_PAYMENT_DRAFT_EXPORT_SAFETY_CERTIFICATE.md`
- `PAYMENT_DOCUMENT_DRAFT_EXPORT_IMPLEMENTATION_VALIDATION_LOG.md`
- `PAYMENT_DOCUMENT_DRAFT_EXPORT_API_CONTRACT.md`
- `PAYMENT_DOCUMENT_DRAFT_EXPORT_TEST_MATRIX.md`
- `PAYMENT_DOCUMENT_REVIEW_WORKFLOW_MODEL.md`
- `PAYMENT_DOCUMENT_SETTINGS_DRAFT_INTEGRATION_VALIDATION_LOG.md`
- `DEMO_LIMITATIONS_AND_DISCLOSURE.md`
- `FINAL_DEMO_READINESS_CERTIFICATE.md`
- Existing payment-document review model, service, router, tests, frontend review panel, and gated XLSX export service.

## Current State

- The real gated draft XLSX workflow already exists.
- `ACCEPTED_FOR_DRAFT_EXPORT` permits generation of a review-only draft XLSX.
- No post-RC1 reviewer has accepted the produced XLSX format.
- Reviewer identity remains `NOT_PROVIDED`.
- The format decision gate remains `HOLD_PENDING_ADDITIONAL_REVIEW`.
- Final authorization design remains `FINAL_AUTHORIZATION_DESIGN_BLOCKED`.

## Why An In-System Checklist Is Needed

The external review package explains the workflow, but it does not provide a durable ordered inspection trail beside the draft, review panel, and export gate. Reviewers need one in-system sequence that records which evidence was inspected, what needs attention, and who recorded each result before an explicit format decision is requested.

## Chosen Implementation

Use persistent checklist item records in a table separate from `payment_document_review_records`.

- Seven default checklist items are returned in a fixed order.
- Missing persisted items appear as `NOT_STARTED`.
- Authorized reviewer roles may update item status and comments.
- Staff may read the checklist but may not update it.
- Checklist progress is derived evidence only.
- Checklist completion never changes review status, draft-export eligibility, payment authorization, final export, or the XLSX format decision gate.

## Safety Boundaries

- `DRAFT_NOT_AUTHORIZED` remains visible.
- `payment_authorization_enabled=false`.
- `final_export_enabled=false`.
- Manual paper-distribution rows remain request-only draft input.
- Existing rates, settings, calculations, review records, and draft-export gate logic remain unchanged.
- No final payment approval, final authorization, official-final export, workload, Work H, opencourse, coinstruc, or teaching-workload change is authorized.
