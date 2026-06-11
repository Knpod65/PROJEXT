# UI Payment And Export Safety Visual Audit

**Date**: 2026-06-11  
**Status**: `LIVE_VISUAL_VALIDATION_PASSED`

## Required State

| Safety item | Expected |
|---|---|
| Document status | `DRAFT_NOT_AUTHORIZED` remains prominent |
| Draft XLSX | Gated by `ACCEPTED_FOR_DRAFT_EXPORT`, review-only |
| Official/final export | Absent |
| Payment approval | Absent |
| Final authorization | Absent |
| Review workflow | Required and visible |
| Settings source/calculation status | Visible and localized |
| Blocked export reason | Visible, not tooltip-only |
| `payment_authorization_enabled` | `false` |
| `final_export_enabled` | `false` |

## Code Review Result

- The existing draft export trigger and gate logic were not changed.
- The page now explains the gate in a visible banner and distinguishes draft XLSX from official/final export.
- Raw review/settings/calculation enums are mapped to localized display labels.
- `ACCEPTED_FOR_DRAFT_EXPORT` remains non-authorizing.
- No approval, official-final export, or final authorization control was added.

## Live Visual Result

- Evidence: `docs/operations/demo-smoke-screenshots/full-ui-audit-invigilation-payment-document-draft.png`
- `DRAFT_NOT_AUTHORIZED`: visible.
- Localized settings/calculation/review status labels: visible; raw `CALCULATED_FROM_SETTINGS` and `ACTIVE_FOR_DRAFT_PREVIEW` are not visible.
- Draft-export gate banner: visible.
- `ACCEPTED_FOR_DRAFT_EXPORT` is displayed as a draft-export review status, not payment approval.
- Final payment approval button: absent.
- Official/final export control: absent.
- Backend safety invariants and gate logic: unchanged.
