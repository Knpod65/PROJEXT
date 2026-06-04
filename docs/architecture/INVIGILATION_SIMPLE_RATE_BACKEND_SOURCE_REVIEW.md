# Invigilation Simple Rate Backend Source Review

**Date**: 2026-06-04  
**Status**: BACKEND-ONLY IMPLEMENTATION REVIEW  
**Scope**: EMS invigilation payment configuration only

## Files Inspected

- `backend/models.py`
- `backend/schemas.py`
- `backend/main.py`
- `backend/routers/invigilation_rate_rules.py`
- `backend/services/invigilation_rate_rule_service.py`
- `backend/services/invigilation_advance_batch_preview_service.py`
- `backend/tests/test_invigilation_rate_rule_service.py`
- `backend/tests/test_invigilation_advance_batch_preview_service.py`
- `backend/auth_utils.py`

## Existing Generic Rate-Rule Behavior

- `InvigilationPaymentRateRule` is persistent SQLAlchemy storage with amount, unit, role/person scopes, lifecycle status, effective dates, and audit fields.
- Existing generic endpoints support listing, draft creation, editing, activation, and archival.
- Current implementation accepts `PER_SESSION` and protects mutations with admin authorization.
- Generic list access uses `require_staff_or_admin`.
- All generic responses already state that payment authorization and final export are disabled.

## Safest Simple-Rate Representation

No schema or table change is required. The existing `role_scope` field can safely identify the two internal configuration records:

- `EMS_SIMPLE_WEEKDAY`
- `EMS_SIMPLE_WEEKEND`

Both records use `person_type_scope = ALL`, `currency = THB`, `payment_unit = PER_SESSION`, and internal `ACTIVE` status. They are configuration records only and do not authorize or calculate payment.

Reserved records will be hidden from the generic list and protected from generic create/update/activate/archive operations. This prevents the simple facade and the compatibility API from mutating the same records through different workflows.

## Authorization Pattern

- `GET /api/invigilation-payment/simple-rates`: `require_staff_or_admin`
- `PUT /api/invigilation-payment/simple-rates`: `require_admin`
- Teacher and print-shop roles fail the staff/admin guard.
- Staff mutation fails the admin guard.

## Backend Files Planned For Modification

- `backend/schemas.py`
- `backend/services/invigilation_rate_rule_service.py`
- `backend/routers/invigilation_rate_rules.py`
- `backend/tests/test_invigilation_rate_rule_service.py`
- `backend/tests/test_invigilation_simple_rate_router.py`

## Explicit Exclusions

- No frontend changes.
- No Advance Batch amount integration.
- No payment calculation, approval, or official export.
- No teaching workload, Work H, `opencourse`, or `coinstruc` logic.

