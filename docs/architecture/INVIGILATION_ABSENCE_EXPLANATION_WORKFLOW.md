# Invigilation Absence Explanation Workflow

**Date**: 2026-06-02  
**Scope**: Post-duty absence/no-show explanation for advance invigilation disbursement.

## Workflow

1. Duty is assigned and included in an advance batch.
2. Exam date passes.
3. Attendance, check-in, substitution, and other evidence are reviewed.
4. If attended, mark `ATTENDED_CONFIRMED`.
5. If substituted, mark `SUBSTITUTE_CONFIRMED`.
6. If absent or no evidence, mark `ABSENT_PENDING_EXPLANATION`.
7. Request explanation from the assigned person.
8. Receive explanation and optional document/note.
9. Supervisor/admin reviews explanation.
10. Decide one of: force majeure accepted, no refund required, refund required, offset next payment, further investigation.
11. Record decision and reviewer.
12. Close reconciliation when evidence, decision, and finance status are complete.

## Responsible Roles

| Role | Responsibility |
|---|---|
| Exam office/admin | Trigger reconciliation, request explanation, maintain duty records. |
| Assigned person | Submit explanation or supporting note/document. |
| Supervisor/reviewer | Review attendance and explanation evidence. |
| Finance/admin owner | Decide or execute refund/offset according to approved policy. |
| System auditor/DPO if required | Review audit trail requirements, not payment amounts. |

## Required Fields

- `duty_id`
- `person_id`
- `advance_payment_batch_id`
- `duty_date`
- `room`
- `evidence_status`
- `reconciliation_status`
- `explanation_required`
- `explanation_reason`
- `explanation_document_ref`
- `reviewed_by`
- `review_decision`
- `refund_required`
- `refund_status`
- `offset_next_payment_flag`
- `audit_log_ref`

## Timeline Placeholders

- Explanation request deadline: `TBD_BY_POLICY`.
- Explanation submission deadline: `TBD_BY_POLICY`.
- Review deadline: `TBD_BY_POLICY`.
- Refund/offset deadline: `TBD_BY_FINANCE`.

## Audit Requirements

Each case must preserve assignment, batch inclusion, evidence review, explanation request, explanation receipt, decision, refund/offset status, and closure timestamp.

