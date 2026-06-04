# Invigilation Simple Rate Frontend Source Review

**Date**: 2026-06-04  
**Status**: FRONTEND SIMPLIFICATION REVIEW  
**Scope**: EMS invigilation-rate configuration only

## Files Inspected

- `frontend/src/pages/InvigilationRateRules.tsx`
- `frontend/src/services/invigilationRateRules.service.ts`
- `frontend/src/hooks/domain/useInvigilationRateRules.ts`
- `frontend/src/types/invigilationRateRules.ts`
- `frontend/src/App.tsx`
- `frontend/src/config/navigation.ts`
- `frontend/src/i18n/en.ts`
- `frontend/src/i18n/th.ts`
- `docs/architecture/INVIGILATION_SIMPLE_RATE_CONTRACT.md`
- `docs/architecture/INVIGILATION_SIMPLE_RATE_BACKEND_VALIDATION_LOG.md`

## Current Complex UI

The existing page exposes generic rate-rule lifecycle concepts: rate name, payment unit, currency, role and person scopes, effective dates, note, draft creation, editing, activation, archival, and a generic rules table.

Those controls are broader than the current EMS business rule and will be removed from the visible page. Existing generic frontend clients remain available for compatibility but will no longer be called by this page.

## Target Simple UI

- Exactly two amount inputs: Monday-Friday and Saturday-Sunday.
- Fixed display values: `THB`, `PER_SESSION`, and baht per session.
- Admin can edit, save, and reset.
- Staff can view selectable read-only values and sees a read-only badge.
- Teacher and print shop remain blocked by the existing route and navigation guards.
- Configuration state, amount state, and latest saved timestamp remain visible.
- No calculation, approval, official export, or Advance Batch integration appears.

## API Contract

- `GET /api/invigilation-payment/simple-rates`
- `PUT /api/invigilation-payment/simple-rates`

The PUT body contains only `weekday_amount` and `weekend_amount`. Both must be numeric, finite, and greater than zero.

## Frontend Files Planned For Modification

- `frontend/src/pages/InvigilationRateRules.tsx`
- `frontend/src/services/invigilationSimpleRates.service.ts`
- `frontend/src/hooks/domain/useInvigilationSimpleRates.ts`
- `frontend/src/types/invigilationSimpleRates.ts`
- `frontend/src/config/navigation.ts`
- `frontend/src/i18n/en.ts`
- `frontend/src/i18n/th.ts`

Backend files and Advance Batch files are explicitly excluded.

