# Payment Document Draft XLSX Format Decision Gate

**Date**: 2026-06-12  
**Release candidate**: `EMS_DEMO_REVIEW_RC_1`  
**Human decision found**: `YES` (2026-06-12)  
**Decision option**: `ACCEPT_DRAFT_XLSX_FORMAT`  
**Reviewer identity**: `NOT_PROVIDED`  
**Current format gate**: `DRAFT_XLSX_FORMAT_ACCEPTED`  
**Final authorization design gate**: `FINAL_AUTHORIZATION_DESIGN_BLOCKED`  
**Supporting requirement opened**: `SUPPORTING_FINANCE_INVIGILATION_ROSTER_REQUIRED`

## Purpose

This gate records the supervisor/finance decision on the produced RC1 draft XLSX format. It is separate from the existing `ACCEPTED_FOR_DRAFT_EXPORT` review status, which permits gated draft generation but does not prove acceptance of the generated format.

## Allowed Human Decisions And Gate Results

| Human decision | Draft XLSX format gate | Additional result |
|---|---|---|
| `ACCEPT_DRAFT_XLSX_FORMAT` | `DRAFT_XLSX_FORMAT_ACCEPTED` | Final authorization design remains blocked unless separately allowed |
| `ACCEPT_WITH_MINOR_FORMAT_NOTES` | `DRAFT_XLSX_FORMAT_ACCEPTED_WITH_MINOR_NOTES` | Create a narrow format-revision backlog |
| `REQUEST_DRAFT_XLSX_FORMAT_REVISION` | `DRAFT_XLSX_FORMAT_REVISION_REQUIRED` | Revise and revalidate the draft XLSX |
| `HOLD_PENDING_ADDITIONAL_REVIEW` | `HOLD_PENDING_ADDITIONAL_REVIEW` | No implementation gate opens |
| `REJECT_DRAFT_XLSX_FORMAT` | `DRAFT_XLSX_FORMAT_REJECTED` | Redesign is required |
| `ALLOW_FINAL_AUTHORIZATION_DESIGN_PHASE` | Existing format result plus `FINAL_AUTHORIZATION_DESIGN_ALLOWED` | Docs-only design phase only; no approval implementation |

## Current Decision (2026-06-12)

Human decision `ACCEPT_DRAFT_XLSX_FORMAT` has been recorded. Reviewer identity is `NOT_PROVIDED` — no identity was fabricated.

- Draft XLSX format gate: `DRAFT_XLSX_FORMAT_ACCEPTED`
- Final authorization design gate: `FINAL_AUTHORIZATION_DESIGN_BLOCKED` (unchanged)
- New supporting requirement: `SUPPORTING_FINANCE_INVIGILATION_ROSTER_REQUIRED`
- Implementation gate for supporting roster: `HOLD_PENDING_OPTIMIZE_ROSTER_SOURCE_CONFIRMATION`

**Acceptance of the draft XLSX format is not payment authorization.** The accepted summary XLSX is a review-only draft. A supporting finance invigilation roster export (`DRAFT_FINANCE_INVIGILATION_ROSTER_XLSX`) is required before finance can verify signatures and headcounts. See `PAYMENT_SUPPORTING_FINANCE_ROSTER_EXPORT_CONTRACT.md`.

## Invariants

- `DRAFT_NOT_AUTHORIZED` remains unchanged.
- Draft XLSX remains review-only and non-authorizing.
- `payment_authorization_enabled=false`.
- `final_export_enabled=false`.
- No final payment approval, final authorization, official-final export, or payment release is authorized.

## In-System Checklist And Evidence Update (2026-06-12)

- A persistent seven-step inspection checklist now supports evidence-based review.
- A real RC1 XLSX sample plus PNG, Markdown preview, and cell map are available for inspection.
- Checklist completion is deliberately separate from this explicit human decision gate.
- No checklist state can set `DRAFT_XLSX_FORMAT_ACCEPTED` or open final-authorization design.
- Current format gate remains `HOLD_PENDING_ADDITIONAL_REVIEW`.

## Checklist Completion And Evidence Recheck (2026-06-12)

- Persistent checklist capability exists, but no reviewer item rows are saved for the RC1 document.
- Effective checklist state is `0/7 CHECKED`; all seven items remain `NOT_STARTED`.
- The XLSX sample, PNG, Markdown preview, and cell map are verified complete.
- Evidence availability and the existing draft-export review record do not prove human format acceptance.
- Explicit decision found: `NO`; reviewer identity: `NOT_PROVIDED`.
- Current format gate remains `HOLD_PENDING_ADDITIONAL_REVIEW`.
- Final authorization design remains `FINAL_AUTHORIZATION_DESIGN_BLOCKED`.
