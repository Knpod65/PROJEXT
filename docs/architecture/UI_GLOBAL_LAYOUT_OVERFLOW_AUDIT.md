# UI Global Layout Overflow Audit

**Date**: 2026-06-05

## Search Areas

- App shell and sidebar layout.
- Page hero action wrapping.
- Data table wrappers.
- Form grids and manual paper-distribution rows.
- Operational custom grids such as staff availability slots.

## Findings

- `AppShell` already uses `minmax(0, 1fr)` for the main content lane.
- `table-wrap` already provides horizontal scrolling for data tables.
- The payment draft paper rows needed a responsive form grid so manual rows do not force horizontal overflow.
- Governance and audit pages had manual table/list styling that could drift from table wrappers.
- No broad shell rewrite is required.

## Fix Direction

- Add responsive `form-grid` variants.
- Keep manual tables inside `table-wrap` or convert to `DataTable`.
- Let page hero actions wrap via existing `page-hero__actions`.
- Do not apply blanket `overflow-x: hidden`.

