# Invigilation Rate Decision After 2/2568 Sample

**Date**: 2026-06-04
**Decision status**: `NEEDS_RATE_CONFIRMATION_AFTER_SAMPLE`
**Recommended current decision**: `HOLD_FOR_FINANCE_CONFIRMATION`
**Finance validation gate**: `PENDING_FINANCE_ADMIN_REVIEW`

## Rate Evidence

| Candidate | Weekday | Weekend | Evidence |
|---|---:|---:|---|
| `USE_SAMPLE_RATE_120_200` | 120 | 200 | User-provided historical sample transcription; provenance pending |
| `KEEP_DRAFT_RATE_150_200` | 150 | 200 | Prior draft stated by user; not found in repository evidence |
| Current active local EMS configuration | 300 | 500 | Read-only database inspection; demo/preview configuration only |
| `TERM_SPECIFIC_RATE` | TBD | TBD | Requires finance/admin term rule |
| Other approved rule | TBD | TBD | Requires approved source |

## Decision Options

- `USE_SAMPLE_RATE_120_200`
- `KEEP_DRAFT_RATE_150_200`
- `KEEP_CURRENT_ACTIVE_300_500`
- `TERM_SPECIFIC_RATE`
- `OTHER_APPROVED_RATE`
- `HOLD_FOR_FINANCE_CONFIRMATION`

## Explicit Finance/Admin Question

Which rate should EMS use for the current operational preview and future document-output draft?

- `120/200` from the transcribed historical 2/2568 sample
- `150/200` from the user-stated prior draft
- `300/500` from the current active local EMS demo configuration
- A term-specific rate
- Another approved rate

## Current Decision

`HOLD_FOR_FINANCE_CONFIRMATION`

No rate is selected as final, and no active stored configuration is changed in this pass.

## Required Evidence Before Change

- Approved rate source or memo
- Effective term/date rule
- Confirmation whether both duty categories use the same rates
- Authorized finance/admin owner
- Signed response intake or equivalent approved evidence

Changing an active rate remains a separate controlled configuration action. It does not authorize payment or official export.
