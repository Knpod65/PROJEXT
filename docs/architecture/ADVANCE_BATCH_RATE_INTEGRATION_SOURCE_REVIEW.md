# Advance Batch Rate Integration Source Review

**Date**: 2026-06-04  
**Scope**: Preview-only invigilation amounts

## Sources Read

- `INVIGILATION_SIMPLE_RATE_CONTRACT.md`
- `INVIGILATION_SIMPLE_RATE_BACKEND_VALIDATION_LOG.md`
- `INVIGILATION_SIMPLE_RATE_FRONTEND_VALIDATION_LOG.md`
- `INVIGILATION_RATE_RULE_SIMPLE_DAY_TYPE_MODEL.md`
- `ADVANCE_BATCH_RATE_RULE_INTEGRATION_DECISION.md`
- `ADVANCE_BATCH_PREVIEW_RESPONSE_CONTRACT.md`
- `ADVANCE_BATCH_LIVE_SMOKE_VALIDATION_LOG.md`
- `INVIGILATION_ADVANCE_DISBURSEMENT_MODEL.md`
- `INVIGILATION_POST_DUTY_RECONCILIATION_MODEL.md`

## Current Data Sources

- Advance roster rows come from `ExamSchedule.supervisions`.
- `ExamSchedule.exam_date` is a SQL `Date` and is serialized as ISO text in the preview response.
- The configured preview rates come from the active reserved simple-rate pair:
  - `EMS_SIMPLE_WEEKDAY`
  - `EMS_SIMPLE_WEEKEND`
- The current local demo database has both rates configured, 23 assigned duties, and no missing assignment dates.

## Date Classification Finding

Current data contains both Gregorian dates such as `2026-03-23` and Thai Buddhist Era dates such as `2569-03-23`. Using the stored Buddhist year directly produces the wrong weekday.

The preview classifier must:

- Preserve the original exam date.
- Treat years greater than or equal to `2400` as Buddhist Era and subtract `543`.
- Treat lower years as Gregorian.
- Return an explicit missing or invalid date status when normalization is unsafe.

## Integration Options Reviewed

- Keep all rows `PENDING_RATE_RULE`.
- Calculate partial amounts when one configured rate exists.
- Calculate preview amounts only when both rates are configured.

## Recommendation

Use `ENABLE_ONLY_IF_BOTH_RATES_CONFIGURED`.

- Calculate only `READY_FOR_BATCH_REVIEW` rows.
- Never partially calculate when one rate is missing.
- Keep blocked roster rows out of the preview total.
- Keep `amount_calculation_enabled = false` for official/final payment safety.
- Add `preview_amount_enabled` for preview arithmetic.

## Open Risks And Controls

- Buddhist Era dates require explicit normalization before weekday classification.
- Preview amounts must not be interpreted as payment authorization.
- Rate configuration is global for this preview pass; internal `effective_from` is not applied.
- Check-in and post-duty evidence remain reconciliation inputs and do not affect advance preview amounts.
- Approval, official export, final payment, refund, and offset logic remain out of scope.
