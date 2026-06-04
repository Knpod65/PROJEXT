# Official Payment Document Data Gap Audit

**Date**: 2026-06-04
**Scope**: Alignment with the user-transcribed historical 2/2568 official-style summary
**Current gate**: `PENDING_FINANCE_ADMIN_REVIEW`

## Classification Values

- `AVAILABLE`
- `AVAILABLE_FOR_INVIGILATION_ONLY`
- `AVAILABLE_FOR_OPERATIONS_BUT_NOT_VALIDATED_FOR_OFFICIAL_PAYMENT_OUTPUT`
- `MISSING`
- `NEEDS_NEW_SOURCE`
- `NEEDS_MANUAL_INPUT`
- `NEEDS_FINANCE_CONFIRMATION`

## Current Read-Only Evidence

| Evidence source | Current local evidence |
|---|---:|
| Current supervision rows used by Advance Batch preview | 23 |
| Current final 2/2568 paper-distribution assignments | 12 rows / 12 slots |
| Historical final-adjusted invigilator rows | 102 |
| Historical optimized-baseline invigilator rows | 107 |
| Historical distribution slots per snapshot | 16 |
| Schedules with a populated `paper_distributor` | 10 of 91 |
| Transcribed historical sample committee totals | 145 invigilation / 29 paper distribution |

No current or historical inspected EMS source aligns directly with the transcribed sample totals.

## Field And Source Audit

| Requirement | Classification | Current source/evidence | Gap or decision needed |
|---|---|---|---|
| Exam date | `AVAILABLE` | Schedules, assignments, historical snapshots | Normalize CE/BE consistently |
| Time slot | `AVAILABLE` | Schedules, assignments, historical snapshots | Normalize mixed time formats |
| Day type | `AVAILABLE` | Derived from normalized date | Finance confirms classification policy |
| Invigilation roster count | `AVAILABLE_FOR_INVIGILATION_ONLY` | Advance Batch `Supervision`; historical invigilator rows | Select authoritative period/version and reconcile count mismatch |
| Paper-distribution committee count | `AVAILABLE_FOR_OPERATIONS_BUT_NOT_VALIDATED_FOR_OFFICIAL_PAYMENT_OUTPUT` | `PaperDistributionAssignment`, schedule distributor, historical distribution slots, pickup evidence | Confirm payable source, unit, category semantics, and completeness |
| Weekday/weekend rate | `NEEDS_FINANCE_CONFIRMATION` | Historical transcription `120/200`; user-stated draft `150/200`; active local `300/500` | Select approved rate and effective period |
| Category subtotal | `NEEDS_FINANCE_CONFIRMATION` | Derivable after rates, unit, and source are approved | Do not treat derived amount as official yet |
| Grand total | `NEEDS_FINANCE_CONFIRMATION` | Derivable after both category subtotals | Requires approved inputs and validation |
| Reviewer/signature fields | `NEEDS_MANUAL_INPUT` | Response intake template exists | Confirm roles and signatory chain |
| Official memo metadata | `MISSING` | No payment-specific memo/document metadata source found | Define source or manual entry process |
| Original historical sample image | `NEEDS_NEW_SOURCE` | Not present in supplied attachment directory | Obtain original or approved copy |
| Official payment-output authority | `NEEDS_FINANCE_CONFIRMATION` | No approved owner/export rule | Identify verifier, approver, exporter, and signer |

## Paper-Distribution Finding

Paper-distribution assignment data is **not missing**. EMS contains multiple operational sources:

- `PaperDistributionAssignment`
- `ExamSchedule.paper_distributor`
- `HistoricalDistributionSlot`
- QR pickup assignments and check-in evidence
- Existing operational paper-distribution exports

However, these sources are not yet validated as the authoritative payable `PAPER_DISTRIBUTION_COMMITTEE` source. Existing operational exports must not be treated as official payment exports.

## Alignment Blockers

1. Source image/provenance is unavailable.
2. Three rate candidates conflict.
3. The authoritative invigilation period/version is unconfirmed.
4. Paper-distribution payable source and unit are unconfirmed.
5. Current/historical EMS counts do not match the transcribed sample totals.
6. Official metadata, signatories, and export authority are missing.

The historical sample-format document cannot be fully or officially generated until these blockers are closed.
