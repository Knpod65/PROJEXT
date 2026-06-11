# EMS Page Template Standard

**Date**: 2026-06-05

## Standard Structure

1. Page container: use `page-stack page-stack--spacious`, responsive spacing, no horizontal body overflow.
2. Page hero: use one hero with eyebrow, title, description, optional actions, and optional status chips.
3. Safety/status banner: payment and document pages must show preview/draft/not-authorized status, no final payment, no official export, and supervisor/finance review required.
4. Summary cards: use 2-4 cards per row with consistent metric typography and muted helper text.
5. Section cards: use `Card` for grouped content with title, subtitle, content, and optional actions.
6. Data tables: use `DataTable` when practical; otherwise wrap manual tables in `table-wrap` and `data-table`.
7. Forms: use label/helper/error patterns through shared form field styling and responsive `form-grid`.
8. Buttons: use `Button`; avoid raw native browser buttons except domain-specific interactive grid controls.
9. Tabs: use shared `Tabs` with visible active and focus state.
10. Status chips: use `Badge` for `DRAFT_NOT_AUTHORIZED`, `PREVIEW_ONLY`, `PENDING_RATE_RULE`, `PREVIEW_CALCULATED`, `CONFIGURED`, `READ_ONLY`, `BLOCKED`, and `NEEDS_REVIEW`.
11. Accessibility: do not rely on color only; maintain visible focus, accessible labels, readable contrast, and Thai wrapping.

## Payment/Document Addendum

- `DRAFT_NOT_AUTHORIZED` must remain visible on official document drafts.
- A gated draft XLSX control may appear only after `ACCEPTED_FOR_DRAFT_EXPORT` and must be labeled as review-only and non-authorizing.
- No approve, authorize, final payment, official/final export, or official PDF/Excel control should appear.
- Paper-distribution manual rows must be described as request-only and non-persistent.
