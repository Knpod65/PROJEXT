# Invigilation Payment Duty Category Model

**Date**: 2026-06-04
**Status**: DOCUMENT/MODEL ALIGNMENT ONLY
**Finance validation gate**: `PENDING_FINANCE_ADMIN_REVIEW`

## Category Definitions

| Category code | Thai label | Proposed document unit | Current EMS evidence |
|---|---|---|---|
| `INVIGILATION_COMMITTEE` | กรรมการคุมสอบ | Per person/session | `Supervision`, Advance Batch preview, historical invigilator rows |
| `PAPER_DISTRIBUTION_COMMITTEE` | กรรมการจ่ายข้อสอบ | Per person/session | `PaperDistributionAssignment`, schedule distributor, historical distribution slot, pickup evidence |

## `INVIGILATION_COMMITTEE`

- Represents a person assigned to invigilate an exam session.
- Appears in an official-style summary as committee count plus compensation subtotal.
- Current Advance Batch preview covers this category only.
- Check-in is not an advance inclusion gate; post-duty evidence remains reconciliation input.

## `PAPER_DISTRIBUTION_COMMITTEE`

- Represents a person assigned to distribute or hand over exam papers for a date/time slot.
- Appears in the historical sample as committee count plus compensation subtotal.
- Existing EMS operational terminology includes both `paper_distribution` and schedule-level `paper_distributor`.
- Finance/admin must confirm whether the official label `กรรมการจ่ายข้อสอบ` is semantically equivalent to all current EMS paper-distribution sources.
- This category is not currently included in the Advance Batch payment-preview contract.

## Observed Historical Rate Rule

The transcribed sample appears to apply the same weekday/weekend rates to both categories. This is an observation, not an approved current rule.

Finance/admin must confirm:

- Whether both categories use the same rates.
- Whether rates are term-specific.
- Which source determines payable paper-distribution committee count.
- Whether one person/session or one slot is the correct paper-distribution unit.

## Document Arithmetic

- `invigilation_compensation_amount = invigilation_committee_count × approved_day_type_rate`
- `paper_distribution_compensation_amount = paper_distribution_committee_count × approved_day_type_rate`
- `total_compensation_amount = invigilation_compensation_amount + paper_distribution_compensation_amount`

These formulas define the historical document shape only. They must not be implemented as official payment logic until finance/admin confirms the rates, units, and source records.
