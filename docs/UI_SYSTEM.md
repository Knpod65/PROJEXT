# UI SYSTEM

## Layout Rules

- Use the shared app shell for authenticated pages
- Primary page framing pattern:
  - `page-stack`
  - `page-hero`
  - cards/data tables below the hero
- Keep actions close to the page hero or card header
- Prefer compact vertical rhythm over deeply nested card structures

## Table Consistency Rules

- Use `DataTable` where possible
- If a native table is used, mirror the same density and spacing as other admin tables
- Keep column labels short and domain-specific
- Use clamp/truncate wrappers for long content
- Show empty state copy, not blank containers

## Scrolling Rules

- Scrollable tables should use the shared threshold pattern
- Current convention:
  - set `scrollThreshold={5}` on `DataTable`
  - use bounded height wrappers for manual tables when record count is large
- Avoid full-page overflow caused by a single table

## Empty / Loading States

- Use `Skeleton` for loading
- Use `EmptyState` for:
  - no rows
  - load errors
  - blocked access views
- Avoid plain text placeholders when a shared component already exists

## Role Theme Usage

- Source of truth: `frontend/src/theme/roleThemes.ts`
- Never hardcode role accent colors inside feature pages
- Use role theme tokens for:
  - role badges
  - shell/sidebar accents
  - role-distribution visuals
  - any role-specific highlight surface

## Role Theme Palette

- `admin`: navy
- `teacher`: green
- `staff`: amber
- `dept_supervisor`: purple
- `esq_head`: maroon
- `secretary`: teal
- `print_shop`: gray-blue

## Typography / Copy Rules

- Headers should be short and operational
- Subtitles should explain action or context, not repeat the title
- Avoid long paragraphs inside cards
- Prefer labels that stay readable in both English and Thai

## i18n In UI

- All user-facing labels should come from i18n keys
- Components should not embed English-only labels
- Use `common.*` for shared controls
- Use domain namespaces for page-specific text
