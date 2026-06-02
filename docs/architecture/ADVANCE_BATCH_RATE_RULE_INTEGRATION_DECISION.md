# Advance Batch Rate Rule Integration Decision

**Date**: 2026-06-02

## Decision

`DEFER_UNTIL_RATE_UI_VALIDATED`

## Reason

Rate-rule setup should be created, tested, and reviewed before Advance Batch Preview displays monetary amounts. This avoids introducing preview calculations before rate configuration, conflict behavior, and admin workflows are validated.

## Current Behavior

- Advance Batch Preview remains unchanged.
- `amount_status = PENDING_RATE_RULE`
- `amount_preview = PENDING_RATE_RULE`
- `amount_calculation_enabled = false`
- No final payment amount is calculated.

## Next Integration Candidate

A later pass may connect an active `PER_SESSION` rate to preview-only advance roster rows. That pass must still avoid final payment approval/export and must keep post-duty reconciliation separate.

