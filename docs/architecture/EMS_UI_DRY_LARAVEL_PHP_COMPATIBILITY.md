# EMS UI DRY Laravel/PHP Compatibility

**Date**: 2026-06-15  
**Constraint**: framework-neutral contracts only; no framework migration.

| Semantic component | React implementation | Blade/Livewire equivalent |
|---|---|---|
| App Shell | `AppShell` | `<x-app-shell>` |
| Page Header | `PageHeader` | `<x-page-header>` |
| Alert Banner | `AlertBanner` | `<x-alert-banner>` |
| Data Table | `DataTable` | `<x-data-table>` |
| Status Chip | `StatusChip` | `<x-status-chip>` |
| Form Field | `FormField` | `<x-form-field>` |
| Empty State | `EmptyState` | `<x-empty-state>` |
| Page Skeleton | `PageSkeleton` | `<x-page-skeleton>` |

CSS custom properties and semantic class names are the portable contract. React hooks, API clients, and business rules remain outside visual primitives.

