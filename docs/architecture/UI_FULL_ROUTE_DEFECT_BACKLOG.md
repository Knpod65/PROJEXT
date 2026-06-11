# UI Full Route Defect Backlog

**Date**: 2026-06-11

| defect_id | Route | Description | Severity | Resolution/status |
|---|---|---|---|---|
| UI-FULL-001 | `/invigilation-payment-document-draft` | Review/settings/calculation statuses displayed raw backend enums. | P1_FIX_NOW | VALIDATED: localized display labels visible in authenticated screenshot. |
| UI-FULL-002 | `/invigilation-payment-document-draft` | Review safety copy contradicted the newly implemented gated draft XLSX workflow, and the gate reason was only a button tooltip. | P1_FIX_NOW | VALIDATED: corrected copy and visible gate banner shown in authenticated screenshot. |
| UI-FULL-003 | `/payment-document-settings` | Settings status/select exposed raw enums; helper/error content bypassed the complete `FormField` pattern. | P1_FIX_NOW | VALIDATED: localized status and aligned field presentation shown in authenticated screenshot. |
| UI-FULL-004 | `/platform-config` | Symbolic check/em-dash display was inconsistent with the text-first institutional template. | P2_POLISH | VALIDATED: stable localized text/fallback display confirmed. |
| UI-FULL-005 | legacy/custom operational routes | Several usable pages still use bespoke heroes, manual tables, or custom form layouts. | P2_POLISH | Deferred to route-specific passes to avoid broad workflow regressions. |
| UI-FULL-006 | workload routes | Workload page retains a custom table/form surface. | DEFER_WITH_REASON | Audit-only; workload domain explicitly excluded from edits. |

## Summary

- P0 blocking: `0`
- P1 identified: `3`
- P1 validated: `3`
- P2 identified: `3`
- Backend/API/business-logic changes: `NO`
