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

## Narrow P2 Role Evidence (2026-06-11)

- Admin evidence shows `DRAFT_NOT_AUTHORIZED`, the review-only draft-export gate, and the restricted draft-export control.
- Staff evidence shows review-comment/request capability and no draft-export control.
- Teacher and print-shop evidence confirms payment-route access remains blocked with a clearer localized explanation.
- Warning copy now states that a review-accepted draft XLSX may be produced while official/final export, payment approval, and final authorization remain disabled.
- Screenshots: `role-admin-payment-draft.png`, `role-admin-draft-export-button.png`, `role-staff-payment-draft.png`, `role-staff-payment-settings-readonly.png`, `role-teacher-payment-blocked.png`, and `role-printshop-payment-blocked.png`.
- Payment/export/review/settings logic changed: `NO`.
