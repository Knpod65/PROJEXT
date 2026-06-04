# Invigilation Payment Preview UI/API Roadmap

**Date**: 2026-06-02  
**Status**: PROPOSED ONLY - NOT IMPLEMENTED  
**Scope**: Preview and workflow planning for invigilation payment only.

## Future Pages

All pages are proposed only:

- `IMPLEMENTED_CONFIGURATION_ONLY` Invigilation Rate Rules Setup
- `PROPOSED` Payment Rules Setup beyond rate configuration
- `PROPOSED` Payment Preview Dashboard
- `PROPOSED` Person Payment Summary
- `PROPOSED` Duty Detail Ledger
- `PROPOSED` Exceptions Review
- `PROPOSED` Approval Queue
- `PROPOSED` Export Center integration
- `PROPOSED` Audit Trail
- `PROPOSED` Advance Payment Batch Preview
- `PROPOSED` Post-Duty Reconciliation Queue
- `PROPOSED` Absence Explanation Tracker
- `PROPOSED` Refund / Offset Tracker
- `PROPOSED` Substitute Confirmation Review

## Future API Endpoints

All endpoints are proposed only:

- `IMPLEMENTED GET /api/invigilation-payment/rate-rules`
- `IMPLEMENTED POST /api/invigilation-payment/rate-rules`
- `IMPLEMENTED PUT /api/invigilation-payment/rate-rules/{rate_rule_id}`
- `IMPLEMENTED POST /api/invigilation-payment/rate-rules/{rate_rule_id}/activate`
- `IMPLEMENTED POST /api/invigilation-payment/rate-rules/{rate_rule_id}/archive`
- `PROPOSED GET /api/invigilation-payment/rules`
- `PROPOSED POST /api/invigilation-payment/preview`
- `PROPOSED GET /api/invigilation-payment/person-summary`
- `PROPOSED GET /api/invigilation-payment/exceptions`
- `PROPOSED POST /api/invigilation-payment/approve`
- `PROPOSED GET /api/invigilation-payment/export`
- `PROPOSED GET /api/invigilation-payment/advance-batches`
- `PROPOSED POST /api/invigilation-payment/advance-preview`
- `PROPOSED GET /api/invigilation-reconciliation/cases`
- `PROPOSED POST /api/invigilation-reconciliation/request-explanation`
- `PROPOSED POST /api/invigilation-reconciliation/record-decision`
- `PROPOSED GET /api/invigilation-reconciliation/refund-offsets`

## Advance Batch Roster Preview

Status: `IMPLEMENTED_BACKEND_PREVIEW_ONLY` after the backend scaffold pass; no frontend page is created in this pass.

Possible page:

- `PROPOSED` Advance Batch Roster Preview

Endpoint:

- `IMPLEMENTED GET /api/invigilation-advance-batch/preview`

Clarifications:

- This is not final payment.
- It calculates no amount.
- Every amount field must remain `PENDING_RATE_RULE`.
- Check-in is not required before advance roster inclusion.
- Post-duty reconciliation remains a separate later workflow.

## Dependencies

- Payment rules answered.
- Data readiness confirmed.
- Approval workflow confirmed.
- Audit policy confirmed.
- Role/rate mapping confirmed.
- Advance roster approval confirmed.
- Post-duty evidence and reconciliation rules confirmed.
- Refund/offset rules confirmed.

## UX Guardrails

- Every preview page must display `PREVIEW ONLY - NOT PAYMENT AUTHORIZATION`.
- No final payable amount should be displayed until finance-approved rules are implemented.
- Advance batch preview and post-duty reconciliation must be separate views.
- Missing check-in must route to reconciliation and must not automatically remove a person from an advance batch.
- Exception lists must be visible before approval.
- Payment export must remain disabled until approval and export-lock rules exist.

## Rate Rule Setup Update

- Rate-rule configuration is implemented as setup only.
- Rate amounts are user-entered and are not hardcoded.
- Active rates do not authorize payment.
- Advance Batch Preview amount integration is deferred until the rate UI/API has been validated.
- Teaching workload compensation must not appear in navigation, labels, filters, or export wording.

## Rate Rule Live Smoke Update

- Authenticated live smoke passed for the rate-rule API/page route on local EMS servers.
- Admin can create, activate, and archive a demo `PER_SESSION` rate rule.
- Staff can read rate rules but mutation is blocked by backend policy.
- Teacher and print shop access is blocked.
- Invalid amount/name/unit submissions are rejected.
- This validates configuration behavior only; Advance Batch amount integration remains deferred and official approval/export remains unimplemented.

## API Guardrails

- Preview endpoints must be read-only until approval workflow is implemented.
- Approval/export endpoints must not be implemented until owner decisions are closed.
- All payment preview outputs must include advance batch status, evidence status, reconciliation status, and exception status.
- Existing `export_compensation` must not be treated as final payment export without compatibility and approval tests.

## Advance Batch Roster Preview Validation - 2026-06-02

- `IMPLEMENTED GET /api/invigilation-advance-batch/preview` with validated demo response.
- `IMPLEMENTED /invigilation-advance-batch-preview` as a preview-only frontend page for `admin` and `staff`.
- The page displays roster rows, blockers, warnings, and rule gaps.
- The page does not include approval, official export, or final payment actions.
- Amounts remain `PENDING_RATE_RULE`; rate rules are still required before any monetary calculation.
- Post-duty reconciliation remains a separate future workflow.

## Live Smoke Update - 2026-06-02

- The advance batch roster preview frontend page is now live and verified in the browser.
- The page remains preview-only and does not change the future payment preview/approval/export roadmap status.
- Post-duty reconciliation is still a separate workflow and is not implemented here.

## Simple Weekday/Weekend Rate Backend Update - 2026-06-04

- `IMPLEMENTED GET /api/invigilation-payment/simple-rates` for admin/staff read access.
- `IMPLEMENTED PUT /api/invigilation-payment/simple-rates` for admin-only save access.
- The backend accepts one weekday and one weekend amount per session, fixed to `THB`.
- The generic rate-rule API remains available for compatibility, while reserved simple-rate records are internally protected.
- The main frontend page is now simplified to two amount inputs and uses the simple-rate facade exclusively.
- Advance Batch Preview remains `PENDING_RATE_RULE`; no payment calculation, authorization, or official export was added.

## Simple Weekday/Weekend Rate Frontend Validation - 2026-06-04

- `/invigilation-rate-rules` now presents only weekday and weekend per-session amounts.
- Admin save and staff read-only behavior passed genuine browser smoke.
- Teacher and print-shop navigation/direct-route blocking passed.
- Invalid zero input was rejected inline; saved `300/500` values persisted after refresh.
- Generic rate-rule lifecycle APIs remain available for compatibility but are no longer the main operator workflow.
- Advance Batch amount integration remains a separate deferred decision.

## Advance Batch Preview Amount Integration - 2026-06-04

- `IMPLEMENTED` preview-only weekday/weekend amounts in `GET /api/invigilation-advance-batch/preview`.
- Both simple rates must be configured before any eligible row is calculated.
- The page shows preview total, weekday/weekend counts, and pending/blocked counts.
- Buddhist Era dates are normalized for day classification while the original date remains visible.
- `amount_calculation_enabled`, payment authorization, final approval, and official export remain disabled.
- Post-duty reconciliation remains separate.

## Official 2/2568 Sample Alignment - 2026-06-04

- A user-transcribed historical official-style sample introduces a future summary grouped by exam date and time slot.
- The future document model requires separate invigilation-committee and paper-distribution-committee counts and subtotals.
- No official output endpoint or page is implemented.
- Existing paper-distribution operational sources require authority and completeness validation before payment use.
- Historical `120/200`, user-stated draft `150/200`, and active local `300/500` rates remain unresolved.
- Approval workflow and official export remain blocked while the gate is `PENDING_FINANCE_ADMIN_REVIEW`.
