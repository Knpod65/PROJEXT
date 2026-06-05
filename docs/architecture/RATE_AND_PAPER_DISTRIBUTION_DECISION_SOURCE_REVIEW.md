# Rate And Paper Distribution Decision Source Review

**Date**: 2026-06-05
**Current gate**: `PENDING_FINANCE_ADMIN_REVIEW`
**Decision status**: `DECISION_PENDING`
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

No rate is selected by this pass. The active `300/500` configuration is not changed.

## Paper-Distribution Source Uncertainty

The official-style sample includes two document/payment categories:

- `INVIGILATION_COMMITTEE` / กรรมการคุมสอบ
- `PAPER_DISTRIBUTION_COMMITTEE` / กรรมการจ่ายข้อสอบ

EMS contains operational paper-distribution data, including assignment, schedule-level distributor, historical slot, and pickup evidence sources. However, none has been confirmed as the authoritative payable source for `PAPER_DISTRIBUTION_COMMITTEE`, and the inspected EMS counts do not yet align with the transcribed 2/2568 sample totals.

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
- Current decision status remains `DECISION_PENDING`.
- Payment approval/export is not implemented.
- No official Excel/PDF/payment document output is implemented.
- No active rates are changed.
- This source review does not authorize payment.
