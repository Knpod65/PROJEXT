# Payment Document Settings Draft Integration Contract

**Date**: 2026-06-08
**Status**: implemented draft-preview calculation contract

## Inputs

- Draft filters: `period_id`, `academic_year`, `semester`, `exam_type`
- Selected term: `semester/academic_year`, with period metadata fallback
- Saved `PaymentDocumentSettings`
- Eligible invigilation roster rows
- Non-persistent manual paper-distribution rows

## Settings Eligibility

| Source status | Condition | Calculation |
|---|---|---|
| `CONFIGURED` | Complete saved row with status `ACTIVE_FOR_DRAFT_PREVIEW` | Use saved weekday/weekend rates |
| `PENDING_SETTINGS` | Term unresolved or no saved row | Block monetary calculation |
| `INCOMPLETE_SETTINGS` | Inactive/archived status or invalid required field | Block monetary calculation |

Required calculation fields are positive weekday/weekend rates, `THB`, `PER_PERSON_SESSION`, and responsible group. Responsible person and effective dates remain optional.

## Response Contract

Draft metadata includes:

- `settings_source_status`, `settings_term`, `settings_status`
- `settings_weekday_rate`, `settings_weekend_rate`
- `currency`, `payment_unit`
- `paper_distribution_responsible_group`, `paper_distribution_responsible_person`
- `calculation_status`, `settings_issues`

Calculation status values:

- `CALCULATED_FROM_SETTINGS`
- `BLOCKED_PENDING_SETTINGS`
- `BLOCKED_INCOMPLETE_SETTINGS`

When blocked, grouped rows and counts remain visible, but row rates, row amounts, and total amounts are null. No demo/simple-rate fallback is allowed.

## Invariants

- `document_status = DRAFT_NOT_AUTHORIZED`
- `payment_authorization_enabled = false`
- `final_export_enabled = false`
- `supervisor_finance_review_required = true`
- Manual paper rows remain non-persistent.
- Settings do not mutate review records or active simple rates.
