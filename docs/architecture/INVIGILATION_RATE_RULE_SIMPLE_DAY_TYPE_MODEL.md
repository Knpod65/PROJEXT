# Invigilation Rate Rule Simple Day-Type Model

**Date**: 2026-06-04  
**Status**: CONFIGURATION/PREVIEW ONLY  
**Payment authorization**: DISABLED

## Operator Model

The main EMS operator page asks for two user-entered amounts:

- Monday-Friday invigilation rate per duty/session.
- Saturday-Sunday invigilation rate per duty/session.

Currency is fixed to `THB`. Payment unit is fixed to `PER_SESSION`. Operators do not manage rate names, scopes, dates, or lifecycle states through the simplified page.

## Role Behavior

- Admin: view, edit, save, and reset.
- Staff: view-only with read-only inputs.
- Teacher: route and navigation blocked.
- Print shop: route and navigation blocked.

Backend authorization remains authoritative.

## Validation

- Both amounts are required.
- Both amounts must be numeric and finite.
- Both amounts must be greater than zero.
- Invalid values are shown inline and are not sent to the API.

## Safety Boundaries

- Saving configuration does not calculate invigilation payment.
- Saving configuration does not authorize final payment.
- No official payment export is available.
- Advance Batch Preview remains disconnected and `PENDING_RATE_RULE`.
- Generic rate-rule APIs and history remain available for compatibility outside the simplified operator page.

