# EMS Authoritative Page Template Standard

**Date**: 2026-06-11  
**Design direction**: Quiet Institutional Command Center

## Standard

1. Use `page-stack page-stack--spacious` with responsive containment and no body-level horizontal overflow.
2. Use one `PageHeader` with localized eyebrow, title, description, optional actions, and optional status.
3. Use `AlertBanner` for safety, blockers, review requirements, and honest provisional states.
4. Use consistent metric and section `Card` surfaces; avoid decorative nested cards.
5. Use `DataTable`, or `table-wrap` plus `data-table` for domain-specific tables that cannot safely migrate.
6. Use `FormField` for labels, helpers, errors, disabled, and read-only presentation.
7. Use shared `Button` and `Badge`; domain-specific grid controls may remain native buttons when their custom interaction requires it.
8. Localize visible statuses. Do not show raw enum, color, or i18n-key text.
9. Preserve visible focus, readable contrast, Thai wrapping, and clear empty/loading/error states.
10. Preserve route roles and access behavior; visual alignment must not change permissions.

## Payment And Draft Export Addendum

- `DRAFT_NOT_AUTHORIZED` remains prominent.
- Settings source, calculation status, review status, and export-gate reason remain visible.
- `ACCEPTED_FOR_DRAFT_EXPORT` permits only the gated draft XLSX workflow.
- Draft XLSX must be described as review-only and non-authorizing.
- Official/final export, payment approval, and final authorization remain absent.
- `payment_authorization_enabled=false` and `final_export_enabled=false` remain invariant.

