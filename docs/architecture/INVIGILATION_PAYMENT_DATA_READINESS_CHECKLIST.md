# Invigilation Payment Data Readiness Checklist

**Date**: 2026-06-02  
**Status**: PREVIEW ONLY - NOT PAYMENT AUTHORIZATION

Current cross-check statuses:

- `EXISTS`
- `EXISTS_INCOMPLETE`
- `MISSING`
- `CAN_BE_DERIVED`
- `REQUIRES_NEW_FIELD`
- `REQUIRES_APPROVAL`
- `NOT_NEEDED_FOR_CHOSEN_MODEL`

No chosen model exists yet, so no field is marked `NOT_NEEDED_FOR_CHOSEN_MODEL`.

| Field | Source | Current Cross-Check Status | Currently Exists? | Required For Calculation? | Required For Evidence? | Gap | Action |
|---|---|---|---:|---:|---:|---|---|
| exam_id | `ExamSchedule.id` | EXISTS | Yes | Yes | Yes | None for internal exams | Use as future duty ledger anchor after rules are answered. |
| course_code | `Section.course.course_id` | EXISTS_INCOMPLETE | Yes | No | Review/export | May be blank for external exams | Define external exam fallback before final export. |
| section | `Section.section_no` | EXISTS_INCOMPLETE | Yes | No | Review/export | May be blank for external exams | Define fallback before final export. |
| exam_date | `ExamSchedule.exam_date`, `ExternalExam.exam_date` | EXISTS_INCOMPLETE | Yes | Yes | Yes | Date type differs internal/external | Normalize in preview design after model selection. |
| start_time | `ExamSchedule.exam_time_start`, QR token start, parsed `exam_time` | EXISTS_INCOMPLETE | Partial | Yes if hourly | Yes | Not always normalized | Required if per-hour model is selected; otherwise still useful evidence. |
| end_time | `ExamSchedule.exam_time_end`, QR token end, parsed `exam_time` | EXISTS_INCOMPLETE | Partial | Yes if hourly | Yes | Not always normalized | Required if per-hour model is selected; otherwise still useful evidence. |
| room_id | `ExamSchedule.room_id`, QR token room | EXISTS_INCOMPLETE | Partial | No | Yes | External exams use room name only | Track as optional with room_name fallback. |
| room_name | `Room.room_name`, `ExternalExam.room_name` | EXISTS | Yes | No | Review/export | None | Use for review/export after output format is confirmed. |
| assigned_invigilator_id | `Supervision.user_id`, `ExternalSupervision.user_id` | EXISTS | Yes | Yes | Yes | Paper distributor may be name string | Normalize only after payable roles are confirmed. |
| assigned_invigilator_name | `User.full_name`, `paper_distributor` string | EXISTS_INCOMPLETE | Partial | No | Review/export | String-only distributor may not map to user | Requires payable role decision. |
| person_type | `User.role` / role group | EXISTS_INCOMPLETE | Partial | Yes if rates vary | No | Role may not equal finance category | Requires finance role/person-type mapping. |
| duty_role | `Supervision.role_in_exam`, pickup role, duty type | EXISTS_INCOMPLETE | Partial | Yes if rates vary | Yes | Role vocabulary not finance-approved | Requires PAY-003/PAY-012 decisions. |
| assignment_status | schedule/supervision/swap state | CAN_BE_DERIVED | Partial | Yes | Yes | No single canonical assignment status | Derive only after evidence/exception rules are known. |
| checkin_status | `CheckinEvent`, `ExamPickupCheckin.status` | EXISTS_INCOMPLETE | Partial | Maybe | Yes | Evidence type not confirmed | Requires PAY-004/PAY-014 decisions. |
| checkin_time | `CheckinEvent.checked_in_at`, `ExamPickupCheckin.scanned_at` | EXISTS_INCOMPLETE | Partial | Maybe | Yes | Pickup check-in may not prove invigilation | Requires evidence decision. |
| confirmed_by | `CheckinEvent.confirmations`, QR `confirmed_by`, section manager confirmer | EXISTS_INCOMPLETE | Partial | Maybe | Yes | No single confirmation owner | Requires approval/evidence hierarchy. |
| substitution_from | `Supervision.baseline_user_id`, `SwapRequest.requester_sup` | EXISTS_INCOMPLETE | Partial | Yes | Yes | Mutation can obscure original owner | Requires PAY-006 substitution rule. |
| substitution_to | `Supervision.user_id`, `SwapRequest.target_id` | EXISTS_INCOMPLETE | Partial | Yes | Yes | Direct handoff/emergency semantics need policy | Requires PAY-006 substitution rule. |
| cancellation_status | schedule status / external exam status | EXISTS_INCOMPLETE | Partial | Yes | Yes | No dedicated cancellation field | Requires PAY-007; may require new field later. |
| no_show_flag | None explicit | MISSING | No | Yes | Yes | Missing invigilator no-show evidence | Requires PAY-005; likely requires new field or manual exception input. |
| late_flag | None explicit for invigilator | MISSING | No | Yes | Yes | `late_count` is student late count | Requires PAY-008; likely requires new field or manual exception input. |
| approved_for_payment | None | MISSING | No | Yes | Yes | Missing approval gate | Requires PAY-009; future field/workflow needed. |
| payment_period | `ExamPeriod` candidate | EXISTS_INCOMPLETE | Partial | Yes | Yes | Exam period may not equal finance period | Requires PAY-010. |
| rate_code | None | MISSING | No | Yes | No | Missing rate rule key | Requires PAY-002/PAY-003; future field likely needed. |
| amount_preview | None | MISSING | No | Preview only | No | Must not be final amount | Blocked until model/rate/unit decisions. |
| approval_status | None | MISSING | No | No | Yes | Missing approval workflow | Requires PAY-009; future field/workflow needed. |
| export_status | Existing export audit only | EXISTS_INCOMPLETE | Partial | No | Yes | No payment export lock status | Requires PAY-011; future field/workflow likely needed. |

## Readiness Summary

Current EMS data can support candidate duty inventory. It cannot support payment preview implementation because rule decisions are missing. It also cannot support final payment because approval, evidence, rate, exception, and export-lock data are missing or incomplete.

