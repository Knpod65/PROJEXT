# Invigilation Simple Rate Contract

**Date**: 2026-06-04  
**Status**: CONFIGURATION ONLY - NOT PAYMENT AUTHORIZATION

## Endpoints

- `GET /api/invigilation-payment/simple-rates`
  - Allowed: admin, staff
  - Blocked: teacher, print shop, and other roles
- `PUT /api/invigilation-payment/simple-rates`
  - Allowed: admin only
  - Blocked: staff, teacher, print shop, and other roles

## Save Request

```json
{
  "weekday_amount": 300,
  "weekend_amount": 500
}
```

Both values are required, numeric, and greater than zero. Currency and payment unit are fixed by the server to `THB` and `PER_SESSION`.

## Response

```json
{
  "preview_only": true,
  "payment_authorization_enabled": false,
  "final_export_enabled": false,
  "currency": "THB",
  "payment_unit": "PER_SESSION",
  "configuration_status": "CONFIGURED",
  "weekday_rate": {
    "day_scope": "WEEKDAY",
    "amount": 300,
    "amount_status": "CONFIGURED",
    "rate_rule_id": 101,
    "saved_at": "2026-06-04T10:00:00Z"
  },
  "weekend_rate": {
    "day_scope": "WEEKEND",
    "amount": 500,
    "amount_status": "CONFIGURED",
    "rate_rule_id": 102,
    "saved_at": "2026-06-04T10:00:00Z"
  }
}
```

When a value is absent, its `amount` is `null` and `amount_status` is `PENDING_CONFIGURATION`.

`configuration_status` values:

- `NOT_CONFIGURED`: neither amount exists.
- `INCOMPLETE`: exactly one amount exists.
- `CONFIGURED`: both amounts exist.

## Persistence And Replacement

- Weekday and weekend records use reserved internal scopes `EMS_SIMPLE_WEEKDAY` and `EMS_SIMPLE_WEEKEND`.
- Each successful save validates both values before mutation.
- The save archives all prior non-archived reserved records and creates one new active pair in one transaction.
- Generic rate rules and their history are preserved.
- Reserved records are internal and cannot be managed through generic rate-rule endpoints.

## Safety Contract

- The facade does not calculate payment.
- The facade does not authorize payment.
- The facade does not create an official export.
- Advance Batch Preview remains unchanged with `PENDING_RATE_RULE` and `amount_calculation_enabled = false`.

