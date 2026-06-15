# EMS UI Permission And Role DRY Contract

**Date**: 2026-06-15

- `getEffectiveRole(user)` is the single role-resolution function.
- `useEffectiveRole()` is the canonical React hook for presentation needing the current effective role.
- Route access remains in `App.tsx` through role declarations and `GuardedPage`.
- Feature actions use named semantic helpers from `utils/permissions.ts` and `usePermission()`.
- Pages must not duplicate effective/active/base-role coalescing or permission role arrays.
- Theme selection never grants permission; permission results never select status colors.
- Admin view-as behavior continues to respect base role and effective role independently.

No permission outcome or route access list is changed by consolidation.

