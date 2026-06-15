# EMS Visual Consolidation Failure Diagnosis

**Date:** 2026-06-15  
**Baseline:** `main` at `c36e906`  
**Status:** Confirmed failures remediated for the diagnosed shared causes and target routes; see `UI_VISUAL_CONSOLIDATION_REMEDIATION_VALIDATION_LOG.md`.

## Preflight

- Repository root: `C:\Users\DELL\Desktop\PROJEXT\opt\ems_system`
- `main` matched `origin/main`; `git pull --ff-only origin main` reported `Already up to date`.
- Backend health: `GET http://127.0.0.1:8000/api/health` returned HTTP 200.
- Frontend root: `GET http://127.0.0.1:3000/` returned HTTP 200.
- Authenticated browser DOM reproduced the defects from the current source. The evidence is not from a stale browser build.

## Invalidated Claims

The following statements in the previous consolidation evidence are retracted until the remediation pass is visually validated:

- zero raw i18n keys
- coherent shared layout
- successful shell alignment
- full route visual consolidation
- completed interface renovation

HTTP 200, successful route rendering, build checks, and i18n scripts are not visual acceptance evidence.

## Confirmed Root Causes

### Competing Heading Layers

`AppShell` always renders a sticky `Topbar` containing the route title as an `h1` and route description. Many authenticated pages also render a large `page-hero` containing the same title and description. Workload Analytics therefore renders the same Thai title twice, while Optimization Trace renders two competing route titles.

### Inert Utility-Class Layouts

The frontend has no Tailwind dependency or generated utility stylesheet. Optimization Trace and Workload Analytics use classes such as `grid-cols-1`, `xl:grid-cols-3`, `p-4`, `mt-4`, `space-y-3`, and `overflow-x-auto`. Those classes have no computed layout effect.

Consequences:

- Workload filter and summary containers compute to `display: block`.
- Workload metric cards and analysis panels become full-width vertical rows.
- Trace score, warning, timeline, and tables lose intended spacing and grouping.
- Raw native controls do not receive canonical field presentation.

### Conflicting Shared Summary Rules

`utilities.css` defines `.summary-grid` as a responsive CSS grid. Later rules in `components.css` redefine it as a wrapping flex container and redefine `.summary-box`. Import order makes the later component rule authoritative, so the shared primitive has two incompatible contracts.

### Sidebar And Breakpoint Pressure

The desktop shell reserves a fixed 280px sidebar. The sidebar is `position: sticky`, `height: 100vh`, and internally scrollable, but it lacks `100dvh` bounding and a stable scrollbar gutter. At the `1024px` boundary the full-width sidebar and verbose cards consume excessive horizontal space immediately before the mobile breakpoint.

## Live Computed Measurements

Authenticated Thai-session measurements were collected from the current source at a live `1920 x 945` browser viewport. Before screenshots were clipped to `1600 x 900` from the same authenticated page.

### Shared Shell

| Measurement | Value |
|---|---:|
| Sidebar rectangle | `x=0`, `width=280`, `height=945` |
| Topbar rectangle | `x=280`, `width=1640`, `height=129` |
| Content rectangle | `x=280`, `width=1640` |
| Page content left edge | `x=308` |
| Hero top edge | `y=157` |
| Document horizontal overflow | `0px` at the measured viewport |

### Optimization Trace

| Measurement | Value |
|---|---:|
| Hero rectangle | `x=308`, `y=157`, `width=1584`, `height=165.19` |
| Detached score row | `width=1584`, `height=149` |
| Raw key visible | `TRACE.EYEBROW` |
| Route heading layers | sticky Topbar `h1` plus page-hero `h2` |
| Candidate container computed display | `block` |
| Backend stub text exposed | `session not found` through `quality_note` |

### Workload Analytics

| Measurement | Value |
|---|---:|
| Hero rectangle | `x=308`, `y=157`, `width=1569`, `height=165.19` |
| Route heading layers | duplicated sticky Topbar `h1` and page-hero `h2` |
| Intended filter grid computed display | `block` |
| Intended summary grid computed display | `block` |
| Intended analysis grid computed display | `block` |
| Summary section height | `654px` |
| Analysis section height | `2922.38px` |
| Person detail section top | `y=4154.56` |
| Approximate page content height | over `5100px` |

## Shared-Root Classification

| Category | Confirmed routes/files |
|---|---|
| Competing Topbar/page heading | Authenticated routes with a local `PageHeader` or manual `page-hero`; shell-level contract requires correction |
| Inert utility layout | `/optimizer-trace`; `/workload-duty-analytics`; `/duty-workload`; `/my-workload` |
| Conflicting `.summary-grid` contract | Active routes and shared cards using `.summary-grid`; repair at the shared primitive |
| Raw form controls caused by missing canonical wrappers | Workload Analytics routes |
| Unaffected comparison page | `/admin-intelligence-dashboard` uses named canonical layout classes and remains the comparison surface |

## Remediation Acceptance

The remediation is accepted only after authenticated after screenshots and computed-style measurements prove:

- exactly one primary `h1` on authenticated destinations
- no raw i18n keys, backend stub strings, or technical enums
- canonical responsive filter, metric, and analysis grids
- no content hidden beneath the sticky application context bar
- no clipped sidebar navigation or horizontal document overflow
- coherent loading, empty, missing-session, and valid-data states

These acceptance checks passed for Optimization Trace and Workload Analytics at `1600x900`, `1366x768`, and `1024x768`. The previous broad 43-route visual-completion claim remains superseded by the narrower evidence-backed remediation result.
