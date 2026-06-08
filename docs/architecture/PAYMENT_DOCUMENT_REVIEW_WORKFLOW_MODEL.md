# Payment Document Review Workflow Model

**Date**: 2026-06-08  
**Status**: model scaffold only  
**Current implementation decision**: `DOCS_ONLY_MODEL_NOW`

## Purpose

Define a review-before-use model for EMS payment-related draft documents. This model supports reviewer comments and decision states without creating final payment authorization, official export, or final payment truth.

## Review Statuses

| Status | Meaning |
|---|---|
| `DRAFT_NOT_AUTHORIZED` | Draft exists but is not authorized for payment, export, or official use. |
| `DRAFT_READY_FOR_REVIEW` | Draft is prepared and ready for supervisor/finance review. |
| `UNDER_REVIEW` | Reviewer is actively checking the draft. |
| `REVISIONS_REQUESTED` | Reviewer requires correction before the draft can proceed. |
| `ACCEPTED_FOR_DRAFT_EXPORT` | Format/content is acceptable for designing a later draft-export workflow; this is not final authorization. |
| `REJECTED_REDESIGN_REQUIRED` | Draft format is rejected and must be redesigned. |
| `FINAL_AUTHORIZATION_REQUIRED` | A later separate authorization gate is required before final payment or official export. |

## Review Fields

| Field | Purpose |
|---|---|
| `document_id` | Stable draft document identifier. |
| `document_type` | Payment-related document type. |
| `term` | Academic term or effective period. |
| `prepared_by` | User/person who prepared the draft. |
| `prepared_at` | Draft preparation timestamp. |
| `reviewer_name` | Reviewer display name. |
| `reviewer_role` | Reviewer role/unit, such as supervisor or finance. |
| `review_status` | One of the review statuses above. |
| `review_comment` | Reviewer comment or requested correction. |
| `reviewed_at` | Review timestamp. |
| `revision_required` | Whether correction is required before proceeding. |
| `decision` | Reviewer decision code. |
| `note` | Additional internal note. |

## Document Types

- `ADVANCE_PAYMENT_DRAFT_SUMMARY`
- `PAYMENT_RECONCILIATION_DRAFT`
- `ABSENCE_EXPLANATION_REQUEST`
- `REFUND_OFFSET_TRACKING_DRAFT`

## Workflow Rules

- Every payment-related document must have a review status before official use.
- Reviewer comments must be stored separately from payment truth and source records.
- `ACCEPTED_FOR_DRAFT_EXPORT` permits design of a later draft-export workflow only; it is not final payment authorization.
- `FINAL_AUTHORIZATION_REQUIRED` is a separate later gate and must not be bypassed.
- Check-in remains post-duty reconciliation evidence and is not a pre-disbursement gate in this model.
- No official PDF/Excel/export is created by this model.

## Out Of Scope

- Runtime API, database, frontend, export, or approval implementation.
- Final payment approval or final authorization.
- Active rate changes.
- Teaching workload, Work H, opencourse, or coinstruc logic.
