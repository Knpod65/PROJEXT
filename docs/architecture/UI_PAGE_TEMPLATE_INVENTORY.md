# UI Page Template Inventory

**Date**: 2026-06-05  
**Scope**: important routed EMS pages and current template risk

| Route | Component | Page type | Current template | Risk | Priority |
|---|---|---|---|---|---|
| `/dashboard` | `Dashboard.tsx` | dashboard | EMS hero, cards, charts | strong baseline; shared header alignment useful | P1_FIX_THIS_PASS_IF_SAFE |
| `/audit-explorer` | `AuditExplorer.tsx` | audit console | hero, tabs, raw audit table | raw table/timeline styling drift | P0_FIX_NOW |
| `/operational-health` | `OperationalHealth.tsx` | operational status | hero, cards, raw status rows | utility-class drift | P1_FIX_THIS_PASS_IF_SAFE |
| `/platform-config` | `PlatformConfiguration.tsx` | read-only configuration | hero, section cards, manual tables | first-screen and table consistency risk | P1_FIX_THIS_PASS_IF_SAFE |
| `/invigilation-advance-batch-preview` | `AdvanceInvigilationBatchPreview.tsx` | payment preview | hero, cards, table, raw form fields | draft safety and form consistency risk | P0_FIX_NOW |
| `/invigilation-rate-rules` | `InvigilationRateRules.tsx` | payment configuration | hero, cards, two inputs | warning/header consistency risk | P0_FIX_NOW |
| `/invigilation-payment-document-draft` | `OfficialPaymentDocumentDraft.tsx` | official-style draft | hero, cards, table, raw form fields | official table shape and draft safety risk | P0_FIX_NOW |
| `/schedule` | `Schedule.tsx` | schedule board | established EMS hero/table | acceptable; avoid broad rewrite | P2_DEFER |
| `/submissions` | `Submissions.tsx` | submissions workflow | established EMS hero/tabs/cards | raw strings outside this pass | P2_DEFER |
| `/exports-center` | `ExportCenter.tsx` | export operations | cards/tables without page hero | hierarchy drift | P1_FIX_THIS_PASS_IF_SAFE |
| `/import` | `ImportV2.tsx` | import wizard | established EMS hero/forms | large workflow; avoid risky rewrite | P2_DEFER |
| `/governance` | `GovernanceCockpit.tsx` | governance cockpit | hero plus raw cards/table | raw/scaffold visual drift | P0_FIX_NOW |
| `/staff-availability` | `StaffAvailability.tsx` | staff availability | custom filters/table/slot grid | raw form controls; interactive table risk | P1_FIX_THIS_PASS_IF_SAFE |
| `/users` | `UsersV2.tsx` | user management | V2 EMS hero and table | already aligned enough | P2_DEFER |
| `/settings` | `SettingsV2.tsx` | settings | V2 EMS hero and panels | already aligned enough | P2_DEFER |

## Inventory Notes

- Legacy files remain tracked, but current routes point to V2 pages for users/settings/workflow/swaps/import.
- Payment/document pages stay draft/preview-only.
- Workload references in active EMS UI remain exam duty workload only; teaching workload payment remains out of scope.

