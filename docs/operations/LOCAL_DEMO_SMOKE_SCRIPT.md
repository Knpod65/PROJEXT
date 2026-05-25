# LOCAL_DEMO_SMOKE_SCRIPT.md

**Date**: 2026-05-25  
**Purpose**: Repeatable local demo smoke for internal/stakeholder rehearsals after DEMO 100% POLISH MINI-SPRINT.

## Prerequisites
- Working tree clean (or only expected demo polish changes)
- Backend .venv active or use the full python path
- Node 18+ for frontend
- Demo seed accounts (see DEMO_ACCOUNT_AND_DATA_READINESS.md):
  - mathawee.m / admin123 (admin)
  - napaporn.ph / esq123 (esq_head)
  - printshop.ops / print123 (print_shop)
  - pailin.phu / teacher123 (teacher)

## Start Commands (from ems_system root)

**Backend (one terminal)**:
```
backend\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (another terminal)**:
```
cd frontend
npm run dev
```

## Key Demo Routes to Visit (with each role where applicable)

1. /login → Role Selection → pick role
2. /dashboard (all roles)
3. /admin-intelligence-dashboard (admin)
4. /workload-duty-analytics or /duty-workload or /my-workload
5. /analytics (executive)
6. /governance (governance roles)
7. /schedule + /submissions (teacher/staff)
8. /print-queue + /print-review + QR scanner (print_shop)
9. /import-v2 (staff)
10. Heavy dashboards: AuditExplorer, OperationalHealth, GovernanceCockpit, ExecutiveAnalytics

## Expected Results
- No crashes or console errors on load
- Role-appropriate navigation (legacy hidden)
- Thai/English toggle works
- Empty states polite where no data
- No raw English in Thai mode on core pages
- All links/buttons functional within demo scope

## Screenshot Checklist
- Login + role selection
- Admin Intelligence (full payload)
- Workload for teacher
- Print queue for print_shop
- Governance for exec
- One heavy analytics page

## Pass/Fail
- Pass if all core routes render cleanly for the 4 roles with no obvious demo blockers.
- Note any remaining polish items for next iteration.

**Note**: Laravel integration explicitly out of scope for this demo. Use standalone auth only.

---
*Run this before every internal or stakeholder demo.*
