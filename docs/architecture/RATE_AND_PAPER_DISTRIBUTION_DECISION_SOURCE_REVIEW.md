# Rate And Paper Distribution Decision Source Review

**Date**: 2026-06-05
**Current gate**: `PENDING_FINANCE_ADMIN_REVIEW`
**Decision status**: `RATE_AND_SOURCE_CONFIRMED` for draft-output purposes only
**Scope**: Decision-source capture before any official document output/export implementation

## Documents Read

- `docs/architecture/OFFICIAL_2_2568_PAYMENT_SAMPLE_SOURCE_REVIEW.md`
- `docs/operations/OFFICIAL_2_2568_PAYMENT_SUMMARY_SAMPLE_REFERENCE.md`
- `docs/architecture/INVIGILATION_RATE_DECISION_AFTER_2_2568_SAMPLE.md`
- `docs/architecture/INVIGILATION_PAYMENT_DUTY_CATEGORY_MODEL.md`
- `docs/architecture/ADVANCE_BATCH_OFFICIAL_DOCUMENT_OUTPUT_REQUIREMENTS.md`
- `docs/architecture/OFFICIAL_PAYMENT_DOCUMENT_DATA_GAP_AUDIT.md`
- `docs/operations/ADVANCE_BATCH_FINANCE_ADMIN_VALIDATION_PACKET.md`
- `docs/operations/ADVANCE_BATCH_FINANCE_FOLLOWUP_QUESTIONS.md`
- `docs/architecture/EMS_CORRECTED_NEXT_PHASE_ROADMAP.md`

## Current Rate Conflict

| Rate source | Weekday | Weekend | Current status |
|---|---:|---:|---|
| Historical 2/2568 sample transcription | 120 | 200 | User-provided transcription; provenance and authority still pending |
| User draft rate | 150 | 200 | User-stated draft; not confirmed by repository evidence |
| Current active demo/system rate | 300 | 500 | Active local demo/preview configuration; not confirmed as official 2/2568 rate |

Initial capture did not select a rate. A later 2026-06-05 human decision selected `120/200` for the 2/2568 draft-output pass only. The active `300/500` configuration is not changed and must be treated as demo/test data only.

## Paper-Distribution Source Uncertainty

The official-style sample includes two document/payment categories:

- `INVIGILATION_COMMITTEE` / กรรมการคุมสอบ
- `PAPER_DISTRIBUTION_COMMITTEE` / กรรมการจ่ายข้อสอบ

EMS contains operational paper-distribution data, including assignment, schedule-level distributor, historical slot, and pickup evidence sources. However, none has been confirmed as the authoritative payable source for `PAPER_DISTRIBUTION_COMMITTEE`, and the inspected EMS counts do not yet align with the transcribed 2/2568 sample totals.

For the next draft-output pass only, paper-distribution committee counts may be entered or confirmed manually by staff as `MANUAL_INPUT_BY_STAFF`. This manual source is non-persistent draft input and is not final payment authorization.

## 2026-06-05 Draft-Output Decision

- Use `USE_SAMPLE_RATE_120_200_FOR_2_2568`.
- Apply weekday/Monday-Friday `120 THB per person/session`.
- Apply weekend/Saturday-Sunday `200 THB per person/session`.
- Treat rates as term-specific for `2/2568`.
- Treat active `300/500` as demo/test data only.
- Include both `INVIGILATION_COMMITTEE` / กรรมการคุมสอบ and `PAPER_DISTRIBUTION_COMMITTEE` / กรรมการจ่ายข้อสอบ in the in-app draft preview.
- Use staff-confirmed/manual-confirmed paper-distribution counts for draft purposes until an authoritative EMS source is validated.
- Match the 2/2568 sample table grouping by normalized exam date and time slot.
- Do not implement final payment approval, payment authorization, official export, PDF, or Excel output in this pass.

## Decisions Required Before Export Or Document Generation

- Confirm the applicable weekday/weekend rate set for 2/2568 or confirm a term-specific/effective-date rule.
- Confirm whether current active `300/500` remains demo/test only or should be replaced through a controlled configuration action.
- Confirm whether both invigilation and paper-distribution categories use the same weekday/weekend rates.
- Confirm the authoritative source and unit for payable paper-distribution committee counts.
- Confirm whether manual paper-distribution input is allowed when EMS sources are incomplete.
- Confirm whether official output must group by date/time slot exactly like the 2/2568 sample.
- Confirm the reviewer/signatory chain for any future official document draft.
- Obtain approved source evidence or finance/admin sign-off before changing the gate.

## Current Gate And Non-Authorization

- Current gate remains `PENDING_FINANCE_ADMIN_REVIEW`.
- Current decision status is `RATE_AND_SOURCE_CONFIRMED` only for in-app draft preview generation.
- Payment approval/export is not implemented.
- No official Excel/PDF/export output is implemented; only an in-app draft preview is allowed by this decision.
- No active rates are changed.
- This source review does not authorize payment.
