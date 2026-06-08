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

## Runtime Implementation Update (2026-06-08)

- Persistent review records and an in-app draft review panel are now implemented for `ADVANCE_PAYMENT_DRAFT_SUMMARY`.
- Review records are stored separately from payment calculations and paper-distribution source truth.
- `payment_authorization_enabled=false` and `final_export_enabled=false` remain invariant in review responses.
- Final payment approval, final authorization, official export/PDF/Excel, and production payment readiness remain out of scope.

## Live Smoke Update (2026-06-08)

- Live API and browser smoke confirmed the review panel can store comments and display review history.
- `ACCEPTED_FOR_DRAFT_EXPORT` was tested in the live app and remains non-authorizing.
- No final payment approval, final authorization, official PDF/Excel/export, or final-truth behavior was observed.

## Configurable Settings Update (2026-06-08)

- Term-specific payment-document settings now exist as a separate preparation configuration layer.
- Review status remains separate from settings status; settings do not bypass `DRAFT_NOT_AUTHORIZED` or review history.
- Settings do not authorize payment, final export, official PDF/Excel, or final payment truth.

## Settings-Backed Calculation Update (2026-06-08)

- Active draft settings may now calculate the official draft preview.
- Calculation source status remains separate from review status and cannot bypass review history.
- `ACCEPTED_FOR_DRAFT_EXPORT` remains non-authorizing and does not enable export.
