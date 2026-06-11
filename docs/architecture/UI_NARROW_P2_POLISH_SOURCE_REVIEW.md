# UI Narrow P2 Polish Source Review

**Date**: 2026-06-11  
**Scope**: payment-interface wording, blocked-role clarity, and role-based visual evidence

## Sources Read

- `UI_DESIGN_SOURCE_RECOVERY_REPORT.md`
- `EMS_AUTHORITATIVE_PAGE_TEMPLATE_STANDARD.md`
- `UI_FULL_ROUTE_TEMPLATE_INVENTORY.md`
- `UI_FULL_ROUTE_SCREENSHOT_CAPTURE_REPORT.md`
- `UI_FULL_ROUTE_DEFECT_BACKLOG.md`
- `UI_PAYMENT_EXPORT_SAFETY_VISUAL_AUDIT.md`
- `UI_SYSTEM_ALIGNMENT_VALIDATION_LOG.md`
- `UI_SCREENSHOT_REVIEW_SUMMARY.md`
- `UI_RESIDUAL_DEFECT_BACKLOG.md`
- readiness and demo disclosure documents

## Remaining Groups

| Group | Classification | Decision |
|---|---|---|
| Payment draft warning still says no files are exported | `P2_SAFE_FIX_NOW` | Correct copy to distinguish gated draft XLSX from official/final export. |
| Disabled draft-export tooltip exposes raw review enum | `P2_SAFE_FIX_NOW` | Replace with localized human-readable gate language. |
| Shared unauthorized route state lacks explanation | `P2_SAFE_FIX_NOW` | Add localized description without changing route guards. |
| Broad legacy/custom operational route polish | `P2_DEFER_VISUAL_ONLY` | Defer to route-specific passes. |
| Workload route presentation | `P2_DEFER_WORKLOAD_SCOPE_NOT_TOUCHING` | Audit/evidence only; no code edits. |
| Role/data evidence unavailable in a live account | `P2_DEFER_AUTH_LIMITATION` | Record honestly if encountered. |

## Planned Frontend Files

- `frontend/src/App.tsx`
- `frontend/src/i18n/en.ts`
- `frontend/src/i18n/th.ts`

## Safety Boundaries

- No backend, API, permissions, route roles, payment calculations, settings persistence, review gate, or draft-export gate changes.
- `DRAFT_NOT_AUTHORIZED` remains visible.
- Gated draft XLSX remains review-only and non-authorizing.
- Workload, Work H, opencourse, coinstruc, and teaching workload remain untouched.

