# Payment Document Draft Export Gate — Source Review

**Date**: 2026-06-08
**Status**: source review completed
**Gate decision input**: `HOLD_PENDING_REVIEW_ACCEPTANCE`

## Source Documents Read

| Document | Location |
|---|---|
| `PAYMENT_DOCUMENT_SETTINGS_DRAFT_INTEGRATION_VALIDATION_LOG.md` | `docs/architecture/` |
| `PAYMENT_DOCUMENT_SETTINGS_DRAFT_INTEGRATION_CONTRACT.md` | `docs/architecture/` |
| `PAYMENT_DOCUMENT_REVIEW_WORKFLOW_MODEL.md` | `docs/architecture/` |
| `PAYMENT_DOCUMENT_REVIEW_IMPLEMENTATION_VALIDATION_LOG.md` | `docs/architecture/` |
| `PAYMENT_DOCUMENT_SETTINGS_IMPLEMENTATION_VALIDATION_LOG.md` | `docs/architecture/` |
| `ADVANCE_BATCH_OFFICIAL_DOCUMENT_OUTPUT_REQUIREMENTS.md` | `docs/architecture/` |
| `OFFICIAL_PAYMENT_DOCUMENT_DATA_GAP_AUDIT.md` | `docs/architecture/` |
| `PAYMENT_DOCUMENT_SETTINGS_API_CONTRACT.md` | `docs/architecture/` |
| `SUPERVISOR_FINANCE_REVIEW_DECISION_FORM.md` | `docs/operations/` |
| `OFFICIAL_PAYMENT_DOCUMENT_DRAFT_REVIEW_CHECKLIST.md` | `docs/operations/` |
| `DEMO_LIMITATIONS_AND_DISCLOSURE.md` | `docs/operations/` |
| `FINAL_DEMO_READINESS_CERTIFICATE.md` | `docs/operations/` |

## Current Settings-Backed Draft Status

Confirmed live API metadata as of 2026-06-08 (commit `b448799`):

| Field | Value |
|---|---|
| `settings_source_status` | `CONFIGURED` |
| `settings_status` | `ACTIVE_FOR_DRAFT_PREVIEW` |
| `settings_weekday_rate` | `120.00` |
| `settings_weekend_rate` | `200.00` |
| `calculation_status` | `CALCULATED_FROM_SETTINGS` |
| `document_status` | `DRAFT_NOT_AUTHORIZED` |
| `payment_authorization_enabled` | `false` |
| `final_export_enabled` | `false` |

Active term `2/2568` settings are fully configured. Calculation is driven by term-specific settings, not hardcoded or demo rates. Missing/incomplete settings block monetary fields without using fallback demo rates. Manual paper-distribution rows remain non-persistent.

## Current Review Workflow Status

- Persistent review records and an in-app draft review panel are implemented for `ADVANCE_PAYMENT_DRAFT_SUMMARY`.
- Live smoke confirmed the panel can store comments, display review history, and show `ACCEPTED_FOR_DRAFT_EXPORT` as a non-authorizing status.
- Role smoke confirmed: admin can set review status including `ACCEPTED_FOR_DRAFT_EXPORT`; staff is limited to preparer/comment role; teacher and print shop are blocked from the review API.
- `ACCEPTED_FOR_DRAFT_EXPORT` permits design of a later draft-export workflow only. It is not final payment authorization and does not enable export.
- `FINAL_AUTHORIZATION_REQUIRED` as a separate later gate has not been bypassed.
- `payment_authorization_enabled=false` and `final_export_enabled=false` remain invariant in all review API responses.

Current review status for export design: **not yet at `ACCEPTED_FOR_DRAFT_EXPORT`**. A human reviewer must explicitly set this status before export design may proceed.

## Export Readiness Blockers

| Blocker | Status |
|---|---|
| Review status at least `ACCEPTED_FOR_DRAFT_EXPORT` | NOT YET — pending human reviewer action |
| Supervisor/finance reviewer comment recorded | NOT YET — pending human review completion |
| Paper-distribution authoritative source confirmed | NOT YET — source remains undocumented payable truth |
| Export output format decision | NOT YET — Excel/PDF/HTML decision pending |
| Export output watermark/label defined | NOT YET — label wording defined in gate doc, not yet implemented |
| P0/P1 UI issues | NONE — current UI QA state is `HUMAN_VISUAL_QA_PASSED_ACCEPTED_FOR_SUPERVISOR_REVIEW` |

No export implementation may begin while any of the above blockers remain unresolved.

## Safety Boundaries Carried Forward

The following safety boundaries are confirmed in all source documents and must be preserved in any future export design:

- `document_status = DRAFT_NOT_AUTHORIZED` must remain visible on any draft export output.
- `payment_authorization_enabled = false` is an invariant in all API responses.
- `final_export_enabled = false` is an invariant in all API responses.
- Manual paper-distribution rows must not be persisted as payment truth by any export action.
- Export output must carry a draft-only watermark/label in both Thai and English.
- No export action may trigger payment approval, final authorization, or payment release.
- Settings do not authorize payment. Settings-backed calculation does not authorize payment.
- Review status `ACCEPTED_FOR_DRAFT_EXPORT` does not authorize payment. It authorizes only the design of a draft-export workflow.
- `FINAL_AUTHORIZATION_REQUIRED` is a separate later gate that must not be bypassed by export design.
- Teaching workload, Work H, opencourse, and coinstruc remain out of scope.
- Check-in remains post-duty reconciliation evidence and is not a pre-disbursement gate.

## Summary

The settings-backed draft preview is fully integrated and validated. The review workflow infrastructure exists. The system is technically capable of reaching the `ACCEPTED_FOR_DRAFT_EXPORT` review state.

However, no human reviewer has yet set the document to `ACCEPTED_FOR_DRAFT_EXPORT`, the paper-distribution source is not confirmed, and the export format has not been decided. These three human decisions are the minimum requirements before export design may proceed.

Recommended gate decision: **`HOLD_PENDING_REVIEW_ACCEPTANCE`**
