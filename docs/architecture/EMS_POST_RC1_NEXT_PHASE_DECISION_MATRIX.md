# EMS Post-RC1 Next-Phase Decision Matrix

**Date**: 2026-06-12  
**Selected branch**: `DRAFT_XLSX_FORMAT_ACCEPTED` (updated 2026-06-12, reviewer NOT_PROVIDED)

| Gate result | Next action | Implementation allowed | Status |
|---|---|---|---|
| `HOLD_PENDING_ADDITIONAL_REVIEW` | Run the RC1 demo again and capture an explicit supervisor/finance decision and reviewer identity | No code implementation | SUPERSEDED |
| `DRAFT_XLSX_FORMAT_ACCEPTED` | Define supporting finance roster export and design gate; confirm roster data source | Docs/design only; supporting roster export design | **SELECTED** — 2026-06-12 |
| `DRAFT_XLSX_FORMAT_ACCEPTED_WITH_MINOR_NOTES` | Run a narrow draft-XLSX format-polish pass and revalidate evidence | Draft format changes only; keep non-authorizing | — |
| `DRAFT_XLSX_FORMAT_REVISION_REQUIRED` | Implement the requested draft-XLSX revision and rerun export evidence | Requested draft changes only | — |
| `DRAFT_XLSX_FORMAT_REJECTED` | Prepare a redesign proposal before implementation | No implementation until redesign approval | — |
| `FINAL_AUTHORIZATION_DESIGN_ALLOWED` | Create a docs-only final-authorization workflow model and decision gate | Design only; no payment approval | BLOCKED |
| `SUPPORTING_FINANCE_INVIGILATION_ROSTER_REQUIRED` | Confirm roster data source (5 items), then implement supporting export | Docs/design this pass; implementation after confirmation | **OPENED** — 2026-06-12 |

## Current Routing

The current route is `DRAFT_XLSX_FORMAT_ACCEPTED`. Supporting finance roster design is now open.
Final authorization design remains blocked.

## Exact Next Action

1. Admin/finance confirms 5 open items in `PAYMENT_SUPPORTING_FINANCE_ROSTER_IMPLEMENTATION_GATE.md`
2. Gate updates to `IMPLEMENT_SUPPORTING_ROSTER_EXPORT`
3. Supporting roster backend + frontend + tests pass is executed
4. Final authorization remains a separate blocked gate

## Evidence-Assisted Hold Branch Update (2026-06-12)

The selected branch remains `HOLD_PENDING_ADDITIONAL_REVIEW`. The rerun must use the in-system seven-step checklist and the real RC1 XLSX visual evidence package before requesting an explicit decision. Checklist completion alone does not open another implementation gate.

## Verified Routing After Checklist Recheck (2026-06-12)

- Saved reviewer checklist records: `0`
- Effective completion: `0/7`
- XLSX evidence package: `VERIFIED_COMPLETE_FOR_REVIEW`
- Explicit reviewer decision: `NO`
- Selected branch was `HOLD_PENDING_ADDITIONAL_REVIEW`
- Exact next action was reviewer inspection and explicit decision.

## Decision Recorded (2026-06-12)

- Human decision: `ACCEPT_DRAFT_XLSX_FORMAT`
- Reviewer identity: `NOT_PROVIDED`
- Format gate: `DRAFT_XLSX_FORMAT_ACCEPTED`
- Supporting requirement opened: `SUPPORTING_FINANCE_INVIGILATION_ROSTER_REQUIRED`
- Supporting roster implementation gate: `HOLD_PENDING_OPTIMIZE_ROSTER_SOURCE_CONFIRMATION`
- Final authorization: `FINAL_AUTHORIZATION_DESIGN_BLOCKED` (unchanged)
- No payment approval, no final authorization, no official-final export added.
