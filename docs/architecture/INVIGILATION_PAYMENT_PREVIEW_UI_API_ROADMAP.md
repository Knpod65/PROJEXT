# Invigilation Payment Preview UI/API Roadmap

**Date**: 2026-06-02  
**Status**: PROPOSED ONLY - NOT IMPLEMENTED  
**Scope**: Preview and workflow planning for invigilation payment only.

## Future Pages

All pages are proposed only:

- `PROPOSED` Payment Rules Setup
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
- Teaching workload compensation must not appear in navigation, labels, filters, or export wording.

## API Guardrails

- Preview endpoints must be read-only until approval workflow is implemented.
- Approval/export endpoints must not be implemented until owner decisions are closed.
- All payment preview outputs must include advance batch status, evidence status, reconciliation status, and exception status.
- Existing `export_compensation` must not be treated as final payment export without compatibility and approval tests.
