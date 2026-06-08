# Payment Document Review API Contract

**Date**: 2026-06-08  
**Status**: implemented draft-review persistence contract  
**Authorization boundary**: review records do not authorize payment

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/payment-document-reviews?document_id=&document_type=` | List review records, optionally filtered by document. |
| `GET` | `/api/payment-document-reviews/{document_id}` | List review records for one draft document id. |
| `POST` | `/api/payment-document-reviews` | Create a persistent review/comment record. |
| `PUT` | `/api/payment-document-reviews/{review_id}` | Update an existing review record. |

## Supported Document Types

- `ADVANCE_PAYMENT_DRAFT_SUMMARY`
- `PAYMENT_RECONCILIATION_DRAFT`
- `ABSENCE_EXPLANATION_REQUEST`
- `REFUND_OFFSET_TRACKING_DRAFT`

Current draft page document id pattern:

`ADVANCE_PAYMENT_DRAFT_SUMMARY:{academic_year}:{semester}:{exam_type}:{period_id_or_all}`

## Review Status Values

- `DRAFT_NOT_AUTHORIZED`
- `DRAFT_READY_FOR_REVIEW`
- `UNDER_REVIEW`
- `REVISIONS_REQUESTED`
- `ACCEPTED_FOR_DRAFT_EXPORT`
- `REJECTED_REDESIGN_REQUIRED`
- `FINAL_AUTHORIZATION_REQUIRED`

`ACCEPTED_FOR_DRAFT_EXPORT` is not final authorization. It only records that the draft may proceed to later draft-export workflow design.

## Request Fields

Create requests support:

- `document_id`
- `document_type`
- `term`
- `review_status`
- `comment`
- `decision`
- `prepared_by`
- `revision_required`
- `note`

Update requests support:

- `review_status`
- `comment`
- `decision`
- `revision_required`
- `note`

## Response Fields

Responses include:

- `review_id`
- `document_id`
- `document_type`
- `term`
- `review_status`
- `comment`
- `decision`
- `reviewer_name`
- `reviewer_role`
- `reviewer_user_id`
- `prepared_by`
- `created_at`
- `updated_at`
- `reviewed_at`
- `revision_required`
- `note`
- `payment_authorization_enabled=false`
- `final_export_enabled=false`

## Permission Rules

| Role | List/read | Comment/request review | Set review decisions |
|---|---:|---:|---:|
| `admin` | Yes | Yes | Yes |
| `esq_head` | Yes | Yes | Yes |
| `secretary` | Yes | Yes | Yes |
| `staff` | Yes | Yes, `DRAFT_READY_FOR_REVIEW` only | No |
| `teacher` | No | No | No |
| `print_shop` | No | No | No |
| `student` | No | No | No |

## Non-Authorization Rules

- Review records do not alter official payment draft calculations.
- Review records do not persist manual paper-distribution draft rows as payable truth.
- Review records do not enable payment approval, final authorization, official PDF, Excel, or export.
- `FINAL_AUTHORIZATION_REQUIRED` is a marker for a later separate gate, not an implemented final authorization workflow.
