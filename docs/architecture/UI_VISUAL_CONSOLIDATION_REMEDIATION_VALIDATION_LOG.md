# EMS Visual Consolidation Remediation Validation Log

**Date:** 2026-06-15  
**Implementation commits:** `ca3bd86`, `f2e76ee`, `c64bd5a`  
**Comparison surface:** `/admin-intelligence-dashboard`

## Root Causes Remediated

- The sticky Topbar is now an application identity/context surface and no longer competes with route headings.
- `PageHeader` owns the authenticated route `h1`; manual authenticated heroes and previously headerless Co-Exam, Copy, and Sections routes use one primary heading.
- Unauthorized and not-found authenticated states explicitly render an `h1`.
- The sidebar is bounded by `100dvh`, keeps intentional internal navigation scrolling, and uses a compact `1024-1199px` presentation.
- Conflicting `.summary-grid` definitions were consolidated into one shared responsive contract.
- Page-stack and Card containment prevent intrinsic table/content width from expanding the document.
- Optimization Trace and Workload Analytics no longer rely on non-existent Tailwind utility layouts.

## Fixed-Viewport Results

Authenticated Chrome DevTools Protocol captures used actual emulated viewport metrics.

| Route | Viewport | Primary `h1` | Horizontal overflow | Raw i18n key | Raw `session not found` |
|---|---:|---:|---:|---:|---:|
| `/optimizer-trace` | `1600x900` | 1 | 0px | No | No |
| `/optimizer-trace` | `1366x768` | 1 | 0px | No | No |
| `/optimizer-trace` | `1024x768` | 1 | 0px | No | No |
| `/workload-duty-analytics` | `1600x900` | 1 | 0px | No | No |
| `/workload-duty-analytics` | `1366x768` | 1 | 0px | No | No |
| `/workload-duty-analytics` | `1024x768` | 1 | 0px | No | No |

### Workload Computed Grid Proof

| Viewport | Filter columns | Metric columns |
|---|---|---|
| `1600x900` | 4 columns, approximately `244px` each | 4 columns, `304px` each |
| `1366x768` | 4 columns, approximately `186px` each | 2 columns, `507px` each |
| `1024x768` | 2 columns, approximately `237px` each | 2 columns, `360px` each |

The person-detail table is internally scrollable at `520px`. Charts use bounded existing-data subsets while the sortable detail table preserves the complete API-backed result.

## Page Acceptance

### Optimization Trace

- One compact page heading and session selector.
- Missing-session backend stub becomes one localized recovery state.
- No score gauge, score cards, raw backend note, or empty table appears in the missing-session state.
- Retry and Back to Optimizer actions are available.
- Valid/limited states use canonical metrics, timeline, status chips, tabs, and DataTable.

### Workload Analytics

- One page heading with localized workload-governance eyebrow.
- Explicit Apply and Reset filter behavior.
- Canonical FilterBar/FormField/Button controls.
- Six compact metrics in responsive shared grids.
- Existing-data visual analysis for people, duty category, role composition, daily cumulative workload, time slots, and fairness.
- Complete sortable person details remain available without expanding the document height for every row.

## Evidence

- `docs/operations/demo-smoke-screenshots/ui-consolidation-remediation/before-trace-1600.png`
- `docs/operations/demo-smoke-screenshots/ui-consolidation-remediation/after-trace-1600.png`
- `docs/operations/demo-smoke-screenshots/ui-consolidation-remediation/after-trace-1366.png`
- `docs/operations/demo-smoke-screenshots/ui-consolidation-remediation/after-trace-1024.png`
- `docs/operations/demo-smoke-screenshots/ui-consolidation-remediation/before-workload-1600.png`
- `docs/operations/demo-smoke-screenshots/ui-consolidation-remediation/after-workload-1600.png`
- `docs/operations/demo-smoke-screenshots/ui-consolidation-remediation/after-workload-1366.png`
- `docs/operations/demo-smoke-screenshots/ui-consolidation-remediation/after-workload-1024.png`

## Automated Validation

- Frontend build: PASS
- EN/TH i18n parity: PASS, `2509` keys per locale
- Raw-string warning scan: completed; no target-page raw keys rendered in fixed-viewport browser validation
- Backend health: HTTP 200
- Full backend suite: PASS, `1582 passed`
- `git diff --check`: PASS

The production build retains the pre-existing large-chunk advisory.

## Non-Regression

- Backend application files changed: **NO**
- Optimization calculations changed: **NO**
- Workload calculations changed: **NO**
- Route declarations or permissions changed: **NO**
- Payment/export/review/settings logic changed: **NO**
- Payment approval, final authorization, or official-final export added: **NO**

