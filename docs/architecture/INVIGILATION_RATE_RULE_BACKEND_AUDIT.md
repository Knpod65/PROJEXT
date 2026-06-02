# Invigilation Rate Rule Backend Audit

**Date**: 2026-06-02  
**Scope**: Backend implementation path for invigilation payment rate-rule configuration.

## Current Backend Pattern

- Routers live under `backend/routers/` and are registered in `backend/main.py`.
- Business logic is commonly placed under `backend/services/`.
- Pydantic response/request schemas are currently centralized in flat `backend/schemas.py`.
- Persistence uses SQLAlchemy models in `backend/models.py`.
- Local development can create new tables through `Base.metadata.create_all(bind=engine)` when startup mutation is deliberately enabled. Production migration/deployment is out of scope.

## Existing Related Implementation

- `backend/routers/invigilation_advance_batch.py` exposes preview-only advance roster data.
- `backend/services/invigilation_advance_batch_preview_service.py` explicitly avoids amount calculation and check-in gating.
- `backend/tests/test_invigilation_advance_batch_preview_service.py` verifies preview-only behavior and `PENDING_RATE_RULE` output.

## Recommended Implementation Path

- Add `InvigilationPaymentRateRule` to `backend/models.py`.
- Add schemas to `backend/schemas.py`.
- Add `backend/services/invigilation_rate_rule_service.py`.
- Add `backend/routers/invigilation_rate_rules.py`.
- Register the router in `backend/main.py` with prefix `/api/invigilation-payment`.
- Use `require_staff_or_admin` for read and `require_admin` for create/update/activate/archive.

## Risks And Controls

- **Risk**: Rate setup could be mistaken for payment authorization.  
  **Control**: All API responses include `preview_only = true`, `payment_authorization_enabled = false`, and `final_export_enabled = false`.
- **Risk**: Conflicting active rates create ambiguous preview calculations later.  
  **Control**: Activation rejects overlapping active rules with the same payment unit, role scope, and person type scope.
- **Risk**: Future code accidentally pulls legacy `Supervision.compensation`.  
  **Control**: This pass does not integrate with advance batch amounts and does not read existing compensation fields.

