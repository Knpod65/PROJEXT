# UNUSED_AND_DUPLICATE_FILE_AUDIT.md

**Date**: 2026-05-22  
**Method**: `git ls-files`, route/import searches, backend router registration, frontend route registration, service/hook reference checks, and documentation cross-checks

---

## Summary

No runtime file was declared unused from a single search alone. The highest-confidence cleanup candidates are legacy frontend pages that are no longer routed by `App.tsx`, stale internal frontend docs, and generated artifacts that should not remain tracked.

---

## Audit Table

| File | Type | Classification | Evidence | Reference Found? | Risk | Recommendation |
|---|---|---|---|---|---|---|
| `frontend/src/pages/Settings.tsx` | Frontend page | Probably unused | `App.tsx` routes `/settings` to `SettingsV2Page`; search only found the page definition and its domain hook | No active route import | Medium | Archive or delete later after final manual check |
| `frontend/src/pages/Users.tsx` | Frontend page | Probably unused | `App.tsx` routes `/users` to `UsersV2Page`; search found only the page definition and stale internal docs | No active route import | Medium | Archive or delete later after manual review |
| `frontend/src/pages/Workflow.tsx` | Frontend page | Probably unused | `App.tsx` routes `/workflow` to `WorkflowV2Page`; search found only the page definition and stale internal docs | No active route import | Medium | Archive or delete later after manual review |
| `frontend/src/pages/Swaps.tsx` | Frontend page | Probably unused | `App.tsx` routes `/swaps` to `SwapsV2Page`; `swap.service.ts` calls `/swaps2/*`, not legacy swap UI | No active route import | Medium | Archive or delete later after manual review |
| `frontend/src/pages/Import.tsx` | Frontend page | Probably unused | `App.tsx` routes `/import` to `ImportV2Page`; search found only page definition | No active route import | Low | Archive after confirming no hidden navigation path depends on it |
| `frontend/src/pages/RoleDashboard.tsx` | Frontend page | Probably unused | No route in `App.tsx`; search found only the page itself plus its hook/service types | No route import | Low | Archive or leave as historical reference pending human review |
| `frontend/src/pages/PagePlaceholder.tsx` | Frontend utility page | Probably unused | Search found only the component definition; no route or component import found in current frontend source | No runtime import found | Low | Delete later or keep only if planned for future scaffolding |
| `frontend/src/hooks/domain/useRoleDashboard.ts` | Frontend hook | Probably unused | Only referenced by `RoleDashboard.tsx`, which is not routed | Indirect only | Low | Archive together with `RoleDashboard.tsx` |
| `frontend/src/hooks/useFacultyConfig.ts` | Frontend hook | Possibly unused | No import found in active routed pages; uses placeholder direct fetch to `/api/platform/faculty-configs/{id}` | No active page reference found | Medium | Keep for now, but treat as unfinished / non-production |
| `frontend/src/hooks/useFacultyPolicy.ts` | Frontend hook | Possibly unused | No import found in active routed pages; depends on endpoints not surfaced in current backend router map | No active page reference found | Medium | Keep for now, but treat as unfinished / non-production |
| `frontend/src/services/platformConfig.service.ts` | Frontend service | Possibly unused | Only used by faculty config hooks that are not part of the current routed app | Indirect only | Medium | Keep if multi-faculty work continues; otherwise fold into a future cleanup pass |
| `frontend/src/docs/EMS_SYSTEM_OVERVIEW.md` | Internal doc | Documentation-only, stale | Claims legacy pages remain active on routes now served by V2 pages; conflicts with live `App.tsx` routing | Yes, but conflicts with code | Medium | Update or archive; do not use as current source of truth |
| `frontend/test-results/.last-run.json` | Generated artifact | Probably unused / generated-only | Machine-generated test runner state file; no app import path | No | Low | Untrack in a later housekeeping pass |
| `backend/routers/swaps.py` | Backend router | Used, but legacy runtime | Included by `main.py` at `/api/swaps`; current frontend uses `/api/swaps2` through `swap.service.ts` | Yes, runtime registration exists | Medium | Keep for compatibility until usage is measured; mark as legacy route family |
| `backend/routers/imports.py` | Backend router | Used, but legacy runtime | Included by `main.py` if import succeeds; current frontend `/import` page uses `ImportV2Page` | Yes, runtime registration exists | Medium | Keep for compatibility until data confirms it is unused |
| `backend/seed_new.py` | Backend script | Possibly unused | Tracked script with no reference found in runtime routing or docs used during this audit | No meaningful runtime refs found | Low | Human review; likely archive or remove later |
| `backend/migrate_*.py` scripts | Backend scripts | Script-only | Referenced by docs and manual migration use, not by runtime | Yes, docs reference them | Low | Keep, but classify clearly as manual migration tooling |
| `backend/historical_schedule_import.py` | Backend support module | Used | Imported by `backend/routers/historical_schedules.py` and `import_historical_schedule_2_2568.py` | Yes | Low | Keep |

---

## Duplicate Or Overlapping Surfaces

| Area | Evidence | Risk | Recommendation |
|---|---|---|---|
| Legacy page vs. V2 page pairs | `Settings`, `Users`, `Workflow`, `Swaps`, `Import` have legacy source files while live routes point to V2 pages | Drift and maintenance duplication | Standardize on the active route implementation and archive unused legacy pages |
| Platform config service split | `platformConfig.service.ts` and `platformConfiguration.service.ts` represent related but different maturity levels | Confusing developer experience | Merge naming and clearly mark unfinished faculty-config endpoints |
| Internal frontend docs vs. code | `frontend/src/docs/EMS_SYSTEM_OVERVIEW.md` still describes legacy routing | Documentation drift | Replace with a route map generated from current `App.tsx` if the doc is retained |
| Auth / permission logic layering | `auth_utils.py` and `permissions.py` both contain role-related behavior | Policy drift risk | Consolidate toward one clearly authoritative permission surface |

---

## Confidence Notes

- `Confirmed unused` was not assigned to runtime code unless both route/import evidence and a second context check agreed.
- Legacy backend routers were **not** marked unused because `main.py` still registers them.
- Generated artifacts were treated separately from code so that cleanup recommendations stay safe.
