# DEMO_100_POLISH_SOURCE_REVIEW.md

**Date**: 2026-05-25  
**Sprint**: EMS DEMO 100% POLISH MINI-SPRINT  
**Pre-flight**: Confirmed real root, main branch at 09d4378 (the 100% audit commit), working tree cleaned (pre-existing backend/requirements.txt accidental httpx addition reverted — unused dep, no code impact).

## 1. What the Latest 100% Audit Says Blocks Demo 100 (from 87/100)

From DEMO_100_PERCENT_READINESS_SCORE.md and EXECUTIVE_SUMMARY:
- No critical blockers (build, 1428 tests, i18n parity all green).
- Polish items only:
  1. Legacy non-V2 pages still visible in navigation (Settings, Users, Workflow, Swaps, Import, RoleDashboard, PagePlaceholder + duplicates).
  2. Raw user-facing strings in 3 heavy pages (AdminIntelligenceDashboard, AuditExplorer, Checkins) flagged by i18n:raw scan.
  3. Some empty states not polished on demo accounts.
  4. Main bundle chunk warning (754.73 kB) causing first-load delay on demo machine.
  5. Demo scripts/screenshots need refresh to current state.
  6. Communication: explicitly note "Laravel integration not in scope for this demo".

From SAFE_QUICK_WINS_TO_REACH_DEMO_100.md:
- Exactly the 5 items the sprint is chartered to execute (navigation polish, raw strings, bundle, smoke script, docs hygiene).

From MASTER_SCORECARD and IMPROVEMENT_BACKLOG:
- Demo target after this sprint: aim for 95–100.
- Pilot/Production % explicitly unchanged (still blocked by external contract/evidence).

## 2. Which Items Can Be Fixed NOW (This Sprint — No External Dependencies)

**Fully in scope for this mini-sprint**:
- Hide legacy non-V2 pages from demo sidebar/navigation (config-driven, reversible, no route deletion).
- Fix real user-facing raw strings on demo-critical pages (add i18n keys, replace only where safe).
- Review and apply safe Vite manualChunks improvements (build-time only).
- Create LOCAL_DEMO_SMOKE_SCRIPT.md + update DEMO_GO_NO_GO_REPORT.md.
- Update score docs and add docs hygiene pointers.
- Run full validation after changes.

**NOT in scope / must wait**:
- Anything requiring Laravel/IT answers (auth bridge, mount path, PG target, DPO).
- Real backup/restore evidence.
- Production secrets or Faculty LAN deployment.
- Full visual redesign (claude-design-handoff-package is for later).
- Deletion of legacy pages (only hide from demo nav).

## 3. Demo Route Priorities (from DEMO_ROUTE_SMOKE_MAP + DEMO_USER_JOURNEY_SCRIPT + DEMO_SCOPE_AND_BOUNDARIES)

**DEMO CORE (must be flawless)**:
- Login / Role Selection (all 4 seed accounts: mathawee.m/admin123, napaporn.ph/esq123, printshop.ops/print123, pailin.phu/teacher123)
- Dashboard (role home)
- Workload / Duty Analytics
- Schedule + Submissions
- Print Queue / Review / QR Pickup
- Governance Cockpit
- Admin Intelligence Dashboard (recently fixed payload)
- Executive Analytics / National / Predictive / Futures
- Audit Explorer / Operational Health

**DEMO SUPPORT (good to have polished)**:
- Import V2 / Historical Schedules
- SettingsV2, UsersV2, WorkflowV2, SwapsV2, StudentsV2, Venue/Room V2, StaffAvailability, RoomAttendance, MyExam, External, Sections, StudentSearch, CoExam, ExamManager, Optimizer, Period, ExportCenter, Copy, Checkins

**HIDE FROM DEMO (recommended)**:
- Any remaining non-V2 legacy pages (Settings.tsx, Users.tsx, Workflow.tsx, Swaps.tsx, Import.tsx, RoleDashboard.tsx, PagePlaceholder.tsx and their direct nav entries).
- Anything behind incomplete external auth or print shop IdP that isn't mocked for standalone demo.

## 4. Validation Plan for This Sprint

After every code change:
- Backend (if touched): compileall + import smoke + pytest
- Frontend: npm run build + check:i18n + check:i18n:raw
- Git status --short (explicit paths only for staging)
- Manual smoke of key demo routes with seed accounts

No claims about Pilot or Production readiness will be made.

## 5. Expected Outcome of This Sprint

- Demo readiness moved from 87/100 → 95–100/100 (internal/stakeholder demo ready with clear limitations noted).
- Pilot 42/100 and Production 28/100 **unchanged**.
- Clean working tree, all changes small/reversible, docs and code committed separately.
- Repeatable local demo smoke process documented.

**Next phase in sprint**: PHASE 2 — full demo route/navigation audit against App.tsx + navigation.ts + smoke map.

---
*This document is the charter for the mini-sprint. All work stays strictly within the safe quick wins identified in the 100% audit.*
