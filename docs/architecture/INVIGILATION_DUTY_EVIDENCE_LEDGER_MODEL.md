# Invigilation Duty Evidence Ledger Model

**Date**: 2026-06-02  
**Purpose**: Evidence ledger for post-duty reconciliation, not an automatic pre-payment gate.

## Core Rule

The evidence ledger supports post-duty reconciliation. It does not block initial advance disbursement by default.

Missing check-in creates a reconciliation case. It does not automatically mean the person should not have been included in an initial advance batch.

## Evidence Sources

- Approved invigilation assignment roster.
- Check-in event.
- QR pickup or paper handling evidence.
- Supervisor confirmation.
- Swap/substitution record.
- Admin incident note.
- Absence explanation.
- Finance refund/offset decision.

## Ledger Fields

| Field | Purpose |
|---|---|
| `duty_id` | Links evidence to the duty assignment. |
| `advance_payment_batch_id` | Links duty to an advance payment batch if included. |
| `disbursed_before_reconciliation` | Indicates payment happened before post-duty evidence was closed. |
| `evidence_source` | Check-in, supervisor note, QR, substitution, explanation, finance decision, or other. |
| `evidence_status` | Current evidence review status. |
| `reconciliation_status` | Current post-duty reconciliation state. |
| `explanation_required` | Whether explanation is required. |
| `explanation_received_at` | Timestamp for received explanation. |
| `explanation_document_ref` | Reference to explanation note/document. |
| `force_majeure_flag` | Whether force majeure is claimed or accepted. |
| `refund_required` | Whether refund/offset is required after review. |
| `refund_status` | Refund/offset tracking status. |
| `refund_amount_pending_rule` | Marks refund amount blocked by missing rate/rule. |
| `offset_next_payment_flag` | Whether next payment offset is selected. |
| `finance_review_status` | Finance review and closure state. |

## Audit Rule

Every status change must preserve who changed it, when, what evidence was used, and whether the decision affects refund or offset.

