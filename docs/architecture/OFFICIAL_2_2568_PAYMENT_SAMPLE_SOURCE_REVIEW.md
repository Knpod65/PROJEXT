# Official 2/2568 Payment Sample Source Review

**Date**: 2026-06-04
**Current gate**: `PENDING_FINANCE_ADMIN_REVIEW`
**Evidence status**: `USER_PROVIDED_TRANSCRIPTION_PENDING_PROVENANCE_VERIFICATION`

## Documents And Sources Read

- `docs/operations/ADVANCE_BATCH_FINANCE_ADMIN_VALIDATION_PACKET.md`
- `docs/operations/ADVANCE_BATCH_FINANCE_VALIDATION_RESPONSE_INTAKE.md`
- `docs/architecture/ADVANCE_BATCH_FINANCE_VALIDATION_DECISION_GATE.md`
- `docs/operations/ADVANCE_BATCH_PREVIEW_CORRECTION_BACKLOG.md`
- `docs/operations/ADVANCE_BATCH_FINANCE_FOLLOWUP_QUESTIONS.md`
- `docs/architecture/INVIGILATION_RATE_RULE_SIMPLE_DAY_TYPE_MODEL.md`
- `docs/architecture/INVIGILATION_ADVANCE_DISBURSEMENT_MODEL.md`
- `docs/architecture/INVIGILATION_POST_DUTY_RECONCILIATION_MODEL.md`
- `docs/architecture/ADVANCE_BATCH_PREVIEW_RESPONSE_CONTRACT.md`
- `docs/architecture/ADVANCE_BATCH_RATE_RULE_INTEGRATION_DECISION.md`
- `docs/architecture/ADVANCE_BATCH_PREVIEW_AMOUNT_VALIDATION_LOG.md`
- `docs/operations/ADVANCE_BATCH_PREVIEW_VALIDATION_SNAPSHOT.md`
- `docs/architecture/INVIGILATION_PAYMENT_PREVIEW_UI_API_ROADMAP.md`
- Read-only local EMS database evidence from `backend/ems.db`
- User-provided transcription of a historical official-style 2/2568 summary

## Provenance Boundary

The historical sample image is not present in the provided attachment directory. This pass therefore records the supplied values as a user-provided transcription pending source-image and provenance verification. It must not be described as independently verified official evidence.

## Transcribed Historical Sample

- Title: `สรุปจำนวนกรรมการและค่าตอบแทน รายวัน/ช่วงเวลา`
- Term: `ภาคการศึกษาที่ 2/2568`
- Weekday rate: `120 THB/person/session`
- Weekend rate: `200 THB/person/session`
- Invigilation committee count: `145`
- Invigilation compensation: `20,280 THB`
- Paper-distribution committee count: `29`
- Paper-distribution compensation: `3,960 THB`
- Grand total: `24,240 THB`

Two payment/document categories appear:

- `INVIGILATION_COMMITTEE` / `กรรมการคุมสอบ`
- `PAPER_DISTRIBUTION_COMMITTEE` / `กรรมการจ่ายข้อสอบ`

## Arithmetic Consistency Check

The supplied totals are arithmetically consistent with the transcribed `120/200` rates:

- Invigilation: 109 weekday duties and 36 weekend duties imply `109 × 120 + 36 × 200 = 20,280 THB`.
- Paper distribution: 23 weekday duties and 6 weekend duties imply `23 × 120 + 6 × 200 = 3,960 THB`.
- Combined: `20,280 + 3,960 = 24,240 THB`.

These weekday/weekend mixes are inferred from aggregate totals. They cannot be row-level verified without the original table.

## Three-Way Rate Conflict

| Rate source | Weekday | Weekend | Evidence status |
|---|---:|---:|---|
| Historical 2/2568 sample transcription | 120 | 200 | User-provided transcription pending provenance verification |
| Prior draft stated by user | 150 | 200 | Not found in repository evidence |
| Current active local EMS configuration | 300 | 500 | Verified by read-only local database inspection |

No rate is selected or changed by this pass. Recommended current decision is `HOLD_FOR_FINANCE_CONFIRMATION`.

## Current EMS Data Evidence

- Current Advance Batch source: 23 supervision rows.
- Current final 2/2568 paper-distribution source: 12 assignment rows across 12 slots.
- Historical final-adjusted snapshot: 102 invigilator rows and 16 distribution slots.
- Historical optimized-baseline snapshot: 107 invigilator rows and 16 distribution slots.
- Schedule-level `paper_distributor` is populated on 10 of 91 schedules.

EMS has paper-distribution operational data. However, no inspected source aligns with the transcribed historical totals of 145 invigilation committee duties and 29 paper-distribution committee duties.

## Recommendation

- Keep `PENDING_FINANCE_ADMIN_REVIEW`.
- Confirm the authoritative rate set and whether rates are term-specific.
- Confirm which EMS source represents payable paper-distribution committee duties.
- Obtain the original image/document or another approved row-level source.
- Do not change active rates, preview calculation, payment authorization, approval, or export behavior.
