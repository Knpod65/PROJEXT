# Invigilation Refund / Offset Tracking Model

**Date**: 2026-06-02  
**Scope**: Refund or offset tracking after advance invigilation disbursement.

## Refund / Offset Record

| Field | Description |
|---|---|
| `reconciliation_case_id` | Links refund/offset to reconciliation case. |
| `payment_batch_id` | Original advance batch identifier. |
| `person_id` | Person identifier. |
| `person_name` | Person name for review/export. |
| `duty_id` | Original duty assignment. |
| `original_disbursement_reference` | Payment or claim reference if available. |
| `refund_required` | Whether refund/offset is required. |
| `refund_reason` | Reason from reconciliation decision. |
| `refund_amount` | Amount, or `PENDING_RATE_RULE` until rates are confirmed. |
| `refund_amount_status` | Whether amount is known, estimated, pending rule, disputed, or waived. |
| `refund_method` | Cash/transfer/offset/other. |
| `offset_next_payment` | Whether offset will be applied to a later payment. |
| `finance_owner` | Finance owner or office responsible. |
| `finance_status` | Current finance status. |
| `requested_at` | Refund request timestamp. |
| `received_at` | Refund received timestamp. |
| `closed_at` | Closure timestamp. |
| `notes` | Reviewer or finance notes. |

## Refund Statuses

- `NOT_REQUIRED`
- `PENDING_DECISION`
- `REQUIRED_PENDING_REQUEST`
- `REQUESTED`
- `RECEIVED`
- `OFFSET_SCHEDULED`
- `OFFSET_COMPLETED`
- `WAIVED_APPROVED`
- `DISPUTED`
- `CLOSED`

## Important Rule

`refund_amount` may be unavailable until rates are confirmed. If rate rules are missing, keep amount as `PENDING_RATE_RULE` and do not calculate a real amount.

