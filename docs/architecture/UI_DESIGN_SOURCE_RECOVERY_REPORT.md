# UI Design Source Recovery Report

**Date**: 2026-06-11  
**Result**: `DESIGN_SOURCE_RECOVERED`

## Authoritative Sources Found

1. `docs/design/claude-design-handoff-package/00_CLAUDE_DESIGN_MASTER_PROMPT.md`
2. `docs/design/claude-design-handoff-package/01_EMS_DESIGN_HANDOFF_BRIEF.md`
3. `docs/design/claude-design-handoff-package/02_EMS_DESIGN_CONTEXT_BUNDLE.md`
4. `docs/design/claude-design-handoff-package/03_CLAUDE_DESIGN_ATTACHMENT_LIST.md`
5. `docs/architecture/EMS_PAGE_TEMPLATE_STANDARD.md`
6. `docs/architecture/UI_SHARED_COMPONENT_STRATEGY.md`
7. `docs/humanization/screenshot-atlas/major-pages.md`
8. `docs/humanization/screenshot-atlas/SCREENSHOT_CAPTURE_REPORT.md`

The authoritative direction is the Claude handoff's **Quiet Institutional Command Center for Exam Operations**, refined by the implemented EMS page template and shared UI primitives. The screenshot atlas is evidence of real page states, not a replacement for the template standard.

## Missing Historical Sources

- `docs/architecture/UI_UX_CONSISTENCY_REPORT.md`
- `docs/architecture/EMS_DESIGN_CONSISTENCY_CHECKLIST.md`

These files remain absent and their contents were not fabricated. The existing humanization audit, template standard, component strategy, and screenshot evidence provide the replacement source set.

## Recovered Design Rules

- Calm institutional hierarchy; data and next action before decoration.
- One consistent page shell and hero per routed operational page.
- Role-aware accents remain restrained and never carry meaning alone.
- Shared cards, tables, form fields, buttons, badges, empty states, and skeletons are the default.
- Thai and English must wrap cleanly and visible backend enums must be localized.
- Payment and document pages must state their draft/review boundaries honestly.
- Gated draft XLSX output is permitted only after review acceptance; it is never official/final export or payment authorization.

## Drift Risk

Highest current risk is on recently extended payment document, settings, review, and draft-export states. Legacy/custom operational pages without `PageHeader` or shared tables remain lower-priority alignment candidates. Workload routes were inventoried but are audit-only because workload logic and surfaces are explicitly out of scope for modification.

