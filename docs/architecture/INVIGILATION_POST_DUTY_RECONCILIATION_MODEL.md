# Invigilation Post-Duty Reconciliation Model

**Date**: 2026-06-02  
**Scope**: Post-duty reconciliation for EMS invigilation payment only.

## Purpose

Post-duty reconciliation happens after the exam duty date. It verifies the operational truth after an assignment may already have been included in an advance disbursement batch.

The purpose is to:

- Verify who actually invigilated.
- Record substitution or replacement.
- Identify absence/no-show.
- Collect explanation where needed.
- Determine whether absence is accepted.
- Track refund or offset if needed.
- Close the audit trail.

## Reconciliation Statuses

| Status | Meaning |
|---|---|
| `NOT_STARTED` | No post-duty review has started. |
| `ATTENDED_CONFIRMED` | Assigned person attended and evidence is accepted. |
| `SUBSTITUTE_CONFIRMED` | A substitute performed the duty and evidence is accepted. |
| `ABSENT_PENDING_EXPLANATION` | Assigned person appears absent or evidence is missing; explanation needed. |
| `ABSENT_EXPLANATION_RECEIVED` | Explanation was received but not yet decided. |
| `ABSENT_FORCE_MAJEURE_ACCEPTED` | Absence was accepted as force majeure/unavoidable. |
| `ABSENT_NOT_ACCEPTED` | Absence explanation was not accepted. |
| `REFUND_REQUIRED` | Reviewer decided refund is required, amount may still depend on rate rules. |
| `REFUND_REQUESTED` | Refund request has been sent. |
| `REFUND_RECEIVED` | Refund has been received and recorded. |
| `OFFSET_NEXT_PAYMENT` | Refund will be offset against a future payment. |
| `NO_REFUND_REQUIRED` | Reviewer decided no refund is required. |
| `CLOSED` | Reconciliation case is closed with audit trail complete. |

## Explanation Types

- `FORCE_MAJEURE`
- `OFFICIAL_ASSIGNMENT_CONFLICT`
- `ILLNESS`
- `EMERGENCY`
- `SUBSTITUTE_ARRANGED`
- `ADMIN_SCHEDULING_ERROR`
- `UNKNOWN`
- `OTHER`

## Refund Handling Options

- Refund cash/transfer.
- Offset against next payment.
- No refund required due to accepted reason.
- Pending finance decision.

## Decision Safety

The system should not automatically decide refund. It should flag exceptions, collect evidence, and route the case to the responsible reviewer. Refund amounts may remain `PENDING_RATE_RULE` until payment rates are approved.

