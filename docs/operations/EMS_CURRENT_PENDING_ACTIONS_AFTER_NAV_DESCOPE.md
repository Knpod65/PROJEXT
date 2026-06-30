# EMS Current Pending Actions After Navigation De-Scope

**Date:** 2026-06-30  
**Baseline commit:** `b958230 docs(scope): record EMS navigation de-scope phase B validation`

## Pending Actions

1. Complete Thai-safe export encoding/font pass for remaining export surfaces.
2. Finance review of the Supporting Finance Roster five-sheet XLSX.
3. Human decision required for the Supporting Finance Roster format:
   - `ACCEPT_SUPPORTING_FINANCE_ROSTER_FORMAT`
   - `ACCEPT_WITH_MINOR_FORMAT_NOTES`
   - `REQUEST_SUPPORTING_ROSTER_REVISION`
   - `HOLD_PENDING_FINANCE_REVIEW`
4. Decide whether Historical Schedules should remain admin-only or become visible to more roles for fairness review.
5. Decide later whether internal diagnostics pages should be merged, archived, or kept as direct-URL-only tools.
6. Keep the `/print-queue` P2 developer-console note as watch-only unless a visible user issue appears.
7. Do not implement final payment approval, final authorization, or official-final export yet.

## Current State To Preserve

| Area | Current decision |
| ---- | ---------------- |
| Navigation de-scope | Eight non-core diagnostics/enterprise pages hidden from main sidebar. |
| Hidden routes | Routes remain active by direct URL under existing guards. |
| Historical Schedules | Still visible for existing `admin` role only. |
| Payment documents | Draft/supporting/review-only; no final authorization. |
| Backend/API | No changes in navigation de-scope or localhost smoke pass. |
| Route guards and role permissions | No changes in navigation de-scope or localhost smoke pass. |

## Watch Items

| Item | Watch condition | Action |
| ---- | --------------- | ------ |
| Browser visual smoke | In-app browser automation was unavailable in this session. | Repeat visual role smoke with browser tooling before pilot signoff. |
| Secretary live smoke | Local DB has a secretary user, but no documented working demo password was available. | Provide/confirm secretary demo credential before role-specific UAT. |
| Hidden diagnostics | Users may request one back in nav after real pilot use. | Restore by removing `hidden: true` for the specific nav entry. |
| `/rooms` route expectation | Current route is `/rooms-v2`; `/rooms` is not declared. | Use `/rooms-v2` in smoke scripts unless a route alias is intentionally added later. |

## Explicit Non-Goals

- Do not add final payment approval.
- Do not add final authorization.
- Do not add official-final export.
- Do not change payment calculations.
- Do not change scheduling or optimization logic.
- Do not touch teaching workload, Work H, opencourse, or coinstruc scope.
