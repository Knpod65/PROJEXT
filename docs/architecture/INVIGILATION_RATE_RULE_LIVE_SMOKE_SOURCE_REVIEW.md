# Invigilation Rate Rule Live Smoke Source Review

**Date**: 2026-06-02  
**Scope**: EMS invigilation payment rate-rule configuration only.

## Docs Read

- `INVIGILATION_RATE_RULE_SETUP_SOURCE_REVIEW.md`
- `INVIGILATION_RATE_RULE_BACKEND_AUDIT.md`
- `INVIGILATION_RATE_RULE_SPEC.md`
- `INVIGILATION_RATE_RULE_FRONTEND_DECISION_GATE.md`
- `ADVANCE_BATCH_RATE_RULE_INTEGRATION_DECISION.md`
- `INVIGILATION_RATE_RULE_SETUP_VALIDATION_LOG.md`
- `INVIGILATION_PAYMENT_PREVIEW_UI_API_ROADMAP.md`
- `EMS_100_PERCENT_MASTER_SCORECARD.md`
- `EMS_100_PERCENT_READINESS_EXECUTIVE_SUMMARY.md`
- `DEMO_LIMITATIONS_AND_DISCLOSURE.md`
- `FINAL_DEMO_READINESS_CERTIFICATE.md`

## Expected Route And API Behavior

- Frontend route: `/invigilation-rate-rules`.
- API routes:
  - `GET /api/invigilation-payment/rate-rules`
  - `POST /api/invigilation-payment/rate-rules`
  - `PUT /api/invigilation-payment/rate-rules/{rate_rule_id}`
  - `POST /api/invigilation-payment/rate-rules/{rate_rule_id}/activate`
  - `POST /api/invigilation-payment/rate-rules/{rate_rule_id}/archive`
- Admin can list, create draft, activate, and archive rate rules.
- Staff can list rate rules but cannot mutate them.
- Teacher and print shop roles must be blocked from rate-rule API access.
- Every rate-rule response must keep:
  - `preview_only = true`
  - `payment_authorization_enabled = false`
  - `final_export_enabled = false`

## Prohibited Behavior

- No final payment calculation.
- No Advance Batch amount integration.
- No final payment approval.
- No official export or payment report.
- No hardcoded rate amount.
- No check-in as a pre-payment gate.
- No teaching workload, Work H, real teaching hours, opencourse, or coinstruc logic.
- No Laravel/POLSCI auth bridge.

## Smoke Plan

1. Confirm EMS root and clean `main`.
2. Confirm backend and frontend local servers are current EMS servers.
3. Log in with documented local demo accounts only.
4. Verify admin list/create/activate/archive.
5. Verify invalid inputs are rejected.
6. Verify staff read-only behavior.
7. Verify teacher and print shop API blocking.
8. Try browser screenshot tooling; if unavailable, document the limitation and do not fabricate screenshots.
9. Record no payment calculation, final approval, or official export was added.

