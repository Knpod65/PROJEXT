# Advance Invigilation Batch Inclusion Rules

**Date**: 2026-06-02  
**Status**: PREVIEW ONLY - NO PAYMENT AUTHORIZATION

## Include In Advance Roster Preview If

- Exam schedule exists.
- Duty assignment exists.
- Assigned person exists.
- Exam date/time exists.
- Room exists, or missing room can be surfaced as a warning for review.
- Duty role exists, or can be marked `UNKNOWN_ROLE`.
- Record is not clearly cancelled before batch.
- Record is not duplicate same person/same slot unless flagged.

## Do Not Require

- Check-in.
- Attendance confirmation.
- Post-duty evidence.
- Explanation letter.
- Refund decision.

## Block Or Flag If

| Condition | Status | Notes |
|---|---|---|
| Missing assigned person | `BLOCKED_MISSING_ASSIGNMENT_DATA` | Cannot identify payee/roster person. |
| Missing exam date/time | `BLOCKED_MISSING_ASSIGNMENT_DATA` | Cannot identify duty slot. |
| Duplicate same person/same time | `BLOCKED_DUPLICATE_DUTY` | Preserve rows but flag duplicate risk. |
| Cancelled before batch | `BLOCKED_RULE_GAP` or warning | Only if status/source clearly indicates cancellation. |
| No duty role | `READY_FOR_BATCH_REVIEW` with warning | Use `UNKNOWN_ROLE`; role/rate still pending. |
| No payment period | `READY_FOR_BATCH_REVIEW` with warning | Rate/period rules still block amount. |
| Unknown person identity | `BLOCKED_MISSING_ASSIGNMENT_DATA` | Cannot build roster line safely. |

## Important

`BLOCKED_RULE_GAP` should be used only when roster inclusion depends on an unanswered admin/finance rule. Missing rate must not block roster inclusion, but it must block amount calculation.

