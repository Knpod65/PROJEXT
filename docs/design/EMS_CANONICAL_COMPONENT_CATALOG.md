# EMS Canonical Component Catalog

**Date**: 2026-06-15

| Semantic component | Purpose and canonical behavior | Blade/Livewire equivalent |
|---|---|---|
| App Shell | Role-aware authenticated frame; responsive sidebar/topbar/mobile nav. | `<x-app-shell>` |
| Page Header | Eyebrow, concise purpose, contextual status, and primary actions. | `<x-page-header>` |
| Alert Banner | Safety, blocker, review, and provisional-state explanation. | `<x-alert-banner>` |
| Button | Actions with semantic variants, disabled/loading state, focus, and reduced motion. | `<x-button>` |
| Card | One coherent section or metric surface; avoid decorative nesting. | `<x-card>` |
| Data Table | Canonical table density, empty/loading state, and local horizontal scrolling. | `<x-data-table>` |
| Status Chip | Localized universal semantic state; never role-colored. | `<x-status-chip>` |
| Badge / Role Badge | Counters, labels, and role identity; not workflow state. | `<x-badge>` / `<x-role-badge>` |
| Tabs | Progressive disclosure for secondary detail. | `<x-tabs>` |
| Form Field | Label, helper, validation, disabled, and read-only anatomy. | `<x-form-field>` |
| Filter Bar | Responsive filter/action grouping. | `<x-filter-bar>` |
| Empty State | No-data, blocked, and focused recovery state. | `<x-empty-state>` |
| Page Skeleton | Stable page-level loading hierarchy. | `<x-page-skeleton>` |
| Inline Error | Persistent local or field-adjacent failure. | `<x-inline-error>` |

All components must support visible keyboard focus, Thai/English wrapping, narrow layouts, and reduced motion. Visual components contain no business rules.

