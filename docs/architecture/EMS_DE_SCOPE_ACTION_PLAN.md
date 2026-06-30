# EMS De-Scope Action Plan

**Date:** 2026-06-30
**Purpose:** Safe, phased plan to reduce EMS scope bloat from the navigation and eventually from the codebase. No code changes in this pass.

---

## Guiding Principles

1. **Never delete before hiding.** Always hide first, observe, then archive, then remove.
2. **Routes remain active throughout.** Admin can always navigate by direct URL.
3. **Backend is never changed in de-scoping.** Only frontend nav visibility changes.
4. **Each phase is independently reversible.**
5. **De-scoping does not mean removal.** It means making the app feel focused for the users who need it.

---

## Phase Overview

| Phase | Timing | What Changes | Risk | Files Affected |
|-------|--------|-------------|------|----------------|
| A | NOW (this pass) | Docs only — no code | None | docs/architecture/ |
| B | After user approval | Hide 8 pages from sidebar | Low | navigation.ts only |
| C | Post-pilot preparation | Merge/simplify nav groups | Medium | navigation.ts, App.tsx |
| D | Post-pilot | Archive legacy files; clean misplaced artifacts | Low | pages/, docs/architecture/ |
| E | After pilot + confirmation | Final removal of confirmed unused routes | Medium | pages/, App.tsx, navigation.ts |

---

## Phase A — No-Code Decision (Current Pass)

### What Happens
- This audit is written and committed (docs only)
- User reviews 8 documents
- User answers decision questions in `EMS_SCOPE_RECENTER_DECISION_QUESTIONS.md`
- User confirms which pages to hide, which to keep accessible, which to defer

### Risk
**None.** Docs-only. No code changed. Fully reversible.

### Rollback Plan
N/A — no changes to revert.

### Files Affected
- `docs/architecture/EMS_ORIGINAL_INTENT_RECENTER_SOURCE_REVIEW.md` (new)
- `docs/architecture/EMS_ROUTE_NECESSITY_AUDIT_MATRIX.md` (new)
- `docs/architecture/EMS_CORE_PRODUCT_SCOPE_PROPOSAL.md` (new)
- `docs/architecture/EMS_SCOPE_BLOAT_AND_THEME_DRIFT_REPORT.md` (new)
- `docs/architecture/EMS_SIMPLIFIED_NAVIGATION_PROPOSAL.md` (new)
- `docs/architecture/EMS_ROLE_BASED_SCOPE_SIMPLIFICATION.md` (new)
- `docs/architecture/EMS_DE_SCOPE_ACTION_PLAN.md` (this file)
- `docs/architecture/EMS_SCOPE_RECENTER_DECISION_QUESTIONS.md` (new)

### Validation
- `git status` after commit shows only pre-existing dirty items
- 8 new `.md` files exist in `docs/architecture/`
- No `.tsx`, `.ts`, `.py` files changed

---

## Phase B — Navigation Cleanup (After Approval)

### What Happens

Set `hidden: true` on 8 page entries in `frontend/src/config/navigation.ts`:

```typescript
// Pages to set hidden: true (in navigation.ts appPages array)
// 1. Admin Intelligence Dashboard — key: "adminIntelligenceDashboard" (or similar)
// 2. Executive Analytics — key: "analytics" 
// 3. Governance Cockpit — key: "governance"
// 4. Operational Health — key: "operationalHealth"
// 5. Audit Explorer — key: "auditExplorer"
// 6. Optimizer Trace — key: "optimizerTrace"
// 7. Platform Configuration — key: "platformConfig"
// 8. Import Audit — key: "importAudit"
```

**Also consider in Phase B:**
- Expand `historical-schedules` role access to include `staff` and `esq_head`/`secretary` (not just admin)
- Confirm that `hidden: true` pages remain accessible to admin by direct URL (they do — `hidden` only affects sidebar rendering, not routing)

### Risk
**Low.** Only `navigation.ts` changes. Routes remain active. No component changes.

### Rollback Plan
`git revert <commit>` — restores `navigation.ts` to previous state. All pages reappear in sidebar within seconds of deployment.

### Files Affected
- `frontend/src/config/navigation.ts` only

### Validation
For each role (admin, esq_head, secretary, dept_supervisor, staff, teacher, print_shop):
1. Log in as that role
2. Confirm sidebar shows only expected items
3. Confirm `/admin-intelligence-dashboard`, `/analytics`, `/governance`, `/operational-health`, `/audit-explorer`, `/optimizer-trace`, `/platform-config`, `/import-audit` all still render correctly when navigated to by direct URL as admin
4. Confirm no broken links in any currently visible nav item
5. Run existing backend tests — must pass (no backend changes)

---

## Phase C — Merge and Simplify (Post-Pilot Preparation)

### What Happens
1. **Workload nav consolidation:** The three workload routes (`/workload-duty-analytics`, `/duty-workload`, `/my-workload`) should appear as a single "ภาระงานคุมสอบ" nav entry that routes to the correct path per role. Currently the nav shows one entry per route — these are role-filtered anyway, so each role only sees one. The simplification is in the label and grouping, not the routes.

2. **Consider merging Governance Cockpit blocker summary into Dashboard:** If the Governance Cockpit's primary value is showing blocker counts, those could be surfaced as Dashboard cards. This would allow permanent removal of the `/governance` nav item without losing the data.

3. **Nav group consolidation:** Consider merging "operations" group items into cleaner functional groups matching the Thai labels in the navigation proposal.

### Risk
**Medium.** Route changes could break existing links. Nav group changes require regression check across all roles.

### Rollback Plan
`git revert <commit>` — restores `navigation.ts` and `App.tsx`. All nav groups return to previous state.

### Files Affected
- `frontend/src/config/navigation.ts`
- `frontend/src/App.tsx` (possibly, for route alias cleanup)

### Validation
- All 8 roles can reach their needed pages
- Direct URL navigation to all routes still works
- Mobile bottom nav unchanged
- No 404 errors on any previously working route

---

## Phase D — Archive Legacy Files (Post-Pilot)

### What Happens
1. **Remove misplaced source files from `docs/architecture/`:**
   These are React/TS files accidentally placed in the docs directory. They are untracked. They should be deleted (or moved back to their correct location if they contain unreleased work).
   ```
   docs/architecture/Import.tsx
   docs/architecture/PagePlaceholder.tsx
   docs/architecture/RoleDashboard.tsx
   docs/architecture/Settings.tsx
   docs/architecture/Swaps.tsx
   docs/architecture/Users.tsx
   docs/architecture/Workflow.tsx
   docs/architecture/useEffectiveRole.ts
   docs/architecture/useRoleDashboard.ts
   ```

2. **Archive legacy page files (after confirming no active routes point to them):**
   ```
   frontend/src/pages/Import.tsx        → verify /import → ImportV2Page, then delete
   frontend/src/pages/Swaps.tsx         → verify /swaps → SwapsV2Page, then delete
   frontend/src/pages/Workflow.tsx      → verify /workflow → WorkflowV2Page, then delete
   frontend/src/pages/Settings.tsx      → verify /settings → SettingsV2Page, then delete
   frontend/src/pages/Users.tsx         → verify /users → UsersV2Page, then delete
   frontend/src/pages/RoleDashboard.tsx → verify no active route, then delete
   ```

3. **Before deleting any legacy file:** Check `App.tsx` imports to confirm the file is not still imported as a fallback. Check navigation.ts for any remaining references.

### Risk
**Low** if routes are confirmed to point to V2 components. **Medium** if any route still imports a legacy component.

### Rollback Plan
`git revert <commit>`. Legacy files return. All routes continue working.

### Files Affected
- `docs/architecture/` (delete 9 misplaced files)
- `frontend/src/pages/` (delete 6 legacy files after verification)

### Validation
- `git grep "Import.tsx" frontend/src/App.tsx` — should return no results for legacy file
- Same check for each legacy file
- All routes still load correctly after deletion
- Bundle size should decrease modestly

---

## Phase E — Final Removal of Confirmed Unused Routes (After Pilot + Confirmation)

### Prerequisites
- Pilot has completed
- No user has navigated to the hidden pages in the past 60+ days
- Admin has confirmed the hidden pages are no longer needed

### What Happens

For each confirmed unused page (expected candidates after pilot: `/analytics`, `/governance`, `/admin-intelligence-dashboard`):
1. Remove route from `frontend/src/App.tsx`
2. Remove page entry from `frontend/src/config/navigation.ts`
3. Delete page component file from `frontend/src/pages/`
4. Delete corresponding domain hook from `frontend/src/hooks/domain/`
5. Remove any imports referencing deleted files
6. Update backend endpoints if any are exclusively used by the removed page (check carefully — most endpoints serve multiple pages)
7. Commit with message: `chore(cleanup): remove confirmed unused route [route-name]`

### Risk
**Medium.** Component deletion cannot be undone without git revert. If any external link points to the removed route, users will get a 404 (but NotFoundPage handles this gracefully).

### Rollback Plan
`git revert <commit>` for each deleted page. Reinstate the route in App.tsx and navigation.ts.

### Files Affected
- `frontend/src/App.tsx`
- `frontend/src/config/navigation.ts`
- `frontend/src/pages/<PageName>.tsx`
- `frontend/src/hooks/domain/use<PageName>Page.ts`
- Any services file exclusively used by the removed page

### Validation
- `npm run build` — must succeed with no broken imports
- TypeScript strict mode — must pass with no errors
- All remaining routes load correctly
- No broken nav links
- Backend tests pass (backend unchanged)

---

## Pages to NEVER Remove

The following pages must never be candidates for removal regardless of how the de-scoping pass proceeds:

| Page | Route | Reason |
|------|-------|--------|
| Exam Schedule | `/schedule` | THE primary product |
| Submissions | `/submissions` | Core exam paper workflow |
| Check-in / QR | `/checkins` | Core exam day handoff |
| Room Attendance | `/attendance` | Core exam day operations |
| Swaps | `/swaps` | Core invigilation flexibility |
| Print Queue | `/print-queue` | Print shop's only entry point |
| Optimizer | `/optimizer` | Core assignment optimization |
| Import | `/import` | Critical data intake |
| Dashboard | `/dashboard` | Main operational hub |
| Login + Auth | `/login`, `/role-selection`, `/` | Auth cannot be removed |
| Student Search | `/student-search` | Public commitment to students |
| All payment draft pages | `/invigilation-*`, `/payment-document-*` | Core payment support |

---

## Risk Summary

| Phase | Risk Level | Recoverable? | Approval Required? |
|-------|-----------|-------------|-------------------|
| A (docs) | None | N/A | Already committed |
| B (hide from nav) | Low | Yes — 1 git revert | Yes — user must approve |
| C (merge/simplify) | Medium | Yes — 1 git revert | Yes — user must approve |
| D (archive legacy) | Low–Medium | Yes — git revert | Yes — user must confirm each file |
| E (final remove) | Medium | Yes — git revert | Yes — requires explicit per-page confirmation |

---

## Recommended Sequencing

```
TODAY:
  Phase A ── commit docs ──────────────────────────────── [DONE in this pass]

THIS WEEK (after user answers decision questions):
  Phase B ── navigation.ts only ──────────────────────── [low risk; fast]

BEFORE PILOT:
  Phase D ── clean up misplaced docs/architecture/ files  [housekeeping]

POST-PILOT (60+ days of usage data):
  Phase C ── merge/simplify nav groups ────────────────── [medium risk]
  Phase E ── final removal of confirmed unused pages ───── [medium risk]
```

Do not rush Phase E. It is safer to ship the pilot with hidden pages than to permanently delete code that might still be needed.
