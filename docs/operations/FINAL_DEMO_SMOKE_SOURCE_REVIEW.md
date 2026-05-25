# FINAL_DEMO_SMOKE_SOURCE_REVIEW.md

**Date**: 2026-05-25  
**Sprint**: EMS FINAL DEMO SMOKE + STAKEHOLDER DEMO PACKAGE PASS  
**Pre-flight status**: Real root confirmed, main at 4b20c57 (Demo 96/100 polish commit), working tree **clean**, no WIP merged.

## 1. Source Documents Read

- docs/operations/LOCAL_DEMO_SMOKE_SCRIPT.md (complete repeatable checklist with 4 seed accounts, critical routes, expected results, screenshot list)
- docs/operations/DEMO_GO_NO_GO_REPORT.md (post-polish: all validation green, Demo 96/100, GO for stakeholder demo with conditions, standalone scope explicitly stated)
- docs/architecture/DEMO_100_PERCENT_READINESS_SCORE.md (96/100 after polish: legacy hidden, bundle improved to ~560 kB, clean tree)
- docs/architecture/EMS_100_PERCENT_MASTER_SCORECARD.md (Demo 96/100; Pilot 42/100 and Production 28/100 explicitly unchanged)
- docs/architecture/EMS_100_PERCENT_READINESS_EXECUTIVE_SUMMARY.md (Demo 96/100 achieved via polish sprint; top gaps remain external contract/evidence)
- docs/operations/DEMO_USER_JOURNEY_SCRIPT.md (detailed 5/15/30 min scripts with pre-demo checklist and role journeys)
- docs/operations/DEMO_ROUTE_SMOKE_MAP.md (core routes mapped to roles)
- docs/operations/DEMO_ACCOUNT_AND_DATA_READINESS.md (seed accounts defined: mathawee.m/admin123, napaporn.ph/esq123, printshop.ops/print123, pailin.phu/teacher123; SQLite auto-seed on first run)
- docs/design/claude-design-handoff-package/README.md (for any future redesign — out of scope for this demo)

## 2. Expected Demo Scope (Standalone Only)

- **In scope**: Standalone EMS with local SQLite seed data, 4 role accounts, core operational + intelligence dashboards, i18n, role-based navigation (legacy hidden from demo sidebar).
- **Target routes** (from LOCAL_DEMO_SMOKE_SCRIPT + previous smoke map):
  - /login → Role Selection
  - /dashboard (all roles)
  - /admin-intelligence-dashboard (admin)
  - Workload variants (/workload-duty-analytics, /duty-workload, /my-workload)
  - /analytics, /governance
  - /schedule + /submissions
  - /print-queue + /print-review + QR
  - /import-v2
  - Heavy: AuditExplorer, OperationalHealth, GovernanceCockpit, ExecutiveAnalytics

## 3. Known Out-of-Scope Items (Must Be Clearly Stated in All Materials)

- Faculty LAN / Laravel / POLSCI OAuth integration (contract still unanswered; Laravel score 25/100)
- Real PostgreSQL target + backup/restore evidence (DB score 62/100)
- DPO sign-off / retention / CMU email flow (PDPA gaps)
- Production secrets, CI/CD on live infra, load testing
- Any claim of Pilot 100% (42/100) or Production 100% (28/100)
- con-1 external issues (explicitly excluded unless in current demo scope)

## 4. Seed / Demo Account Assumptions

From DEMO_ACCOUNT_AND_DATA_READINESS.md:
- 4 accounts seeded on first run via backend/seed.py when DB empty.
- Passwords: admin123, esq123, print123, teacher123 (bcrypt).
- Roles: admin, esq_head, print_shop, teacher.
- If accounts unavailable in this environment: mark SKIPPED in verification, do not fabricate.

## 5. Validation Plan for This Pass

- Run full backend/frontend validation commands (compile, import, pytest, build, i18n checks).
- Follow LOCAL_DEMO_SMOKE_SCRIPT exactly (non-destructive).
- If dev servers runnable: actual login + route visits with seed accounts.
- Record honest PASS/WARNING/FAIL/SKIPPED per route and account.
- Create stakeholder package (script + limitations + certificate) regardless of server availability.

## 6. Expected Outcome

- Honest final smoke results document.
- Stakeholder-ready materials that clearly separate "Demo 96/100 (standalone)" from "Pilot/Production still blocked by external contracts and evidence".
- No over-claiming.

**Next**: PHASE 2 — execute the smoke validation commands and (if possible) actual route smoke.

---
*This review confirms the sprint is scoped strictly to standalone demo polish and honest stakeholder packaging.*
