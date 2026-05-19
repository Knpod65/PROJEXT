# FRONTEND_VIEWMODEL_AUDIT

## Heavy Orchestration Pages Identified

### GovernanceCockpit.tsx
- Heavy useState for filters, periods, sessions
- Inline fetch + polling logic
- Inline label mapping for governance status
- Duplicated loading/error/empty handling

### OptimizationTraceExplorer.tsx
- Complex timeline + diff state
- Inline data transformation for trace rows
- Permission checks mixed with render logic

### AuditExplorer.tsx
- Tab + filter state orchestration
- Inline session/row loading
- Status label formatting inline

### ExecutiveAnalytics.tsx
- Metric cards + chart data derivation
- Filter state + summary calculations
- Loading coordination across multiple async sources

### PlatformConfiguration.tsx + OperationalHealth.tsx
- Table + card model building inline
- Status/severity formatting repeated
- Filter/search state mixed with data

### ExportCenter.tsx
- Multiple export action handlers
- Workload/distribution data loading
- Admin-only conditional rendering logic

### Settings.tsx + SettingsV2.tsx
- Form draft state + save orchestration
- Section modeling mixed with UI

## Recommended Extraction Pattern (Laravel-style)

- Page (View): only JSX + minimal props
- Hook (ViewModel/Controller): all state, effects, derived data, action handlers
- Service: API calls only
- Utils/Presenters: pure formatting/label functions
- Types: DTO contracts

## Next Slices

U1-s2: Governance + Trace ViewModels
U1-s3: Analytics + Config + Health
U1-s4: Export + Settings
U1-s5: Shared Presenters
U1-s6: Docs + Final Validation

This audit was generated as part of U1-s1.