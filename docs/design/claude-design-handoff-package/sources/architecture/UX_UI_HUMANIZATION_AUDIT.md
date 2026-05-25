# UX_UI_HUMANIZATION_AUDIT.md

**Date**: 2026-05-22  
**Missing requested input**: `docs/architecture/UI_UX_CONSISTENCY_REPORT.md` does not exist  
**Substitute evidence used**: live frontend code, `docs/humanization/*`, screenshot atlas, cognitive-load audit, humanization-quality review

---

## Summary

EMS UX is stronger than many internal operational systems because it already has:

- a role-aware shell
- bilingual dictionaries
- role manuals
- screenshot atlas material
- explicit humanization and cognitive-load docs

Its main UX weaknesses are not absence of design. They are:

- uneven legacy-page consistency
- cognitive load on large operational pages
- residual raw strings / wording drift
- missing dedicated current UI consistency report

---

## Strengths

- `AppShell` gives the app a stable frame across authenticated pages.
- role theming and role-aware navigation are intentional, not accidental.
- screenshot atlas and role manuals are unusually comprehensive for an internal system.
- screenshot alignment report says current atlas is still largely representative for pilot training.
- i18n key parity passed (`1688` / `1688`).

---

## Inconsistency And Usability Findings

| Area | Evidence | UX Impact | Priority |
|---|---|---|---|
| Large operational pages | `Checkins.tsx`, `MyExam.tsx`, `Optimizer.tsx`, `WorkflowV2.tsx` remain large | Higher cognitive load and harder onboarding | High |
| Legacy vs. V2 page lineage | active routes use V2 pages while legacy pages remain tracked | Designers and developers can misread which UI is canonical | High |
| Raw string candidate debt | `check:i18n:raw` still warns | Wording and localization consistency remain uneven | Medium |
| Platform/faculty config surfaces | partial wiring and empty-array backend snapshot | UI can imply readiness that backend does not truly support | High |
| Missing dedicated current UI consistency report | requested source doc absent | Audit must rely on substitutes, not a single canonical UI audit | Medium |

---

## Humanization / Manual Alignment

### Strong alignment

- role manuals exist for admin, staff, teacher, supervisor, executive, governance, and related families
- journey docs cover operational and governance scenarios
- screenshot atlas exists and is still considered sufficient for initial pilot training

### Gaps

- some screenshot / manual references may age if pilot wording or icons change
- the missing UI consistency report leaves no single current architecture-side UX source
- stale internal frontend docs can undermine manual accuracy if copied forward

---

## Bilingual Clarity

Current state:

- dictionary parity is strong
- localization infrastructure is real
- backend message-to-translation mapping exists for some auth/public messages

Remaining concern:

- raw string scan still flags candidate text in operational pages and placeholders

---

## Role-Based UX Assessment

### Strong

- public student route exists separately from authenticated app flow
- print shop is explicitly isolated as its own narrow operational role
- governance roles have dedicated routed surfaces

### Watchlist

- some large admin pages still risk “too much on one screen”
- enterprise pages and older legacy pages may not feel equally polished

---

## Mobile / Tablet Readiness

Evidence:

- mobile bottom navigation exists
- screenshot atlas contains mobile and tablet captures for some pages

Audit judgment:

- foundational responsiveness exists
- role- and page-specific responsive behavior still needs real device validation on pilot hardware

---

## Pages Most Likely To Need UX Follow-Up

1. `Checkins`
2. `MyExam`
3. `Optimizer`
4. partially wired platform configuration / future faculty-config surfaces

These are not necessarily broken. They are the most likely to benefit from simplification or clearer guided flows.

---

## Audit Judgment

UX/UI humanization readiness is **good enough for rehearsal and controlled pilot onboarding**, but still uneven enough that post-pilot cleanup should include:

- canonical route/page cleanup
- raw-string cleanup
- focused cognitive-load reduction on the largest operational pages
