# FRONTEND_SUPERIOR_ENGINEER_AUDIT.md

**Date**: 2026-05-22  
**Scope**: `frontend/src/App.tsx`, layout, pages, hooks, services, store, i18n, build state

---

## What The Frontend Currently Is

The EMS frontend is a React 18 SPA using:

- React Router
- React Query
- centralized API wrapper
- centralized i18n dictionaries
- role-aware shell, navigation, and protected routes

It is a real production-facing frontend, but it is also a migration-era frontend: active V2 pages coexist with tracked legacy pages, internal docs, and partially wired admin configuration surfaces.

---

## Confirmed Strengths

- **Role-aware routing is strong**: `App.tsx` clearly gates routes by role and uses a common `GuardedPage` pattern.
- **Shell consistency exists**: `AppShell` centralizes sidebar, topbar, theme, and mobile bottom navigation.
- **Auth state is centralized**: `auth.store.tsx` handles bootstrap, refresh, session clearing, and logout behavior coherently.
- **API access is mostly centralized**: `services/api.ts` standardizes `credentials: "include"`, error parsing, and unauthorized events.
- **i18n maturity is high**: `check:i18n` passed with `1688` keys in both `en.ts` and `th.ts`.
- **Build health is good**: `npm run build` passed successfully.
- **Lazy loading is used for heavier enterprise pages**: analytics, audit explorer, governance, operational health, and related pages are dynamically imported.

---

## High-Priority Findings

| Priority | Finding | Evidence | Risk |
|---|---|---|---|
| High | Active app routes no longer match some tracked legacy pages and internal frontend docs | `App.tsx` routes `/settings`, `/users`, `/workflow`, `/swaps`, `/import` to V2 pages, while legacy files and `frontend/src/docs/EMS_SYSTEM_OVERVIEW.md` still describe the old path owners | Documentation and maintenance drift |
| High | Platform/faculty config surfaces are only partially wired | `useFacultyConfig.ts` contains a placeholder fetch to `/api/platform/faculty-configs/{id}`; backend active route is `/api/admin/platform-config`; admin snapshot returns empty arrays with a note that DB registries are not fully wired | Feature appears more complete than it is |
| High | Frontend lacks real application-level unit/e2e coverage in repo source | No meaningful app test suite found outside `node_modules`; only `frontend/test-results/.last-run.json` is present | UI regressions rely on build + manual checking |
| Medium | Main bundle is large | Build emitted a `754.73 kB` main JS chunk warning | Performance risk on lower-powered pilot devices |
| Medium | Raw string debt remains | `check:i18n:raw` warns about raw string candidates; build passes but string cleanup is not finished | UX consistency / localization debt |

---

## Maintainability Findings

| Area | Evidence | Impact | Recommendation |
|---|---|---|---|
| Large page components | `Checkins.tsx`, `MyExam.tsx`, `Optimizer.tsx`, `WorkflowV2.tsx`, `RoomManagementV2.tsx`, `HistoricalSchedules.tsx` are among the largest pages | Review and regression cost stays high | Continue extracting domain hooks and presenters |
| Legacy/V2 coexistence | legacy pages remain tracked even though routes use V2 pages | Onboarding confusion | Archive inactive legacy pages after confirmation |
| Mixed service maturity | some services use `api.ts`, while placeholder faculty hooks still call `fetch()` directly | API behavior inconsistency | Route all network calls through shared API layer |
| Internal frontend docs drift | `frontend/src/docs/EMS_SYSTEM_OVERVIEW.md` no longer matches live routes | Future engineers may trust the wrong source | Update or archive internal frontend docs |
| Naming overlap | `platformConfig.service.ts` and `platformConfiguration.service.ts` are easy to confuse | Higher mistake rate | Consolidate naming around current supported surface |

---

## UX / Interaction Observations

- Loading and empty states are better than average:
  - `ProtectedRoute` uses skeletons
  - `DataTable` has explicit loading and empty handling
  - `EmptyState` is reused
- Role-aware navigation and role theming are meaningful strengths.
- Humanization assets are extensive and useful.

Remaining issues:

- large admin/operations pages still carry high cognitive load
- some legacy pages are likely less aligned with the enterprise shell pattern than the newer pages
- bundle size and raw string debt can still affect user experience even when routing and shell quality are good

---

## Dead / Legacy Surface Observations

High-confidence legacy candidates:

- `Settings.tsx`
- `Users.tsx`
- `Workflow.tsx`
- `Swaps.tsx`
- `Import.tsx`

These are tracked, but current routing uses:

- `SettingsV2Page`
- `UsersV2Page`
- `WorkflowV2Page`
- `SwapsV2Page`
- `ImportV2Page`

This is a maintainability issue even if it does not break runtime behavior today.

---

## Frontend Production Readiness

### Strong

- route gating
- auth bootstrap
- API wrapper
- i18n parity
- build health
- reusable shell and table/empty-state primitives

### Weak

- limited automated UI testing
- stale internal docs
- partial admin/platform config wiring
- large chunk size
- mixed legacy/V2 surface area

---

## Recommended Refactors

### Must fix before Faculty LAN pilot

1. clearly label unfinished platform/faculty config surfaces as non-pilot features
2. correct or archive `frontend/src/docs/EMS_SYSTEM_OVERVIEW.md`
3. confirm which legacy pages are safe to archive because routes already point elsewhere

### Should fix after pilot

1. reduce the main bundle size
2. continue page decomposition for the largest operational pages
3. add real frontend unit and/or e2e coverage
4. standardize all network calls through `services/api.ts`

### Leave as is for now

- core shell architecture
- auth store shape
- React Query foundation
- i18n provider and dictionaries
