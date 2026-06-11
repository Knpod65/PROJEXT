# UI Legacy Operational Polish Plan

**Date**: 2026-06-11

| Route | Component family | Current issue | Planned presentation fix | Validation |
|---|---|---|---|---|
| `/submissions` | `Submissions`, submission summary/table | Mixed-language raw labels and statuses | Route-scoped EN/TH copy for hero, metrics, tabs, filter, table, messages, empty states, and toasts | Admin screenshot + build/i18n |
| `/swaps` | `SwapsV2`, swap modals | Raw statuses/actions and mojibake separators | Localized status/action/modal/table copy and clean separators | Staff screenshot + build/i18n |
| `/printreview` | `PrintReview` | Raw print-review lifecycle and detail copy | Localized statuses, metrics, tabs, detail fields, validation, filters, and actions | Admin screenshot + build/i18n |
| `/external` | `External` | Raw operational forms/status/preview copy | Localized hero, forms, statuses, preview, metrics, empty states, and toasts | Admin screenshot + build/i18n |
| `/rooms-v2` | `RoomManagementV2`, `RoomEditModal` | Raw room/availability/status copy | Localized table, metrics, filters, slot states, block lists, modal, and toasts | Admin screenshot + build/i18n |
| `/period` | `Period` | No page header; raw lifecycle/options/actions; incomplete states | Add shared `PageHeader`, use `FormField`, localize lifecycle and states | Admin screenshot + build/i18n |

## Implementation Rules

- Preserve existing hero structures on the first five routes; `/period` alone gains `PageHeader`.
- Keep all current services, hooks, handlers, payloads, role checks, and mutation flows unchanged.
- Keep domain-specific tables and room slot controls where they already support the workflow.
- Add only matching EN/TH keys for changed visible strings.
- Use existing before-state `full-ui-audit-*.png` captures and save real updated screenshots as `legacy-polish-*.png`.

## Regression Checks

- `/invigilation-payment-document-draft`: `DRAFT_NOT_AUTHORIZED`, review-only draft XLSX gate, no final approval/authorization.
- `/payment-document-settings`: unchanged role and safety behavior.
- Workload route files and presentation: unchanged.

