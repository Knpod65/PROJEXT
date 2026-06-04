# Advance Batch Preview Amount Validation Log

**Date**: 2026-06-04  
**Result**: PASS  
**Scope**: Preview-only weekday/weekend invigilation amounts

## Decision Gate

- Decision: `ENABLE_ONLY_IF_BOTH_RATES_CONFIGURED`
- Both active simple rates are configured in the local demo database.
- All 23 current assigned duties have exam dates.
- Gregorian and Buddhist Era dates are deterministically classified after BE normalization.

## Implemented Contract

- Ready roster rows receive `PREVIEW_CALCULATED` with numeric `amount_preview`.
- Missing or incomplete rate pairs keep eligible rows `PENDING_RATE_RULE`.
- Missing and invalid dates receive explicit blocked amount statuses.
- Non-ready roster rows receive `BLOCKED_ROSTER_INELIGIBLE`.
- `amount_calculation_enabled = false` remains the official/final-payment safeguard.
- `preview_amount_enabled` identifies preview arithmetic only.
- Payment authorization and final export flags remain `false`.

## Automated Validation

- Focused Advance Batch service/router suite: `18 passed`.
- Backend compileall: PASS.
- Router import smoke: `IMPORT_ROUTERS_ERROR = None`.
- Full backend suite: `1486 passed`.
- Frontend build: PASS.
- i18n parity: PASS, `en=1826`, `th=1826`.
- Raw i18n scan: PASS with existing warning-only heuristic candidates.

## Live Demo Result

Using the current local configured pair of weekday `300 THB` and weekend `500 THB`:

- Total roster rows: `23`
- Preview-calculated rows: `23`
- Weekday duties: `21`
- Weekend duties: `2`
- Pending/blocked amount rows: `0`
- Preview total: `7,300 THB`
- Original Buddhist Era dates remain displayed while normalized dates drive day classification.

These values are validation evidence only and are not hardcoded.

## Genuine Browser Smoke

- Admin page loaded successfully from `/invigilation-advance-batch-preview`.
- Preview-only warning was visible.
- Summary showed `7,300 THB`, 21 weekday duties, 2 weekend duties, and 0 pending/blocked amounts.
- All 23 rows displayed `PREVIEW_CALCULATED`.
- The only page action was Reset; no final approval or official export action appeared.
- Browser console errors: none.
- Role access was covered by backend router tests in this pass; multi-role browser smoke was not rerun.

Screenshot:

- `docs/operations/demo-smoke-screenshots/advance-batch-preview-amounts-admin.png`

## Safety Confirmation

- Final payment calculation implemented: **NO**
- Payment authorization enabled: **NO**
- Final approval/export added: **NO**
- Check-in used as pre-payment gate: **NO**
- Reconciliation logic changed: **NO**
- Production/payment readiness increased: **NO**
