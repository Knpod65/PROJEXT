# Payment Document Draft XLSX Format Decision Gate

**Date**: 2026-06-12  
**Release candidate**: `EMS_DEMO_REVIEW_RC_1`  
**Human decision found**: `NO`  
**Current format gate**: `HOLD_PENDING_ADDITIONAL_REVIEW`  
**Final authorization design gate**: `FINAL_AUTHORIZATION_DESIGN_BLOCKED`

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

## Current Decision

No explicit post-RC1 human decision or reviewer identity is recorded. Therefore:

- Draft XLSX format gate: `HOLD_PENDING_ADDITIONAL_REVIEW`
- Final authorization design gate: `FINAL_AUTHORIZATION_DESIGN_BLOCKED`
- Next implementation gate opened: `NO`

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
