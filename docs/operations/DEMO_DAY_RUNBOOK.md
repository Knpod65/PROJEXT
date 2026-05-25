# DEMO_DAY_RUNBOOK.md

**Date**: 2026-05-25  
**Status**: Ready for stakeholder demo (standalone EMS only)

## 1. Demo Status

- **Demo Readiness**: 98/100 (standalone, interactive GUI smoke passed on real browser 2026-05-25)
- **Pilot Readiness**: 42/100 (unchanged)
- **Production Readiness**: 28/100 (unchanged)
- Scope: Standalone demo only. No Faculty LAN, Laravel auth, real PostgreSQL, backup evidence, or DPO sign-off.

## 2. Before Demo Checklist (Presenter)

- [ ] `git pull origin main` (confirm a3abb18 or newer)
- [ ] Working tree clean
- [ ] Backend started and healthy
- [ ] Frontend started and healthy
- [ ] Test one login with demo account
- [ ] Test /dashboard loads
- [ ] Open backup tabs: limitations one-pager, feedback form, certificate
- [ ] Projector/browser zoom set to 100-125%
- [ ] Close email, Slack, unrelated tabs
- [ ] Have printed or PDF copies of:
  - EMS_STAKEHOLDER_DEMO_ONE_PAGER.md
  - DEMO_LIMITATIONS_AND_DISCLOSURE.md
  - FINAL_DEMO_READINESS_CERTIFICATE.md
  - DEMO_STAKEHOLDER_FEEDBACK_FORM.md

## 3. Service Startup Commands

**Backend** (one terminal):
```
backend\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend** (second terminal):
```
cd frontend
npm run dev
```

**Health checks**:
- Backend: http://127.0.0.1:8000/health
- Frontend: http://localhost:3000
- Login page should appear cleanly

Expected dev warnings only (SECRET_KEY, SQLite fallback) — document as known for standalone demo.

## 4. Demo Accounts

Use the 4 seed accounts (passwords in internal secure note only — never in public materials):
- mathawee.m (admin)
- napaporn.ph (esq_head)
- printshop.ops (print_shop)
- pailin.phu (teacher)

Do not share passwords in stakeholder materials.

## 5. Recommended Route Order (15–20 min core flow)

1. Login + Role Selection (show 2–3 roles)
2. Admin view: /dashboard → /admin-intelligence-dashboard
3. Workload: /workload-duty-analytics or teacher variant
4. Operational: /schedule + /submissions
5. Intelligence deep: /operational-health + /audit-explorer + /governance
6. Print shop: /print-queue
7. Teacher example: /myexam (if time)
8. Limitations & Next Steps (use one-pager)

Keep to 5/15/30 min script in STAKEHOLDER_DEMO_SCRIPT.md.

## 6. Emergency Fallback

If any route fails or shows unexpected error:
- Immediately show pre-captured screenshot from previous smoke
- Continue with next section of script
- Note issue in feedback log
- Do **not** improvise claims about production or pilot readiness
- Say: "This is the exact state we validated yesterday — we are transparent about any remaining polish items."

## 7. End-of-Demo Checklist

- [ ] Collect all filled feedback forms
- [ ] Record key questions and decisions on POST_DEMO_DECISION_MATRIX.md
- [ ] Note any "wow" moments or strong concerns
- [ ] Assign owners for next actions (e.g., send Laravel contract request)
- [ ] Thank participants and restate limitations

**Rule**: Never claim Pilot or Production readiness. Always redirect to the disclosed gaps and the clear next-step options.

---
*Print or have this runbook open on a second screen during the demo.*
