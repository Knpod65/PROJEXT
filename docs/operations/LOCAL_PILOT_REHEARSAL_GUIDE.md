# LOCAL_PILOT_REHEARSAL_GUIDE.md

**Date**: 2026-05-22  
**Purpose**: Guide for performing a safe local rehearsal of the pilot deployment process while waiting for a real pilot target environment.

---

## 1. Purpose

Local rehearsal is **not** an official pilot. It is intended for:

- Practicing deployment steps
- Validating that the current codebase runs cleanly in a near-production configuration
- Testing the UAT checklists and observation process internally
- Building confidence before the real environment is available

**Important**: Evidence collected during local rehearsal **cannot** be used as production pilot evidence for SECRET_KEY, DATABASE_URL, backup policy, or DPO sign-off.

---

## 2. Local Rehearsal Checklist

- [ ] Backend starts successfully with production-like settings (`ENVIRONMENT=production`, `DEBUG=False`)
- [ ] Frontend builds and serves without errors
- [ ] Local PostgreSQL (or Docker Postgres) is running
- [ ] Login works for at least Admin and Teacher roles
- [ ] Main dashboards load (Workload Analytics, Governance, Executive views)
- [ ] Audit Explorer and import/export routes are accessible
- [ ] Health endpoint returns clean status
- [ ] Language switch (Thai ↔ English) works
- [ ] No critical console errors in browser

---

## 3. Recommended Local Commands (Placeholders)

```bash
# Backend (example)
cd backend
python -m compileall . -q
# or using the project's venv
.venv\Scripts\python.exe -m pytest --tb=no -q

# Frontend
cd frontend
npm run build
npm run preview   # or serve the dist folder
```

Adjust commands according to the actual project setup in `README-DEV.md` or deployment scripts.

---

## 4. Evidence That Can Be Collected Locally

- Screenshots of dashboards and workflows
- Browser console logs
- Health endpoint responses
- Role navigation tests using the `UAT_ROLE_WORKFLOW_CHECKLISTS.md`
- Observation notes using `PILOT_OBSERVATION_CAPTURE.md`

---

## 5. Evidence That Cannot Be Counted as Production Evidence

- Any `SECRET_KEY` used locally
- Local `DATABASE_URL`
- Local backup/restore tests (unless performed against a production-like PostgreSQL instance with real policy)
- DPO sign-off (requires formal review)
- Real user UAT results

---

## 6. Outcome Record

**Rehearsal Performed By**: _______________________________  
**Date**: _______________________________

**Result**:
- [ ] Rehearsal Passed (all checklist items successful)
- [ ] Rehearsal Failed (issues found — see below)

**Issues Found**:
_______________________________________________________________________________

**Follow-up Actions**:
_______________________________________________________________________________

---

**End of LOCAL_PILOT_REHEARSAL_GUIDE.md**  
Use this guide for internal practice. Do not treat local results as official pilot evidence.