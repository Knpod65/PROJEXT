# EMS Existing UI System Recovery Report

**Date**: 2026-06-15  
**Direction**: Quiet Institutional Command Center, consolidated edition

## Recovered Foundation

- Existing role-aware `AppShell`, sidebar, topbar, and mobile bottom navigation are strong and remain authoritative.
- The shell already uses `minmax(0, 1fr)`, responsive navigation, `data-role`, and role-aware CSS variables.
- Existing shared primitives: `Button`, `Card`, `DataTable`, `Badge`, `Tabs`, `EmptyState`, `Skeleton`, `PageHeader`, `AlertBanner`, `FormField`, `FilterBar`, `RoleBadge`, `StatCard`, `Modal`, `ConfirmDialog`, `Toast`, and `LanguageToggle`.
- Existing semantic role and permission sources: `utils/roles.ts`, `utils/permissions.ts`, `usePermission.ts`, and route-level `GuardedPage`.
- Existing evidence: 78 screenshot-atlas PNGs and 92 operations smoke PNGs.

## Current Drift

- Role colors are still injected as AppShell and component inline styles instead of being fully rooted in semantic CSS selectors.
- Status color mappings and raw enum labels are repeated across feature pages.
- Loading/error patterns are split between `Skeleton`, `EmptyState`, and older utility-class wrappers.
- Motion timings are scattered and reduced-motion handling is missing.
- Active high-load pages remain large: Checkins, MyExam, Optimizer, WorkflowV2, and the official payment draft.
- Manual tables and native controls remain valid in some custom workflows, but several lack canonical wrappers or state presentation.

## Enforcement Decisions

- Preserve the shell and shared components; add only `StatusChip`, `PageSkeleton`, and `InlineError`.
- Use semantic CSS role selectors and universal status tokens.
- Keep permissions independent from visual themes.
- Use `DataTable` when behavior is preserved; otherwise retain semantic tables within `table-wrap`.
- Treat duty-workload routes as audit/validation only and do not modify their files.
- Keep backend, API, calculation, permission, readiness, payment, export, and workload behavior unchanged.

