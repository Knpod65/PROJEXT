# Invigilation Duty Evidence Status Taxonomy

**Date**: 2026-06-02  
**Scope**: Evidence and reconciliation statuses for invigilation advance disbursement.

## Evidence Statuses

| Status | Meaning |
|---|---|
| `NOT_REVIEWED` | Evidence has not been reviewed. |
| `ASSIGNMENT_ONLY` | Approved roster exists; no post-duty evidence reviewed yet. |
| `CHECKIN_CONFIRMED` | Check-in evidence supports attendance. |
| `SUPERVISOR_CONFIRMED` | Supervisor/admin confirmed attendance. |
| `SUBSTITUTION_RECORDED` | A substitute or replacement record exists. |
| `MISSING_CHECKIN` | Check-in is missing and requires reconciliation review. |
| `CONFLICTING_EVIDENCE` | Evidence sources conflict. |
| `EXPLANATION_REQUESTED` | Explanation requested from assigned person. |
| `EXPLANATION_RECEIVED` | Explanation received but not decided. |
| `FINANCE_REVIEW_REQUIRED` | Refund/offset/waiver review is required. |
| `CLOSED` | Evidence and reconciliation are closed. |

## Disbursement Relationship

Evidence statuses are not payment authorization statuses. A duty can be `ASSIGNMENT_ONLY` and still be included in an advance batch if finance/admin policy allows roster-based disbursement.

## Reconciliation Relationship

Missing or conflicting evidence should route the duty to reconciliation instead of deleting the payment record or automatically reversing it.

