# UNUSED_FILE_ACTION_PLAN.md

**Date**: 2026-05-22  
**Source**: `UNUSED_AND_DUPLICATE_FILE_AUDIT.md`  
**Rule**: No files deleted in this pass. Action plan only.

---

## Frontend Legacy Pages

| File | Confidence | Action Plan | Rationale |
|------|-----------|------------|-----------|
| `frontend/src/pages/Settings.tsx` | Probable — no active route in `App.tsx`; `/settings` goes to `SettingsV2Page` | **Archive** after confirming `SettingsV2Page` is complete and no hidden nav link references `Settings.tsx` | V2 page is active; legacy page is dead code until proven otherwise |
| `frontend/src/pages/Users.tsx` | Probable — `/users` → `UsersV2Page` | **Archive** after confirming same | V2 page is active |
| `frontend/src/pages/Workflow.tsx` | Probable — `/workflow` → `WorkflowV2Page` | **Archive** after confirming same | V2 page is active |
| `frontend/src/pages/Swaps.tsx` | Probable — `/swaps` → `SwapsV2Page`; API uses `/swaps2/*` | **Archive** after confirming same | V2 page and V2 API active |
| `frontend/src/pages/Import.tsx` | Low-Medium — `/import` → `ImportV2Page` | **Archive** after confirming no hidden nav path | V2 page active; legacy page likely dead |
| `frontend/src/pages/RoleDashboard.tsx` | Low — no route in `App.tsx` | **Archive** together with `useRoleDashboard.ts`; treat as historical if active role dashboards confirmed elsewhere | No runtime import found |
| `frontend/src/pages/PagePlaceholder.tsx` | Low — no route or component import | **Archive or delete later** if planned scaffolding is near | Currently unused utility |

## Frontend Hooks / Services

| File | Confidence | Action Plan | Rationale |
|------|-----------|------------|-----------|
| `frontend/src/hooks/domain/useRoleDashboard.ts` | Low — only referenced by `RoleDashboard.tsx` | **Archive** together with the page | Indirectly unused |
| `frontend/src/hooks/useFacultyConfig.ts` | Medium — no active routed page reference | **Keep** for now if multi-faculty work continues; otherwise **archive** | Unfinished, not on critical path |
| `frontend/src/hooks/useFacultyPolicy.ts` | Medium — depends on unsettled endpoints | **Keep** for now; review after pilot | Non-blocking |
| `frontend/src/services/platformConfig.service.ts` | Medium — only used by unfinished hooks | **Keep** alongside hooks; merge or fold later | Partial service split |

## Frontend Internal Docs

| File | Confidence | Action Plan | Rationale |
|------|-----------|------------|-----------|
| `frontend/src/docs/EMS_SYSTEM_OVERVIEW.md` | High — conflicts with live `App.tsx` routing | **Update or archive; replace with current route map** if retained | Describes legacy routing as active |

## Generated Artifacts

| File / Path | Confidence | Action Plan | Rationale |
|------------|-----------|------------|-----------|
| `frontend/test-results/.last-run.json` | High — machine-generated test runner state | **Untrack in a later housekeeping pass** | No app import path |

## Backend Legacy Routers

| File | Confidence | Action Plan | Rationale |
|------|-----------|------------|-----------|
| `backend/routers/swaps.py` | High — registered; frontend uses `/swaps2/*` | **Keep for backward compatibility; mark as legacy** until traffic confirms inactivity | Used at runtime; not yet safe to remove |
| `backend/routers/imports.py` | Medium — conditionally included; frontend uses `ImportV2Page` | **Keep for compatibility; mark as legacy** | Same as above |

## Backend Scripts

| File | Confidence | Action Plan | Rationale |
|------|-----------|------------|-----------|
| `backend/seed_new.py` | Low — no runtime ref found | **Human review required** (likely archive) | Probable dead code |

**Rule for all items**: No file is marked for deletion in this pass. Each item should be reviewed by the relevant owner after the pilot has produced traffic evidence confirming inactivity.

---

**End of UNUSED_FILE_ACTION_PLAN.md**