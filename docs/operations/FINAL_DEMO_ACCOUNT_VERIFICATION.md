# FINAL_DEMO_ACCOUNT_VERIFICATION.md

**Date**: 2026-05-25  
**Sprint**: EMS FINAL DEMO SMOKE + STAKEHOLDER DEMO PACKAGE PASS

## Accounts Checked (from DEMO_ACCOUNT_AND_DATA_READINESS.md)

| Account | Role | Expected Behavior | Actual (this run) | Status | Notes |
|---------|------|-------------------|-------------------|--------|-------|
| mathawee.m / admin123 | admin | Full access to intelligence, governance, settings (V2), users (hidden in demo nav) | SKIPPED | SKIPPED | No live server/DB execution in CLI environment |
| napaporn.ph / esq123 | esq_head | Governance + exec views | SKIPPED | SKIPPED | - |
| printshop.ops / print123 | print_shop | Print queue, review, QR | SKIPPED | SKIPPED | - |
| pailin.phu / teacher123 | teacher | My workload, schedule, submissions, my-exam | SKIPPED | SKIPPED | - |

## Summary

- Seed data defined in backend/seed.py (auto-seeds on empty DB for demo).
- All passwords bcrypt-hashed.
- Local SQLite (backend/ems.db) used for standalone demo.
- **Interactive login + forbidden page tests**: SKIPPED (no dev server/browser run in this execution).
- **Command-level readiness**: Confirmed via prior validation (DB would seed on first run if empty).

## What Is Needed for Full Verification

- Start backend + frontend dev servers.
- Clear or use fresh SQLite.
- Log in with each of the 4 accounts.
- Verify role-appropriate dashboards load and legacy items are hidden.
- Test one "forbidden" action per role (e.g., teacher trying admin-intelligence → should see permission denied or redirect).

**Honest status**: Accounts assumed ready based on prior seed + polish sprint. Full live verification recommended before stakeholder demo day.

---
*No fabrication. SKIPPED items clearly marked.*
