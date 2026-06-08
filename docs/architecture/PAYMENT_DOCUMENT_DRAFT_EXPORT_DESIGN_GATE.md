# Payment Document Draft Export Design Gate

**Date**: 2026-06-08
**Status**: `ALLOW_DRAFT_EXPORT_DESIGN` (updated 2026-06-08 after re-evaluation)
**Recommended gate decision**: `ALLOW_DRAFT_EXPORT_DESIGN`

## Purpose

Define the exact conditions, boundaries, formats, warnings, data requirements, and test requirements that must be satisfied before a draft export button or workflow may be designed and implemented for the EMS official payment document.

This document does NOT implement export. It defines the gate.

## Current Export Status

| Field | Value |
|---|---|
| Export implemented | NO |
| Payment approval added | NO |
| Final authorization added | NO |
| Draft export design gate status | `ALLOW_DRAFT_EXPORT_DESIGN` |
| Recommended decision | `ALLOW_DRAFT_EXPORT_DESIGN` |

## Allowed Future Export Concept

Export type: **`DRAFT_EXPORT_ONLY`**

Properties:
- Used for review and administrative preparation only.
- Not final payment authorization.
- Not official finance approval.
- Not payment release.
- Not final payment truth.
- Must carry a clearly visible draft label in both Thai and English on every page/sheet of the output.
- Must include `DRAFT_NOT_AUTHORIZED` in the export metadata and output header.
- Must not trigger or record any approval, authorization, or payment release action.
- Must not persist manual paper-distribution rows as payment truth.

## Allowed Future Export Formats

| Format | Allowed | Notes |
|---|---|---|
| Excel draft (`.xlsx`) | Allowed after gate passes | Must include draft label on every sheet |
| PDF draft | Allowed after gate passes | Must include draft watermark on every page |
| Print-friendly HTML | Allowed after gate passes | Must include draft label in header |
| CSV | Allowed if needed for internal checking only | Must include draft label in first column or header row |
| Official finance export | BLOCKED | Blocked until final authorization gate passes |
| Final payment export | BLOCKED | Blocked until final authorization gate passes |

## Required Document Labels

Every draft export output must display the following labels:

**Thai (primary)**:
`ร่างเอกสารเพื่อการตรวจทานเท่านั้น ยังไม่ใช่เอกสารอนุมัติเบิกจ่าย`

**English (secondary)**:
`Draft for review only. Not payment authorization.`

These labels must appear:
- In the document/file header.
- On every page or sheet.
- As a watermark or prominent banner, not a footnote.
- In the filename or file metadata where technically feasible.

## Required Preconditions Before Implementing Export

All ten conditions below must be met before draft export implementation begins:

| # | Condition | Required Value |
|---|---|---|
| 1 | Settings source status | `CONFIGURED` |
| 2 | Calculation status | `CALCULATED_FROM_SETTINGS` |
| 3 | Document status | `DRAFT_NOT_AUTHORIZED` |
| 4 | Review status | At least `ACCEPTED_FOR_DRAFT_EXPORT` (set by authorized human reviewer) |
| 5 | `payment_authorization_enabled` | `false` |
| 6 | `final_export_enabled` | `false` |
| 7 | Supervisor/finance reviewer comment | Must exist in persistent review records |
| 8 | Paper-distribution responsible source | Must be documented (group/person field populated and confirmed by reviewer) |
| 9 | UI issues | No P0 or P1 issues open |
| 10 | Export output watermark/label | Defined and implemented before export is enabled |

If any of these conditions is not met, export design is blocked.

## Blocked Until Final Authorization

The following items remain blocked and must NOT be implemented as part of any draft export pass:

| Item | Status |
|---|---|
| Official payment export | BLOCKED — requires final authorization gate |
| Final payment approval | BLOCKED — requires separate authorization workflow |
| Payment authorization | BLOCKED — requires separate authorization gate |
| Payment release workflow | BLOCKED — out of current scope |
| Refund/offset final processing | BLOCKED — requires post-duty reconciliation completion |
| Final payment truth record | BLOCKED — requires all above gates |
| Export that bypasses `DRAFT_NOT_AUTHORIZED` | BLOCKED — permanently prohibited in draft path |

## Data That Must Be Included in Draft Export

| Data | Required | Notes |
|---|---|---|
| Academic term | YES | e.g., `ภาคการศึกษาที่ 2/2568` |
| Exam type | YES | |
| Weekday rate from settings | YES | e.g., `120.00 THB` |
| Weekend rate from settings | YES | e.g., `200.00 THB` |
| Paper-distribution responsible group | YES | From confirmed settings |
| Paper-distribution responsible person | If populated | From confirmed settings |
| Invigilation committee counts by date/time slot | YES | |
| Paper-distribution committee counts | YES | Marked as draft/manual source |
| Compensation amounts by category | YES | Calculated from settings rates |
| Grand totals | YES | |
| Document status label | YES | `DRAFT_NOT_AUTHORIZED` |
| Draft warning label | YES | Both Thai and English |
| Review metadata | YES | Reviewer name, role, review status, reviewed_at |
| Preparation timestamp | YES | |
| Settings source reference | YES | Term, settings status |
| Calculation status | YES | `CALCULATED_FROM_SETTINGS` |
| Export generation timestamp | YES | |

## Data That Must NOT Appear in Draft Export

| Data | Reason |
|---|---|
| Final payment authorization reference | Not authorized; must not be implied |
| Official payment approval signature | Not implemented; must not be faked |
| `payment_authorization_enabled = true` | This field must remain false |
| `final_export_enabled = true` | This field must remain false |
| Teaching workload data | Out of scope |
| Active simple demo/test rates | These are not the official draft rates |
| Persisted manual paper-distribution amounts as payable truth | Manual counts are not confirmed payable source |

## Decision Options

| Decision | Meaning |
|---|---|
| `ALLOW_DRAFT_EXPORT_DESIGN` | All 10 preconditions are met; export design may proceed |
| `HOLD_PENDING_REVIEW_ACCEPTANCE` | Human reviewer has not yet set `ACCEPTED_FOR_DRAFT_EXPORT` |
| `HOLD_PENDING_PAPER_SOURCE` | Paper-distribution responsible source is not confirmed |
| `HOLD_PENDING_FORMAT_DECISION` | Export format (Excel/PDF/HTML) decision is pending |
| `REJECT_EXPORT_DESIGN` | Draft format is rejected; redesign required before export planning |

## Current Recommended Decision

**`ALLOW_DRAFT_EXPORT_DESIGN`** (updated 2026-06-08 after re-evaluation pass)

All 10 preconditions passed. Review acceptance captured as review_id 4 with Thai comment and `ACCEPT_FOR_DRAFT_EXPORT_DESIGN` decision by admin reviewer `นางสาว มาธวี เมืองศรี`. Full re-evaluation recorded in `docs/architecture/PAYMENT_DOCUMENT_DRAFT_EXPORT_GATE_REEVALUATION.md`.

## Next Human Action Required

Gate is now open for draft export design. The next action is for the development team to:

1. Implement a backend draft export endpoint per test matrix requirements.
2. Implement a frontend export button/trigger on the draft page.
3. Write and pass all 57 tests in `docs/architecture/PAYMENT_DOCUMENT_DRAFT_EXPORT_TEST_MATRIX.md`.
4. Produce a validation log confirming file formats, safety flags, Thai text rendering, and role blocking.

Official payment export, final authorization, payment approval, and payment release remain blocked pending a separate final authorization gate.

## What This Gate Does NOT Do

- This document does not implement export.
- This document does not authorize payment.
- This document does not change `document_status`, `payment_authorization_enabled`, or `final_export_enabled`.
- This document does not advance any readiness score.
- This document does not substitute for a human reviewer decision.
