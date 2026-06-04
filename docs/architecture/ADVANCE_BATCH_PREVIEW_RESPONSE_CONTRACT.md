# Advance Batch Preview Response Contract

Status: preview-only amount contract for `GET /api/invigilation-advance-batch/preview`.

## Summary

`summary` contains:

- `preview_only`
- `amount_calculation`
- `amount_calculation_enabled`
- `amount_status`
- `preview_amount_enabled`
- `preview_total_amount`
- `preview_weekday_count`
- `preview_weekend_count`
- `total_rows`
- `total_assignments`
- `ready_for_batch_review`
- `included_in_advance_batch`
- `blocked_missing_assignment_data`
- `blocked_duplicate_duty`
- `blocked_rule_gap`
- `blocked_rows`
- `pending_rate_rule_count`
- `missing_exam_date_count`
- `invalid_exam_date_count`
- `blocked_roster_amount_count`
- `warning_count`
- `payment_authorization_enabled`
- `final_export_enabled`

Required invariant:

- `amount_calculation_enabled` must be `false`.
- `preview_amount_enabled` is `true` only when both simple rates are configured.
- `payment_authorization_enabled` and `final_export_enabled` must be `false`.
- `preview_total_amount` includes only ready roster rows with `PREVIEW_CALCULATED`.

## Roster Rows

`roster_rows` contains one row per assigned invigilation duty considered by the advance roster preview.

Important fields:

- `duty_id`
- `exam_id`
- `schedule_id`
- `course_code`
- `course_title`
- `section`
- `exam_date`
- `exam_date_calendar`
- `normalized_exam_date`
- `start_time`
- `end_time`
- `room_name`
- `person_id`
- `person_name`
- `person_type`
- `department`
- `duty_role`
- `advance_inclusion_status`
- `inclusion_reason`
- `blocked_reason`
- `rate_rule_status`
- `amount_status`
- `amount_preview`
- `rate_day_type`
- `rate_source`
- `payment_authorization_status`
- `reconciliation_status`
- `post_duty_evidence_status`
- `warnings`

Required invariants:

- `amount_status` values are `PREVIEW_CALCULATED`, `PENDING_RATE_RULE`, `BLOCKED_MISSING_EXAM_DATE`, `BLOCKED_INVALID_EXAM_DATE`, or `BLOCKED_ROSTER_INELIGIBLE`.
- `amount_preview` is numeric only for `PREVIEW_CALCULATED`; otherwise it is `null`.
- `rate_day_type` values are `WEEKDAY`, `WEEKEND`, or `UNKNOWN`.
- `rate_source` is `SIMPLE_WEEKDAY_WEEKEND_RATE` only for calculated rows.
- `payment_authorization_status` is always `NOT_AUTHORIZED_PREVIEW_ONLY`.
- Missing check-in must not block advance inclusion.
- Reconciliation remains post-duty.

## Date Classification

- Preserve the original `exam_date`.
- A year greater than or equal to `2400` is classified as Buddhist Era and normalized by subtracting `543`.
- A lower year is treated as Gregorian.
- Missing or invalid dates do not receive a preview amount.

## Rate Availability

- Both weekday and weekend simple rates must be configured before any row is calculated.
- An incomplete or missing pair keeps otherwise eligible rows `PENDING_RATE_RULE`.
- Blocked roster rows never receive a preview amount and never enter the preview total.

## Blockers, Warnings, Rule Gaps

- `blockers`: string list of blocking issues found in source rows.
- `warnings`: string list of non-blocking review signals.
- `rule_gaps`: string list of finance/admin rules still required before final payment or unresolved preview behavior.

## Prohibited Claims

The response must not claim:

- official payment approval
- final payable amount
- final report/export readiness
- production payment readiness
