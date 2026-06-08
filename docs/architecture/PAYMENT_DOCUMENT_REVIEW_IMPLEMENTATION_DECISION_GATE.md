# Payment Document Review Implementation Decision Gate

**Date**: 2026-06-08  
**Current decision**: `DOCS_ONLY_MODEL_NOW`  
**Draft status**: `DRAFT_NOT_AUTHORIZED`

## Purpose

Define safe implementation options for payment-document review/comment workflow after the supervisor/finance-facing decision accepted the current draft format.

## Options

| Option | Meaning | Risk |
|---|---|---|
| `DOCS_ONLY_MODEL_NOW` | Record decision and model workflow/settings without runtime changes. | Lowest; no false review persistence. |
| `IMPLEMENT_REVIEW_FIELDS_ON_DRAFT_PAGE` | Add visible review fields to the current draft page. | Requires careful persistence decision; non-persistent comments may mislead reviewers. |
| `IMPLEMENT_REVIEW_QUEUE` | Build a dedicated queue for payment-document drafts awaiting review. | Requires backend model, permissions, audit, and UI scope. |
| `IMPLEMENT_SETTINGS_PAGE_FIRST` | Build configurable rate and paper-distribution responsibility settings first. | Requires settings ownership and validation rules. |
| `HOLD_FOR_SUPERVISOR_CONFIRMATION` | Pause until reviewer identity, storage, and process are confirmed. | Safe but delays workflow implementation. |

## Recommended Decision

`DOCS_ONLY_MODEL_NOW`

Rationale: the current repo has a draft preview route and configuration foundations, but no persistent payment-document review table/API. A docs-only model records the human decision without implying that comments are safely stored or that review records are durable.

## Decision Criteria For Next Pass

- Do comments need to be visible on the current draft page?
- Do review records need to be persistent and auditable?
- Which roles can create, comment, request revisions, and accept drafts?
- Is reviewer identity available from the current auth/session model?
- Should comments be attached to generated draft versions or to current filters/input only?
- Are email or notification workflows required later?

## Non-Authorization Rules

- No option in this gate authorizes payment.
- `ACCEPTED_FOR_DRAFT_EXPORT` is not official export and not final payment authorization.
- Final authorization remains a separate future gate.
- Teaching workload, Work H, opencourse, and coinstruc are out of scope.

## Implementation Update (2026-06-08)

- Current implementation has advanced from `DOCS_ONLY_MODEL_NOW` to persistent review records plus a draft-page review panel.
- The implemented path is limited to durable comments, review status, reviewer identity, and review history for `ADVANCE_PAYMENT_DRAFT_SUMMARY`.
- `ACCEPTED_FOR_DRAFT_EXPORT` remains non-authorizing and does not enable final export.
- Payment approval, final authorization, official PDF/Excel/export, active-rate changes, and final payable truth remain blocked.
