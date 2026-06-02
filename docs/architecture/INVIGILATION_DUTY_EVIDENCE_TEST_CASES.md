# Invigilation Duty Evidence Test Cases

**Date**: 2026-06-02  
**Status**: Documentation-only; no tests implemented.

| Test ID | Scenario | Evidence behavior | Reconciliation behavior | Status |
|---|---|---|---|---|
| EVD-001 | Assignment included in advance batch before duty | Ledger records `ASSIGNMENT_ONLY` and batch link | Reconciliation remains `NOT_STARTED` until duty date passes | BLOCKED_BY_RULE |
| EVD-002 | Check-in confirmed after advance disbursement | Ledger records `CHECKIN_CONFIRMED` | Case closes as `ATTENDED_CONFIRMED` if reviewer accepts | BLOCKED_BY_RULE |
| EVD-003 | Missing check-in, supervisor confirms attendance | Ledger records `MISSING_CHECKIN` plus `SUPERVISOR_CONFIRMED` | Reviewer may close as attended if policy allows | BLOCKED_BY_RULE |
| EVD-004 | No evidence after duty | Ledger records `MISSING_CHECKIN` | Case becomes `ABSENT_PENDING_EXPLANATION` | BLOCKED_BY_RULE |
| EVD-005 | Explanation accepted as force majeure | Ledger links explanation document | Case becomes `ABSENT_FORCE_MAJEURE_ACCEPTED` or `NO_REFUND_REQUIRED` | BLOCKED_BY_RULE |
| EVD-006 | Refund required but rate unknown | Ledger records finance decision | Refund amount remains `PENDING_RATE_RULE` | BLOCKED_BY_RULE |

