# UI Shared Component Strategy

**Date**: 2026-06-05

## Reused Components

- `Button`
- `Card`
- `DataTable`
- `Badge`
- `Tabs`
- `EmptyState`
- `Skeleton`

## Added Small Wrappers

- `PageHeader`: shared hero structure for routed pages.
- `AlertBanner`: shared safety/status message surface.
- `FormField`: shared label/helper/error wrapper for form controls.

## CSS Conventions

- Keep role-aware tokens and shell variables unchanged.
- Prefer `page-stack`, `form-grid`, `table-wrap`, `data-table`, `metric-value`, `ui-list`, and `timeline-list`.
- Avoid introducing external UI libraries or large design-system abstractions.

## Pages Updated

- Official Payment Document Draft.
- Advance Batch Preview.
- Invigilation Rate Rules.
- Audit Explorer.
- Governance Cockpit.
- Operational Health.
- Platform Configuration.
- Export Center.
- Staff Availability.
- Dashboard.

## Risks

- Some large legacy/custom pages still contain manual tables or raw strings and should be handled in later lower-risk passes.
- Human screenshot evidence is still separate from this pass unless a real screenshot is placed.

