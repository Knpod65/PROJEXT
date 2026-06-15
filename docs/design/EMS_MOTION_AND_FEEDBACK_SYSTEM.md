# EMS Motion And Feedback System

**Date**: 2026-06-15

- Hover/focus: `140ms`
- Small state change: `180ms`
- Drawer/sidebar/modal: `220ms`
- Page reveal and accordion: `200ms`
- Toast: `220ms`
- Default easing: calm institutional ease-out

Allowed motion is limited to opacity, 4-8px reveal translation, active-navigation indicators, subtle 1-2px elevation, drawers/modals, accordions, and skeletons.

Do not repeatedly animate critical warnings, monetary totals, table rows, backgrounds, or decorative surfaces. All transitions and animations must collapse under `prefers-reduced-motion: reduce`.

