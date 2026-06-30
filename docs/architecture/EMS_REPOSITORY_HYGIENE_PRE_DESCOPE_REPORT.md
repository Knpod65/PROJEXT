# EMS Repository Hygiene Pre-Descope Report

## Summary

Repository hygiene cleanup before navigation de-scoping. This pass classifies the dirty tree, removes accidental misplaced source artifacts, and keeps the canonical `useEffectiveRole` hook update. No navigation, route, backend, payment/export/review/settings, scheduling, optimization, role-permission, or final-authorization behavior is changed.

## Preflight

| Check | Result |
| ---- | ---- |
| Repository root | `C:/Users/DELL/Desktop/PROJEXT/opt/ems_system` |
| Branch | `main` |
| Starting HEAD | `cb4cc1a docs(scope): audit EMS route necessity and de-scope options` |
| Dirty tree | Matched reported pre-descope hygiene files |

## Classification

| Path | Current state | Classification | Action | Rationale |
| ---- | ------------- | -------------- | ------ | --------- |
| `frontend/src/hooks/useEffectiveRole.ts` | Modified tracked source | `VALID_SOURCE_COMMIT` | Keep and commit | Canonical hook, imported by active frontend code, delegates to `getEffectiveRole(user)`. |
| `frontend/src/hooks/PageSkeleton.tsx` | Untracked source in wrong folder | `DUPLICATE_SOURCE_REMOVE` | Remove | Canonical tracked component exists at `frontend/src/components/ui/PageSkeleton.tsx`; active imports use the canonical component path. The untracked hook-path copy also breaks TypeScript casing checks. |
| `docs/architecture/useEffectiveRole.ts` | Untracked TS source in docs | `DUPLICATE_SOURCE_REMOVE` | Remove | Duplicates the canonical hook under `frontend/src/hooks/useEffectiveRole.ts`; no active imports reference the docs path. |
| `docs/architecture/Import.tsx` | Untracked zero-byte TSX source in docs | `MISPLACED_SOURCE_REMOVE` | Remove | Canonical tracked page exists under `frontend/src/pages/Import.tsx`; docs must not contain source stubs. |
| `docs/architecture/PagePlaceholder.tsx` | Untracked zero-byte TSX source in docs | `MISPLACED_SOURCE_REMOVE` | Remove | Canonical tracked page exists under `frontend/src/pages/PagePlaceholder.tsx`; docs must not contain source stubs. |
| `docs/architecture/RoleDashboard.tsx` | Untracked zero-byte TSX source in docs | `MISPLACED_SOURCE_REMOVE` | Remove | Canonical tracked page exists under `frontend/src/pages/RoleDashboard.tsx`; docs must not contain source stubs. |
| `docs/architecture/Settings.tsx` | Untracked zero-byte TSX source in docs | `MISPLACED_SOURCE_REMOVE` | Remove | Canonical tracked page exists under `frontend/src/pages/Settings.tsx`; docs must not contain source stubs. |
| `docs/architecture/Swaps.tsx` | Untracked zero-byte TSX source in docs | `MISPLACED_SOURCE_REMOVE` | Remove | Canonical tracked page exists under `frontend/src/pages/Swaps.tsx`; docs must not contain source stubs. |
| `docs/architecture/Users.tsx` | Untracked zero-byte TSX source in docs | `MISPLACED_SOURCE_REMOVE` | Remove | Canonical tracked page exists under `frontend/src/pages/Users.tsx`; docs must not contain source stubs. |
| `docs/architecture/Workflow.tsx` | Untracked zero-byte TSX source in docs | `MISPLACED_SOURCE_REMOVE` | Remove | Canonical tracked page exists under `frontend/src/pages/Workflow.tsx`; docs must not contain source stubs. |
| `docs/architecture/useRoleDashboard.ts` | Untracked zero-byte TS source in docs | `MISPLACED_SOURCE_REMOVE` | Remove | Canonical tracked hook exists at `frontend/src/hooks/domain/useRoleDashboard.ts`; docs must not contain source stubs. |
| `docs/architecture/EMS_SYSTEM_OVERVIEW.md` | Untracked zero-byte markdown | `STALE_SCRATCH_REMOVE` | Remove | Empty accidental scratch file; not useful architecture documentation. |

## Validation

Validation commands for this hygiene pass:

- `cd frontend && npm run build`
- `npm run check:i18n`
- `npm run check:i18n:raw`
- `cd .. && git diff --check`
- `git status --short`

Expected result: frontend build passes after removing the duplicate hook-path `PageSkeleton`; i18n checks remain exit 0. Backend tests are not required because backend files are not touched.

## Guardrails

| Guardrail | Result |
| ---- | ---- |
| Navigation changed | NO |
| Routes removed | NO |
| Backend changed | NO |
| Payment/export/review/settings logic changed | NO |
| Scheduling/optimization logic changed | NO |
| Role permissions changed | NO |
| Final authorization added | NO |
