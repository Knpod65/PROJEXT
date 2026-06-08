# Official Payment Document Draft Review Decision Gate

**Date**: 2026-06-05
**Current status**: `PENDING_SUPERVISOR_FINANCE_REVIEW`
**Draft status**: `DRAFT_NOT_AUTHORIZED`

## Purpose

This gate records the allowed supervisor/finance outcomes after reviewing the in-app 2/2568 official-style payment document draft preview.

The gate does not authorize payment, does not create final truth, and does not permit official PDF/Excel/export until a later authorized process exists.

## Inputs

- Draft preview route: `/invigilation-payment-document-draft`
- Review checklist: `docs/operations/OFFICIAL_PAYMENT_DOCUMENT_DRAFT_REVIEW_CHECKLIST.md`
- Manual smoke result: `docs/architecture/OFFICIAL_PAYMENT_DOCUMENT_DRAFT_MANUAL_SMOKE_RESULTS.md`
- Rate basis for draft: term-specific `120/200` for `2/2568`
- Paper-distribution basis for draft: staff-confirmed/manual-confirmed input until authoritative EMS source validation is complete

## Allowed Outcomes

| Decision | Routing |
|---|---|
| `ACCEPT_DRAFT_FORMAT` | The team may design a later draft export workflow, but this is still not payment authorization, final approval, or official export. |
| `ACCEPT_WITH_CORRECTIONS` | Record corrections in backlog, apply scoped fixes, and re-smoke before any later workflow design. |
| `HOLD_PENDING_DATA_SOURCE` | Validate the authoritative paper-distribution payable source first; do not proceed to export workflow design. |
| `REJECT_DRAFT_FORMAT` | Redesign the draft format before continuing. |

## Non-Authorization Rules

- No final payment approval is created by this gate.
- No payment authorization is created by this gate.
- No official PDF, Excel, or export output is created by this gate.
- No persistent paper-distribution rows are created by this gate.
- No active EMS rates are changed by this gate.
- No teaching workload, Work H, opencourse, or coinstruc logic is in scope.

## Next Human Decision

Supervisor/finance must review the draft table format and decide one of the allowed outcomes. If the paper-distribution source remains unvalidated, the safe route is `HOLD_PENDING_DATA_SOURCE`.

## 2026-06-08 Supervisor / Finance Review Package

The review package is now prepared for non-developer supervisor/finance review:

- `docs/operations/SUPERVISOR_FINANCE_REVIEW_PACKAGE_SOURCE_REVIEW.md`
- `docs/operations/EMS_PAYMENT_DOCUMENT_DRAFT_REVIEW_ONE_PAGER.md`
- `docs/operations/SUPERVISOR_FINANCE_REVIEW_DECISION_FORM.md`
- `docs/operations/SUPERVISOR_FINANCE_REVIEW_TALKING_SCRIPT.md`
- `docs/operations/SUPERVISOR_FINANCE_QUICK_REVIEW_CHECKLIST.md`

Current gate remains `PENDING_SUPERVISOR_FINANCE_REVIEW`. The review package does not record acceptance, does not authorize payment, and does not permit official export.
