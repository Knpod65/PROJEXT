# FACULTY_LAN_PILOT_IMPLEMENTATION_PLAN.md

**Date**: 2026-05-22
**Purpose**: Staged implementation plan for deploying and validating EMS on the Faculty LAN Server with Laravel/CMU auth integration.
**Status**: DRAFT — owners TBD, timeline TBD

---

## Overview

This plan covers all stages from technical contract confirmation through Go/No-Go approval. Each stage has an owner, required evidence, pass criteria, and a blocker condition that must halt progress if not met.

**No stage may be marked complete without its required evidence.**
**No stage may begin until its preceding stage is complete (pass criteria met).**

---

## Stage 1 — Confirm Technical Contract

**Owner**: TBD (EMS team + Laravel owner + IT owner)
**Prerequisite**: Laravel owner and IT owner identified and engaged
**Target date**: TBD

### Activities

- [ ] Send `LARAVEL_AUTH_CONTRACT_QUESTIONS.md` to Laravel owner and IT owner
- [ ] Receive completed answers from Laravel owner (session payload, callback route, CMU email field)
- [ ] Receive completed answers from IT owner (PostgreSQL target, deployment method, server path, network scope)
- [ ] Verify answers against actual Laravel codebase (not just verbal confirmation)
- [ ] Decide EMS mount route (`/ems`, `/exam`, or subdomain)
- [ ] Decide auth bridge option (A, B, C, or D from `EMS_LARAVEL_INTEGRATION_OPTIONS.md`)
- [ ] Decide `cmu_sso.py` path (activate direct OAuth stub vs. Laravel bridge vs. both)
- [ ] If direct OAuth path: confirm OIT credentials (`CMU_SSO_CLIENT_ID`, `CMU_SSO_CLIENT_SECRET`) are available
- [ ] Confirm PostgreSQL DB ownership (shared or separate)
- [ ] Confirm backup owner

### Required Evidence

- Completed `LARAVEL_AUTH_CONTRACT_QUESTIONS.md` with answers from Laravel/IT owners
- Written agreement on auth bridge option and EMS mount route
- IT confirms server hostname/IP and access method

### Pass Criteria

All critical contract items in `PILOT_BLOCKER_DASHBOARD.md` items 3–9 move from OPEN to EVIDENCE ATTACHED or CLOSED.

### Blocker Condition

If the Laravel owner or IT owner is unresponsive within the agreed deadline: escalate to Faculty Leadership. Do not proceed to Stage 2 without contract answers.

---

## Stage 2 — Configure Environment

**Owner**: TBD (IT owner + EMS deployment owner)
**Prerequisite**: Stage 1 complete
**Target date**: TBD

### Activities

- [ ] Provision EMS PostgreSQL database on Faculty LAN server
- [ ] Generate `SECRET_KEY` (≥50 characters, cryptographically random) — never commit to code
- [ ] Configure `DATABASE_URL` pointing to the EMS PostgreSQL instance
- [ ] Configure `ALLOWED_HOSTS` (Faculty LAN hostname)
- [ ] Configure `ALLOWED_ORIGINS` (EMS frontend origin)
- [ ] Set `DEBUG=False`
- [ ] Set `LOG_LEVEL` (INFO for pilot)
- [ ] Set `PDPA_RETENTION_DAYS`
- [ ] If direct CMU OAuth path: configure `CMU_SSO_CLIENT_ID`, `CMU_SSO_CLIENT_SECRET`, `CMU_SSO_REDIRECT_URI`
- [ ] If Laravel bridge (Option B): configure `LARAVEL_BRIDGE_URL`, `LARAVEL_BRIDGE_SECRET`
- [ ] Run EMS database migrations against Faculty LAN PostgreSQL
- [ ] Verify migrations applied correctly (no errors, all tables present)

### Required Evidence

- IT confirms (yes/no only, no actual values) each env var is configured
- `alembic current` or equivalent shows migrations applied
- No SECRET_KEY or credentials appear in any committed file

### Pass Criteria

- All required env vars configured (confirmed yes by IT)
- Database migrations applied without errors
- `PILOT_BLOCKER_DASHBOARD.md` items 10 and 11 move to EVIDENCE ATTACHED

### Blocker Condition

If SECRET_KEY appears in any code file or git diff: STOP immediately. Do not proceed until removed and key rotated.

---

## Stage 3 — Deploy Backend and Frontend

**Owner**: TBD (EMS deployment owner)
**Prerequisite**: Stage 2 complete
**Target date**: TBD

### Activities

- [ ] Deploy EMS FastAPI backend to Faculty LAN server (Docker or direct Python service)
- [ ] Confirm FastAPI backend starts without errors (`uvicorn` or equivalent)
- [ ] Deploy EMS React frontend static files (build and copy to server path)
- [ ] Configure Nginx to serve EMS frontend at agreed mount path (`/ems` or subdomain)
- [ ] Configure Nginx to proxy `/api/...` requests to EMS FastAPI backend port
- [ ] Verify health endpoint: `GET /health` returns 200 OK with status "ok"
- [ ] Verify frontend loads in browser without JavaScript errors
- [ ] Verify frontend static assets (JS, CSS, images) are served correctly
- [ ] Verify API responds to `GET /api/auth/me` (should return null or 401 if not logged in)
- [ ] Check that EMS FastAPI backend port is NOT directly accessible from LAN (only via Nginx) — if Option C or any proxy-dependent setup

### Required Evidence

- Screenshot of `/health` returning 200 OK
- Screenshot of EMS frontend loading without errors
- Screenshot of DevTools showing no console errors on page load
- IT confirms Nginx configuration is active

### Pass Criteria

- Health endpoint returns 200 OK
- EMS frontend loads without errors
- API endpoint responds (correctly rejects unauthenticated requests)

### Blocker Condition

If FastAPI backend fails to start (e.g., migration errors, env var missing): fix root cause before Nginx configuration.

---

## Stage 4 — Auth Bridge Rehearsal

**Owner**: TBD (EMS team + Laravel owner)
**Prerequisite**: Stage 3 complete, auth bridge option implemented (from contract)
**Target date**: TBD

### Activities

- [ ] User visits EMS on Faculty LAN (browser)
- [ ] Login flow triggers CMU authentication (via Laravel or direct cmu_sso.py)
- [ ] CMU OAuth callback completes successfully
- [ ] Laravel session (`session("USS")`) is set (verify with Laravel owner)
- [ ] EMS bridge endpoint receives verified identity
- [ ] EMS backend maps CMU email to EMS user/role from EMS database
- [ ] EMS JWT HttpOnly cookie is set
- [ ] EMS frontend shows authenticated user with correct role
- [ ] Audit log entry created for bridge login (confirm in EMS admin or DB)
- [ ] Test logout — EMS session cleared, JWT cookie removed
- [ ] Test session expiry handling (what happens when Laravel session expires?)
- [ ] Test with at least 2 CMU email accounts (different roles)
- [ ] Confirm `cmu_at` is NOT visible in browser DevTools (no localStorage, no cookie readable by JS, not in any API response body)

### Required Evidence

- Screenshot of successful CMU-authenticated EMS login
- Screenshot of EMS frontend showing correct user name and role
- Audit log entry showing bridge login (CMU email + EMS role + timestamp)
- Screenshot of DevTools confirming no CMU token visible in frontend
- Logout test: screenshot of session cleared

### Pass Criteria

- Full login flow completes without errors
- Correct EMS role assigned from DB
- Audit log entry exists
- cmu_at is not visible to frontend

### Blocker Condition

If any of the following occur: STOP, do not proceed to UAT.
- CMU email is read from URL param or localStorage (not server-verified)
- cmu_at appears in any browser-visible location
- Role is assigned from client claim rather than EMS DB
- Audit log entry not created

---

## Stage 5 — Backup and Restore Test

**Owner**: TBD (IT / Ops)
**Prerequisite**: Stage 3 complete (can run in parallel with Stage 4)
**Target date**: TBD

### Activities

- [ ] Run first EMS database backup (`pg_dump` or equivalent)
- [ ] Confirm backup file is created and non-empty
- [ ] Store backup in agreed backup location (not on the same disk as primary DB)
- [ ] Perform restore test to a safe non-production target (separate database, local machine, or test DB)
- [ ] Verify restored database is queryable and contains expected tables
- [ ] Schedule automated daily backup (cron or equivalent)
- [ ] Document backup and restore procedure in `BACKUP_AND_RESTORE_RUNBOOK.md`

### Required Evidence

- Backup file timestamp and size
- Restore test: confirmation that restored DB has correct schema and data
- Cron or backup schedule configuration confirmed
- `BACKUP_RESTORE_TEST_EVIDENCE.md` updated

### Pass Criteria

- `PILOT_BLOCKER_DASHBOARD.md` item 13 (Backup scheduled and tested) moves to EVIDENCE ATTACHED
- Restore completes without error

### Blocker Condition

If backup cannot be restored: do not proceed to UAT. Unreliable backup is a pilot blocker.

---

## Stage 6 — UAT (User Acceptance Testing)

**Owner**: TBD (Pilot coordinator)
**Prerequisite**: Stages 4 and 5 complete
**Target date**: TBD

### Activities

Conduct UAT for each role using `UAT_ROLE_WORKFLOW_CHECKLISTS.md` and `UAT_SESSION_EXECUTION_GUIDE.md`.

| Role | Test Focus | Pass Criteria |
|---|---|---|
| Admin | User management, period management, schedule management, system settings, exports | All admin workflows complete without errors |
| Staff / Secretary | Workload assignment, workflow signing, room operations, operational exports | All staff workflows complete without errors |
| Teacher | Exam submission, personal schedule view, personal workload view | Teacher-only workflows complete; cross-dept data not visible |
| Dept Supervisor | Department workload, dept exports, approval | Dept-scoped data only; no cross-dept data |
| Executive / Governance | Executive dashboard, governance reports | Correct aggregated data; no personally identifiable data leakage |

Additional UAT items for Faculty LAN:
- [ ] CMU email login works for all pilot accounts
- [ ] Correct role assigned per user after CMU email → EMS DB mapping
- [ ] No test/seed accounts visible in production (cleanup confirmed)
- [ ] PDPA-relevant data handling confirmed (no unauthorised data export)

### Required Evidence

- Completed `UAT_ROLE_WORKFLOW_CHECKLISTS.md` for each role
- `PILOT_OBSERVATION_CAPTURE.md` entries for each session
- Any bugs logged in `PILOT_BUG_TRIAGE.md`
- Screenshot evidence attached per checklist

### Pass Criteria

- All critical workflows pass for all roles
- No critical or high-severity bugs open
- CMU auth login confirmed working for pilot user accounts

### Blocker Condition

If critical auth or data security issues are found during UAT: halt. Fix and re-run affected UAT sections before Go/No-Go.

---

## Stage 7 — Go/No-Go Decision

**Owner**: Faculty Leadership
**Prerequisite**: All previous stages complete
**Target date**: TBD

### Activities

- [ ] Review evidence from all stages
- [ ] Update `UAT_GO_NO_GO_REPORT.md` with final evidence
- [ ] Confirm all `PILOT_BLOCKER_DASHBOARD.md` blockers are CLOSED or accepted as known risk
- [ ] DPO sign-off obtained (`DPO_RETENTION_SIGNOFF_TEMPLATE.md` signed)
- [ ] Pilot account list confirmed
- [ ] Faculty Leadership approves Go/No-Go

### Required Evidence

- All stage evidence packages present
- `UAT_GO_NO_GO_REPORT.md` updated and signed
- `DPO_RETENTION_SIGNOFF_TEMPLATE.md` signed
- `PILOT_BLOCKER_DASHBOARD.md` — no OPEN critical blockers

### Pass Criteria (Go)

- All stages pass
- No open critical blockers
- DPO sign-off obtained
- Faculty Leadership approves

### No-Go Conditions

- Any critical blocker remains OPEN
- DPO sign-off not obtained
- Auth bridge not verified (Stage 4 not passed)
- Backup not tested (Stage 5 not passed)
- Critical UAT failures unresolved

---

## Summary Table

| Stage | Name | Owner | Depends On | Status |
|---|---|---|---|---|
| 1 | Confirm technical contract | TBD | IT owner + Laravel owner assigned | OPEN |
| 2 | Configure environment | TBD | Stage 1 | OPEN |
| 3 | Deploy backend/frontend | TBD | Stage 2 | OPEN |
| 4 | Auth bridge rehearsal | TBD | Stage 3 + bridge implemented | OPEN |
| 5 | Backup/restore test | TBD | Stage 3 (can parallel Stage 4) | OPEN |
| 6 | UAT | TBD | Stages 4 + 5 | OPEN |
| 7 | Go/No-Go | Faculty Leadership | Stage 6 | OPEN |

---

**End of FACULTY_LAN_PILOT_IMPLEMENTATION_PLAN.md**
All stages are OPEN. No stage may be marked complete without verified evidence. No values fabricated.
