# Advance Invigilation Batch Preview Test Matrix

**Date**: 2026-06-02  
**Status**: PREVIEW AMOUNTS ONLY - NOT PAYMENT AUTHORIZATION

| Test ID | Input | Expected Advance Inclusion Status | Expected Amount Status | Expected Reconciliation Status | Expected Warning / Blocker |
|---|---|---|---|---|---|
| ADV-001 normal assignment included | Schedule + supervision + user + date/time + room + configured pair | `READY_FOR_BATCH_REVIEW` | `PREVIEW_CALCULATED` | `PENDING_POST_DUTY_RECONCILIATION` | Preview only |
| ADV-002 missing assigned person | Supervision without user | `BLOCKED_MISSING_ASSIGNMENT_DATA` | `BLOCKED_ROSTER_INELIGIBLE` | `PENDING_POST_DUTY_RECONCILIATION` | Missing assigned person |
| ADV-003 missing room | Schedule without room + configured pair | `READY_FOR_BATCH_REVIEW` | `PREVIEW_CALCULATED` | `PENDING_POST_DUTY_RECONCILIATION` | Missing room warning |
| ADV-004 cancelled exam before batch | Schedule status/source indicates cancellation | `BLOCKED_RULE_GAP` | `BLOCKED_ROSTER_INELIGIBLE` | `PENDING_POST_DUTY_RECONCILIATION` | Cancellation handling pending |
| ADV-005 duplicate person same time | Same person/date/time appears twice | `BLOCKED_DUPLICATE_DUTY` | `BLOCKED_ROSTER_INELIGIBLE` | `PENDING_POST_DUTY_RECONCILIATION` | Duplicate duty blocker |
| ADV-006 rate missing but roster eligible | Normal assignment, no rate rule | `READY_FOR_BATCH_REVIEW` | `PENDING_RATE_RULE` | `PENDING_POST_DUTY_RECONCILIATION` | Rate rule gap |
| ADV-007 check-in missing but still included | Normal assignment, no check-in record + configured pair | `READY_FOR_BATCH_REVIEW` | `PREVIEW_CALCULATED` | `PENDING_POST_DUTY_RECONCILIATION` | No check-in blocker |
| ADV-008 substitution already recorded before batch | Supervision `is_swapped` or emergency flag + configured pair | `READY_FOR_BATCH_REVIEW` | `PREVIEW_CALCULATED` | `PENDING_POST_DUTY_RECONCILIATION` | Substitution rule gap |
| ADV-009 payment period missing | Schedule term not mapped to `ExamPeriod` + configured pair | `READY_FOR_BATCH_REVIEW` | `PREVIEW_CALCULATED` | `PENDING_POST_DUTY_RECONCILIATION` | Missing payment period warning |
| ADV-010 batch already approved and locked | Future persisted batch status | `BLOCKED_RULE_GAP` | `PENDING_RATE_RULE` | `PENDING_POST_DUTY_RECONCILIATION` | Not implemented; future case |
| ADV-011 Buddhist Era date | `2569-03-28` + configured pair | `READY_FOR_BATCH_REVIEW` | `PREVIEW_CALCULATED` | `PENDING_POST_DUTY_RECONCILIATION` | Normalize to `2026-03-28` before weekend classification |
| ADV-012 invalid exam date | Unparseable exam date + configured pair | `BLOCKED_MISSING_ASSIGNMENT_DATA` | `BLOCKED_INVALID_EXAM_DATE` | `PENDING_POST_DUTY_RECONCILIATION` | Invalid date blocker |

## Endpoint Validation Update - 2026-06-02

- Backend endpoint validation passed for the local demo data set.
- Default preview response returned 23 roster rows, 23 `READY_FOR_BATCH_REVIEW`, 0 blockers, and 0 warnings.
- All amount fields remained `PENDING_RATE_RULE`.
- Frontend preview page is implemented as read-only; no approve/export/final payment action is present.
- Full payment calculation remains blocked by rate, approval, and reconciliation policy answers.

## Live Smoke Results - 2026-06-02

- `ADV-001`, `ADV-003`, `ADV-006`, `ADV-007`, and `ADV-009` matched the live browser response pattern: 23 rows, `READY_FOR_BATCH_REVIEW`, and `PENDING_RATE_RULE` amounts.
- Admin and staff access passed.
- Teacher and print shop direct access were blocked.
- No final payment or official export controls appeared in the live page.

## Preview Amount Integration Update - 2026-06-04

- Both configured simple rates are required; incomplete or missing rates never partially calculate.
- Ready roster rows receive preview-only amounts selected by normalized weekday/weekend exam date.
- Years greater than or equal to `2400` are normalized from Buddhist Era before classification.
- Blocked roster rows, missing dates, and invalid dates do not enter the preview total.
- Check-in remains outside advance preview eligibility and amount logic.
- Final payment, authorization, approval, and official export remain unimplemented.
