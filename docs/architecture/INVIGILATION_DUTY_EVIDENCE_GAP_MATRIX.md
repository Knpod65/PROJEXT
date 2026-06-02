# Invigilation Duty Evidence Gap Matrix

**Date**: 2026-06-02  
**Purpose**: Track evidence data gaps for post-duty reconciliation.

| Evidence / Field | Current Source Candidate | Gap | Impact | Needed Before Advance Batch? | Needed Before Reconciliation Closure? |
|---|---|---|---|---:|---:|
| Approved assignment roster | `Supervision`, `ExamSchedule` | Approval semantics need confirmation | Batch inclusion basis | Yes | Yes |
| Check-in status | `CheckinEvent` | Rule no longer pre-payment gate; still needed after duty | Attendance review | No | Yes |
| Supervisor confirmation | `CheckinEvent.confirmed`, notes | Confirmation owner unclear | May replace missing check-in | No | Yes |
| Substitute record | `SwapRequest`, emergency flags | Finance effect unknown | Original/substitute payee decision | Maybe | Yes |
| No-show flag | Not explicit | Needs new reconciliation field | Absence workflow | No | Yes |
| Explanation document reference | Not explicit | Needs new field/process | Audit evidence | No | Yes |
| Force majeure decision | Not explicit | Needs reviewer and labels | Refund/waiver decision | No | Yes |
| Refund status | Not explicit | Needs tracking model | Finance follow-up | No | Yes |
| Offset next payment | Not explicit | Needs tracking model | Finance follow-up | No | Yes |
| Finance review status | Not explicit | Needs owner/status | Closure control | Yes for approval | Yes |

