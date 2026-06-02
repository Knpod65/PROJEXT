# Invigilation Rate Rule Spec

**Date**: 2026-06-02  
**Status**: CONFIGURATION ONLY - NOT PAYMENT AUTHORIZATION

## Fields

- `rate_rule_id`
- `rate_name`
- `payment_unit`
- `rate_amount`
- `currency`
- `role_scope`
- `person_type_scope`
- `effective_from`
- `effective_to`
- `status`
- `created_by`
- `created_at`
- `updated_by`
- `updated_at`
- `activated_by`
- `activated_at`
- `archived_by`
- `archived_at`
- `note`

## Supported Values

Payment unit options:

- `PER_SESSION` - supported in this implementation.
- `PER_HOUR` - reserved for future rule expansion.
- `PER_DAY` - reserved for future rule expansion.
- `CUSTOM` - reserved for future rule expansion.

Status options:

- `DRAFT`
- `ACTIVE`
- `ARCHIVED`

Default scope values:

- `role_scope = ALL`
- `person_type_scope = ALL`
- `currency = THB`

## Validation Rules

- `rate_name` is required.
- `payment_unit` is required.
- `rate_amount` is required and must be positive.
- Current implementation accepts `PER_SESSION` only.
- `effective_from` is required before activation.
- `effective_to` is optional, but must not be earlier than `effective_from`.
- Archived records cannot be edited or activated.
- Activation rejects overlapping active rules with the same payment unit, role scope, and person type scope.

## Safety Rules

- Creating a rate does not authorize payment.
- Activating a rate does not authorize final payment.
- Draft and archived rates do not enable calculation.
- Only an active rate may be eligible for a later preview-calculation integration.
- Advance Batch Preview remains `PENDING_RATE_RULE` until a separate integration pass.

