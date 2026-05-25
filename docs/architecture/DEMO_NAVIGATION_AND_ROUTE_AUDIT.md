# DEMO_NAVIGATION_AND_ROUTE_AUDIT.md

**Date**: 2026-05-25  
**Sprint**: EMS DEMO 100% POLISH MINI-SPRINT

## Summary of Audit Approach

- Inspected: frontend/src/App.tsx (465 lines, lazy + direct imports of V2 pages), frontend/src/config/navigation.ts (371 lines, central appPages config with hidden flag), roles/utils, AppShell/Sidebar.
- Cross-referenced with: DEMO_ROUTE_SMOKE_MAP.md, DEMO_USER_JOURNEY_SCRIPT.md, DEMO_SCOPE_AND_BOUNDARIES.md, previous 100% audit route table.
- Goal: Classify every nav item for demo without deleting routes or breaking permissions.

## Classification Results (Key Entries)

**DEMO CORE (show, polish if needed)**:
- dashboard, admin-intelligence-dashboard, workload-duty-analytics-* (admin/staff/teacher variants), executive-analytics, governance-cockpit
- workflow (V2), schedule, submissions, print queue/review, checkins, import-v2, etc.
- All major lazy-loaded heavy dashboards.

**HIDE FROM DEMO (set hidden: true in navigation.ts for demo runs)**:
- Any direct entries pointing to non-V2 legacy pages (Settings, Users, Workflow non-V2, Swaps, Import, RoleDashboard, PagePlaceholder and their nav items).
- Duplicates where V2 versions exist and are preferred for demo (e.g., if both /workflow and /workflow-v2 style exist).

**DEMO SUPPORT (show but note as secondary)**:
- SettingsV2, UsersV2, WorkflowV2, SwapsV2, StudentsV2, VenueManagementV2, RoomManagementV2, StaffAvailability, RoomAttendance, MyExam, External, Sections, StudentSearch, CoExam, ExamManager, Optimizer, Period, ExportCenter, Copy, HistoricalSchedules.

**PRODUCTION/PILOT ONLY or LEGACY/REVIEW**:
- Any page behind un-mocked external auth (print_shop full IdP if not standalone).
- Old internal frontend/src/docs/ references.

**BROKEN / FIX REQUIRED**:
- None critical for standalone demo (all validation green).

## Safe Polish Recommendation (for PHASE 3)

In navigation.ts:
- Add `hidden: true` to legacy/non-preferred duplicate entries for demo.
- Keep the actual routes in App.tsx intact (no deletion, reversible by removing the hidden flag).
- This prevents confusing demo users while preserving full functionality for development.

This matches the exact recommendation in DEMO_100_PERCENT_READINESS_SCORE.md and SAFE_QUICK_WINS.

No i18n or permission changes needed for this classification step.

---
*Audit complete. Ready for safe implementation in PHASE 3.*
