# Frontend MVC-Style Guide
## EMS Academic Operations Platform - 2026-05-12

> Objective: map the Laravel "view/controller/model" mindset into the current React + TypeScript frontend without changing frameworks.

---

## 1. Layer Mapping

| Laravel concept | EMS frontend equivalent | Responsibility |
|---|---|---|
| View | page/component JSX | Render data and trigger callbacks |
| Controller | custom hook or page-level orchestration block | Load data, handle actions, manage local page state |
| Model / repository | service module under `frontend/src/services/*` | Talk to backend APIs and return typed data |
| AuthMiddleware view gate | route guard + `permissions.ts` + auth store | Decide whether the UI path is visible or actionable |

---

## 2. Responsibility Standard

### Pages
Pages should:
- decide whether the user may access the route
- compose cards, tables, and sections
- wire hooks into presentational components

Pages should not:
- call `fetch()` directly
- duplicate backend permission logic inline
- own large data-shaping blocks when a hook can do it once

### Hooks
Hooks should:
- orchestrate page-level loading, error, mutation, and filter state
- call service modules
- expose stable UI-ready state to pages

Hooks should not:
- render JSX
- know layout details

### Services
Services should:
- be the only layer that talks to backend endpoints
- wrap `api.ts`
- return typed payloads

Services should not:
- hold view state
- decide page layout

### Components
Components should:
- render props
- emit events
- stay mostly free of network knowledge

Components should not:
- call backend APIs directly except in rare, strongly bounded infrastructure widgets

---

## 3. Current EMS Frontend Audit

### Already aligned
- `frontend/src/services/api.ts` centralizes request building, credentials, and error parsing.
- `frontend/src/services/auth.service.ts` and `frontend/src/store/auth.store.tsx` create a clean auth/session flow.
- `frontend/src/utils/permissions.ts` provides a growing semantic permission layer.
- Several pages already use controller-like hooks such as `useAsyncData`, `useRoomOperationsData`, `useUsersData`, and `usePrintQueueData`.
- **U1 COMPLETE:** Enterprise pages now use domain hooks: GovernanceCockpit, OptimizationTraceExplorer, AuditExplorer, ExecutiveAnalytics, PlatformConfiguration, OperationalHealth, ExportCenter, Settings, SettingsV2.

### Partially aligned
- Many pages consume services correctly but still contain large controller blocks internally.
- Some hooks still contain direct role mapping logic that should move into shared helpers.
- Components are mostly presentation-focused, but some page-local sections inside large pages should become reusable components.

### Not aligned yet
- `Checkins.tsx` (`680` lines)
- `MyExam.tsx` (`590` lines)
- `Optimizer.tsx` (`563` lines)
- `RoomManagementV2.tsx` (`554` lines)
- `WorkflowV2.tsx` (`548` lines)
- `External.tsx` (`529` lines)

These pages still combine route composition, data orchestration, transformation logic, and view rendering in one file.

---

## 4. Good Current Examples

### Service discipline
- `frontend/src/services/api.ts`
- `frontend/src/services/auth.service.ts`
- `frontend/src/services/schedule.service.ts`

These files already resemble a repository/client layer in Laravel terms.

### Hook/controller discipline
- `frontend/src/hooks/useAsyncData.ts`
- `frontend/src/hooks/useRoomOperationsData.ts`
- `frontend/src/hooks/usePrintQueueData.ts`
- `frontend/src/hooks/useUsersData.ts`
- `frontend/src/hooks/domain/useGovernanceCockpit.ts`
- `frontend/src/hooks/domain/useExecutiveAnalyticsPage.ts`

These are the best starting patterns for future page thinning.

### Auth/session discipline
- `frontend/src/store/auth.store.tsx`

This file already behaves like a centralized auth/session controller for the frontend.

---

## 5. What Should Move Where

### From page to hook

| Current page | Move into hook |
|---|---|
| `Checkins.tsx` | check-in action orchestration, QR/session refresh, filter state, mutation loading states |
| `Optimizer.tsx` | session bootstrap, unavailability CRUD orchestration, schedule summary transformations |
| `MyExam.tsx` | submission step orchestration, modal state, upload/retry flows |
| `RoomManagementV2.tsx` | room form state, availability filtering, mutation orchestration |
| `WorkflowV2.tsx` | workflow session loading, status reduction, signing action state |
| `External.tsx` | preview/confirm flow orchestration and allocation summary shaping |

### From page to service

| Current concern | Target service |
|---|---|
| repeated schedule fetch and filter setup | `schedule.service.ts` or a dedicated schedule query service |
| workflow init/sign/open-swap calls | keep in `workflow.service.ts`, expand response-specific helpers if needed |
| document export URL building | keep in `documents.service.ts` |
| exam manager CRUD and reassignment | keep in `exam-manager.service.ts`, expand as page logic is extracted |

### From page to component

| Current page section | Candidate component |
|---|---|
| Optimizer unavailability panel | `components/optimizer/UnavailabilityPanel.tsx` |
| Workflow signature summary cards | `components/workflow/SignatureSummary.tsx` |
| MyExam step sections | `components/submissions/*` step panels |
| External allocation preview cards | `components/external/*` preview sections |

---

## 6. Role / Permission Rendering Standard

### Standard
- Use `frontend/src/utils/permissions.ts` for semantic access rules.
- Use `frontend/src/utils/roles.ts` only for low-level role extraction helpers.
- Let pages ask "can this user do X?" instead of checking raw role strings.

### Examples

Preferred:

```ts
if (canManageOperationalWork(user)) {
  // render ops actions
}
```

Avoid:

```ts
if (effectiveRole === "admin" || effectiveRole === "staff") {
  // duplicated role logic
}
```

### Current remaining cleanup targets
- `frontend/src/pages/Checkins.tsx`
- `frontend/src/pages/MyExam.tsx`
- `frontend/src/pages/Optimizer.tsx`
- `frontend/src/pages/RoomManagementV2.tsx`
- `frontend/src/pages/WorkflowV2.tsx`
- `frontend/src/pages/External.tsx`
- `frontend/src/hooks/useSwapsData.ts`

---

## 7. Table / Layout DRY Standard

### Reuse these patterns
- `Card`
- `EmptyState`
- `Skeleton`
- `table-wrap`
- `data-table`

### Standard expectations
- loading state must use one shared visual pattern
- empty state must use one shared component pattern
- tables should prefer shared wrappers and consistent compact/normal variants
- page sections should become reusable subcomponents before introducing new CSS systems

### Mobile / responsive rule
- put responsive concerns in the shared section/component layer where possible
- do not leave every page to invent its own table overflow strategy

---

## 8. Recommended Frontend Migration Order

1. `Checkins.tsx`
2. `Optimizer.tsx`
3. `MyExam.tsx`
4. `WorkflowV2.tsx`
5. `RoomManagementV2.tsx`
6. `External.tsx`

This order balances size, operational importance, and the ability to reuse the resulting hooks/components across other pages.

---

## 9. Non-Negotiable Guardrails

- Do not move API calls into components.
- Do not reintroduce raw `fetch()` inside pages.
- Do not bypass `permissions.ts` for routine role gating.
- Do not mix major UI redesign with controller extraction.
- Preserve current UX and workflow semantics while restructuring.