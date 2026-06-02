# Invigilation Payment Data Readiness Checklist

**Date**: 2026-06-02  
**Status**: PREVIEW ONLY - NOT PAYMENT AUTHORIZATION

| Field | Source | Currently Exists? | Required For Calculation? | Required For Evidence? | Gap | Action |
|---|---|---:|---:|---:|---|---|
| exam_id | `ExamSchedule.id` | Yes | Yes | Yes | None for internal exams | Use as duty ledger anchor |
| course_code | `Section.course.course_id` | Yes | No | Review/export | May be blank for external exams | Define external exam display field |
| section | `Section.section_no` | Yes | No | Review/export | May be blank for external exams | Define fallback for external exams |
| exam_date | `ExamSchedule.exam_date`, `ExternalExam.exam_date` | Yes | Yes | Yes | Date type differs internal/external | Normalize in preview design |
| start_time | `ExamSchedule.exam_time_start`, QR token start, parsed `exam_time` | Partial | Yes if hourly | Yes | Not always normalized | Require normalization audit |
| end_time | `ExamSchedule.exam_time_end`, QR token end, parsed `exam_time` | Partial | Yes if hourly | Yes | Not always normalized | Require normalization audit |
| room_id | `ExamSchedule.room_id`, QR token room | Partial | No | Yes | External exams use room name only | Track as optional with room_name fallback |
| room_name | `Room.room_name`, `ExternalExam.room_name` | Yes | No | Review/export | None | Use for review/export |
| assigned_invigilator_id | `Supervision.user_id`, `ExternalSupervision.user_id` | Yes | Yes | Yes | Paper distributor may be name string | Normalize people source |
| assigned_invigilator_name | `User.full_name`, `paper_distributor` string | Partial | No | Review/export | String-only distributor may not map to user | Require mapping if payable |
| person_type | `User.role` / role group | Partial | Yes if rates vary | No | Role may not equal finance category | Finance must define mapping |
| duty_role | `Supervision.role_in_exam`, pickup role, duty type | Partial | Yes if rates vary | Yes | Role vocabulary not finance-approved | Create role mapping after answers |
| assignment_status | schedule/supervision/swap state | Partial | Yes | Yes | No single canonical assignment status | Define preview status derivation |
| checkin_status | `CheckinEvent`, `ExamPickupCheckin.status` | Partial | Maybe | Yes | Evidence type not confirmed | Keep as evidence candidate |
| checkin_time | `CheckinEvent.checked_in_at`, `ExamPickupCheckin.scanned_at` | Partial | Maybe | Yes | Pickup check-in may not prove invigilation | Finance/admin decision required |
| confirmed_by | `CheckinEvent.confirmations`, QR `confirmed_by`, section manager confirmer | Partial | Maybe | Yes | No single confirmation owner | Define evidence hierarchy |
| substitution_from | `Supervision.baseline_user_id`, `SwapRequest.requester_sup` | Partial | Yes | Yes | Mutation can obscure original owner | Use swap logs plus baseline when available |
| substitution_to | `Supervision.user_id`, `SwapRequest.target_id` | Partial | Yes | Yes | Direct handoff/emergency semantics need policy | Define substitution rule |
| cancellation_status | schedule status / external exam status | Partial | Yes | Yes | No dedicated cancellation field | Add as data gap |
| no_show_flag | None explicit | No | Yes | Yes | Missing invigilator no-show evidence | Add future field or derive only after policy |
| late_flag | None explicit for invigilator | No | Yes | Yes | `late_count` is student late count | Add future field or manual exception input |
| approved_for_payment | None | No | Yes | Yes | Missing approval gate | Add future preview/approval model |
| payment_period | `ExamPeriod` candidate | Partial | Yes | Yes | Exam period may not equal finance period | Finance must confirm period rule |
| rate_code | None | No | Yes | No | Missing rate rule key | Add after rate table decision |
| amount_preview | None | No | Preview only | No | Must not be final amount | Add only after symbolic/approved rules |
| approval_status | None | No | No | Yes | Missing approval workflow | Add after owner decision |
| export_status | Existing export audit only | Partial | No | Yes | No payment export lock status | Add after official output decision |

## Readiness Summary

Current EMS data can support duty inventory and exception discovery. It cannot yet support official payment calculation or final payment export because rule answers, evidence policy, payment period, rate codes, and approval status are missing.

