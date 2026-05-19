# I18N Audit Report — EMS Frontend

**Date:** 2026-05-19  
**Scope:** `frontend/src/` (pages, components, hooks, services)

## Summary

The EMS frontend has partial i18n coverage. Many new pages added in D4/D5 still contain raw Thai and English strings instead of using the `translate()` helper from `@/i18n`.

## Raw String Hotspots (High Severity)

| File | Raw Strings Found | Recommended Fix |
|------|-------------------|-----------------|
| `frontend/src/pages/ExecutiveAnalytics.tsx` | "Overall Health", "Risk Band", "Optimization Quality" | Wrap in `translate()` |
| `frontend/src/pages/GovernanceCockpit.tsx` | "Blockers", "Publication Ready", "Pending Approvals" | Wrap in `translate()` |
| `frontend/src/pages/OptimizationTraceExplorer.tsx` | "Trace Events", "Candidates", "Constraint Hits" | Wrap in `translate()` |
| `frontend/src/pages/OperationalHealth.tsx` | "Backend Health", "Analytics Health", "Queue Status" | Wrap in `translate()` |
| `frontend/src/pages/AuditExplorer.tsx` | "Audit Events", "Governance Timeline", "Lifecycle Timeline" | Wrap in `translate()` |
| `frontend/src/pages/PlatformConfiguration.tsx` | "Faculty Config", "Workload Policy", "Integration Contracts" | Wrap in `translate()` |

## Repeated Strings (Medium Severity)

- "Loading..." appears 37 times inline (should use `<LoadingState />`)
- "No data available" appears 12 times with slight variations
- Error messages like "Something went wrong" / "เกิดข้อผิดพลาด" are duplicated

## Missing Translation Keys

`src/i18n/en.ts` and `th.ts` are missing keys for:
- `governance.blocker_count`
- `analytics.overall_health_score`
- `optimization.trace_quality_score`
- `common.loading`
- `common.no_data`

## Recommended i18n Structure

```
src/i18n/
├── en.ts
├── th.ts
└── namespaces/
    ├── common.ts
    ├── governance.ts
    ├── analytics.ts
    ├── optimization.ts
    └── audit.ts
```

## Script Created

`frontend/scripts/check-i18n-coverage.js` — scans for raw strings and reports missing keys.

Add to `package.json`:
```json
"check:i18n:coverage": "node scripts/check-i18n-coverage.js"
```

## Next Steps

1. Run `npm run check:i18n:coverage`
2. Wrap remaining raw strings in `translate()`
3. Add missing keys to both language files
4. Enforce via CI (fail on new raw strings in new pages)

**Status:** Audit complete. Remediation work deferred to I1 phase.