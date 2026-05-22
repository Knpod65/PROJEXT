# DRY_AND_MAINTAINABILITY_AUDIT.md

**Date**: 2026-05-22

---

## Summary

EMS has already invested in consolidation through shared services, shared UI, i18n, and common auth helpers. The largest remaining DRY problems are not basic syntax duplication; they are **parallel legacy surfaces**, **split authority between old and new abstractions**, and **partial migrations that leave multiple valid-looking ways to do the same thing**.

---

## DRY / Maintainability Table

| Area | Duplication Found | Evidence | Risk | Suggested Consolidation | Priority |
|---|---|---|---|---|---|
| Frontend page pairs | Legacy and V2 pages coexist for settings, users, workflow, swaps, import | `App.tsx` routes active paths to V2 pages while legacy files remain tracked | Onboarding confusion and inconsistent fixes | Standardize one routed implementation per capability | Must fix before pilot |
| Platform config surface | `platformConfig.service.ts` vs. `platformConfiguration.service.ts`, plus placeholder hooks | Similar domain expressed across different maturity levels | Incomplete features appear production-ready | Collapse naming and clearly fence unfinished faculty-config work | Must fix before pilot |
| Auth / permission authority | `auth_utils.py` and `permissions.py` both carry role logic | Overlapping helper functions and permission concepts | Policy drift risk | Keep runtime decisions in one authoritative permission layer | Should fix after pilot |
| Startup / environment hardening | `config/settings.py` and `security.py` validate secrets differently | `ENVIRONMENT` vs. `ENV`, `50` chars vs. `32` chars | Hard-to-debug deploy behavior | Create one canonical production hardening policy | Must fix before pilot |
| Health surfaces | `/health` root endpoint plus `/api/health/*` router | Two health entry families with different behavior | Probe policy drift | Document one external probe policy and one internal readiness policy | Should fix after pilot |
| Direct fetch vs shared API wrapper | Faculty config hooks still use raw `fetch()` while most app code uses `api.ts` | Inconsistent unauthorized/error behavior | Harder frontend troubleshooting | Route all HTTP through shared request wrapper | Should fix after pilot |
| Settings UI lineage | `Settings.tsx`, `SettingsV2.tsx`, `useSettingsPage`, `useSettingsData`, `useSettingsV2Page` | Multiple abstraction layers for one admin feature | Makes fixes more expensive | Retire the legacy settings path after validation | Should fix after pilot |
| Swaps workflow lineage | `swaps.py` + `swaps_v2.py`, `Swaps.tsx` + `SwapsV2.tsx` | Runtime and UI carry old/new workflows at once | Policy and behavior drift | Measure usage, then retire old path | Should fix after pilot |
| Workflow lineage | `Workflow.tsx` + `WorkflowV2.tsx` | Only V2 route is active, legacy page remains | Dead-code drift | Archive unused workflow page | Should fix after pilot |
| Internal docs vs live code | `frontend/src/docs/EMS_SYSTEM_OVERVIEW.md` conflicts with `App.tsx` | One doc says legacy routes are active; code says otherwise | Future incorrect changes | Replace with code-derived route map or archive | Must fix before pilot |
| Formatting / presenter overlap | existing docs mention overlap with legacy `utils/format.ts` | Confirmed by historical architecture docs and mixed page patterns | Incremental duplication | Continue presenter/formatter extraction in largest pages | Nice to have |
| Loading / empty / error patterns | Shared primitives exist, but large pages still implement local orchestration | `DataTable`, `EmptyState`, `Skeleton` exist, yet large page files still carry bespoke state | Not a correctness issue, but more review effort | Continue domain-hook extraction | Leave as is |

---

## Areas That Are Already Reasonably DRY

- centralized API request wrapper
- shared i18n dictionaries
- shell layout (`AppShell`, sidebar, topbar, mobile nav)
- shared data table and empty-state components
- backend service / repository / serializer separation in many areas

These should be preserved, not rewritten.

---

## Audit Judgment

The biggest maintainability threat is not lack of architecture. It is **architecture drift across generations of the same feature**.

The safest cleanup strategy is:

1. decide which surfaces are canonical
2. mark the rest as legacy
3. archive or remove only after route and dependency confirmation
