# UI Narrow P2 Polish Plan

**Date**: 2026-06-11

| Route/state | Classification | Current symptom | Planned fix | Risk | Validation |
|---|---|---|---|---|---|
| `/invigilation-payment-document-draft` warning | `P2_SAFE_FIX_NOW` | Copy says no files are exported although gated draft XLSX exists. | State that review-accepted draft XLSX may be produced while official/final export remains disabled. | Low, copy only | Build, i18n, admin/staff screenshots |
| Disabled draft-export control | `P2_SAFE_FIX_NOW` | Tooltip exposes raw `ACCEPTED_FOR_DRAFT_EXPORT`. | Use localized human-readable gate language. | Low, copy only | Build, i18n, admin screenshot |
| Teacher/print-shop payment routes | `P2_SAFE_FIX_NOW` | Shared blocked state has a title but no explanatory description. | Add localized current-role access explanation to shared unauthorized state. | Low, presentation only | Teacher/print-shop screenshots |
| Legacy/custom operational pages | `P2_DEFER_VISUAL_ONLY` | Bespoke page patterns remain usable but not fully standardized. | No edit in this pass. | Broad regression risk | Existing evidence/backlog |
| Workload routes | `P2_DEFER_WORKLOAD_SCOPE_NOT_TOUCHING` | Custom layout remains. | No edit in this pass. | Explicit scope boundary | Confirm no workload diff |

## Acceptance

- Admin and staff retain their current payment-document behavior.
- Staff settings remain read-only.
- Teacher and print shop remain blocked.
- No final approval, final authorization, official-final export, or payment authorization wording/control is added.

