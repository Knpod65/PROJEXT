# DEMO_USER_JOURNEY_SCRIPT.md

**Date**: 2026-05-22
**Status**: DRAFT — for internal demo / stakeholder walkthrough
**Audience**: Presenter + up to 8 stakeholders
**Duration options**: 5 min | 15 min | 30 min

---

## Pre-Demo Checklist (for presenter)

- [ ] Backend running: `uvicorn main:app --reload --port 8000`
- [ ] Frontend running: `npm run dev` (port 3000) or built static served at port 8000
- [ ] SQLite DB seeded (first run auto-seeds)
- [ ] Demo accounts confirmed working (see DEMO_ACCOUNT_AND_DATA_READINESS.md)
- [ ] This script printed / open on second screen
- [ ] Screen recording / screenshot tool ready

---

## Demo Context Opening (30 sec)

> **What to say to stakeholders:**
> "Today I'm showing you the EMS (Exam Management System) — a platform built for Chiang Mai University's Faculty of Political Science and Public Administration. This is a functional development build running locally. Some things here are in progress, and I'll be clear about what's complete and what's coming next."

---

## Stage 1 — Login and Role Selection (1 min)

**Route**: `/login` → `/role-selection` then auto-redirect to `/dashboard`

**What to click**:
1. Click "เข้าสู่ระบบ" (Login) button on landing page, or go directly to `/login`
2. Enter credentials: `mathawee.m` / `admin123`
3. Click "เข้าสู่ระบบ" (Sign in)
4. Observe the redirect to `/dashboard`

**What to say**:
> "Users log in with their EMS account. The system is currently using local username/password authentication. Before the pilot goes live, this will integrate with the CMU OAuth login used across Chiang Mai University — the faculty IT team is working on that connection now."

**Expected screen**: Dashboard with role selector dropdown, key stats area.

**Fallback if broken**: Use admin account `mathawee.m` / `admin123`; confirm landing page at `/` is reachable.

---

## Stage 2 — Admin Dashboard Overview (2 min)

**Route**: `/dashboard`

**Role**: Admin

**What to click**:
1. Observe top summary cards (submissions, schedules, workload, rooms)
2. Note the role selector at top-right (can switch view-as roles)
3. Observe sidebar navigation — all 5 nav groups visible

**What to say**:
> "The admin dashboard gives a live view of the entire exam operations platform — pending submissions, upcoming exam days, room assignments, and staffing signals. The sidebar organizes the system into five areas: Dashboard, Operations, Exam Management, People, and System. Each user only sees pages their role is authorized to access."

**Expected screen**: Dashboard with summary cards filled with local data or empty-state placeholders.

**Fallback if broken**: Check sidebar → click other nav group → back to dashboard.

---

## Stage 3 — Role Dashboard / Role Switching (1–2 min)

**Route**: `/dashboard` (same) using view-as

**Role**: Admin (view-as teacher/staff)

**What to click**:
1. Click the role selector (top-right) → switch to "Teacher" view
2. Observe sidebar reorders for teacher role
3. Switch to "Staff" — observe different sidebar
4. Switch to "Dept Supervisor" — observe dept-scoped view

**What to say**:
> "Every role sees a different navigation layout and different operational signals. An admin sees governance and system pages. A teacher sees only their own exam submissions and schedule. A staff member sees duty assignments and room operations. A departmental supervisor is scoped to their own department's data."

**Expected screen**: Sidebar reorders after role switch; dashboard content adapts.

**Fallback if broken**: Log in as a different role directly (e.g., `pailin.phu` / `teacher123` for teacher).

---

## Stage 4 — Workload Duty Analytics (3–5 min)

**Routes**: `/workload-duty-analytics` (admin) or `/duty-workload` (staff) or `/my-workload` (teacher)

**Role**: Admin (preferred for demo depth)

**What to click**:
1. Sidebar → **Dashboard** → **Workload Analytics**
2. Observe per-person summary (teachers and staff)
3. Observe daily trend / bar chart
4. Observe fairness / balancing bars

**What to say**:
> "This analytics page shows the duty allocation for every person across the exam cycle — invigilation and paper distribution assignments. The bar chart shows per-person duty counts, and the fairness section shows whether the load is balanced. This is an **operational signal**, not a performance evaluation — that's a deliberate design choice."

**Expected screen**: Bar chart with bars per person; fairness section visible.

---

## Stage 5 — Schedule and Submissions (2–3 min)

**Routes**: `/schedule` and `/submissions`

**What to click**:
1. Sidebar → **Exam Management** → **Sections** (or **Schedule**)
2. Scroll through section list; note department and course/code
3. Sidebar → **Exam Management** → **Submissions**
4. Filter or scan by status (Submitted, Approved, Rejected, Released)

**What to say**:
> "Sections are course registrations — each row is a course section with its assigned teacher and student count. Submissions track the exam paper workflow: submitted → approved or rejected by admin → released to print shop. The entire lifecycle stays audit-logged."

**Expected screen**: Tables with sections and submissions; status labels visible.

---

## Stage 6 — Governance Cockpit (1 min)

**Route**: `/governance`

**Role**: Admin / ESQ Head / Secretary

**What to click**:
1. Sidebar → **System** → **Governance Cockpit**
2. Observe: Health score, blockers, pending approvals, overrides, rollbacks

**What to say**:
> "The Governance Cockpit shows the system's policy and publication health. It counts pending approvals, outstanding governance blockers, overrides, and escalations — all logged for DPA-compliant audit purposes."

**Expected screen**: Governance cards; may show untranslated or no-data state on empty DB.

---

## Stage 7 — Operational Health (1 min)

**Route**: `/operational-health`

**Role**: Admin / ESQ Head

**What to click**:
1. Sidebar → **System** → **Operational Health**
2. Observe service status columns

**What to say**:
> "This page shows whether all backend services, integrations, and dependencies are healthy. In the current local development environment it shows what's running."

---

## Stage 8 — Audit Explorer (1 min)

**Route**: `/audit-explorer`

**Role**: Admin / ESQ Head

**What to click**:
1. Sidebar → **System** → **Audit Explorer**
2. Scan audit table or event timeline
3. Note login/logout events, state changes

**What to say**:
> "Every significant action in EMS is logged in the audit trail — who did what, when, and what values changed. This is the foundation for DPO-compliant record-keeping."

---

## Stage 9 — Teacher Workflow (My Exam Work) (1 min)

**Route**: `/myexam`

**Role**: Teacher (`pailin.phu` / `teacher123`)

**What to click**:
1. Log out; or use view-as → Teacher
2. Sidebar → **Exam Management** → **My Exam Work**
3. Observe assigned sections and submission state
4. Click a section → submission draft

**What to say**:
> "From the teacher's view, the dashboard narrows to their own assigned sections. They see a direct path to submitting their exam paper, checking submission status, and responding to admin requests."

---

## Stage 10 — Print Shop Queue (30 sec, optional)

**Route**: `/print-queue`

**Role**: Print Shop Operator (`printshop.ops` / `print123`)

**What to click**:
1. Use `printshop.ops` / `print123` to log in
2. Observe print queue, batch status, delivery section

**What to say** (optional):
> "Print shop users see a dedicated queue interface with delivery status and batch tracking."

---

## Stage 11 — Acknowledging Limitations (30 sec)

**What to say**:
> "A few things to be clear about in this demo:
> 1. **Auth**: Right now users log in with local passwords. CMU faculty authentication (Laravel integration) is the next integration step.
> 2. **Data**: This is demo/seed data — no real personal records or real schedule data.
> 3. **Deployment**: This is a local development build, not a live production system.
> 4. **Go/No-Go**: Before any real pilot goes live, backup/restore, DPO sign-off, and Laravel auth verification are still required."

---

## Role Account Reference (Demo)

| Role | Username | Password | Notes |
|------|----------|----------|-------|
| Admin | `mathawee.m` | `admin123` | Dev only — rotate before pilot |
| ESQ Head | `napaporn.ph` | `esq123` | Dev only |
| Dept Supervisor | `phusanisa.sai` | `staff123` | Dev only |
| Staff | `ketsinee.s` | `staff123` | Dev only |
| Teacher | `pailin.phu` | `teacher123` | Dev only |
| Print Shop | `printshop.ops` | `print123` | Dev only |

> **These credentials are for LOCAL DEVELOPMENT / DEMO ONLY. Passwords are intentionally weak and must be changed before any real use.**

---

## What to Avoid Saying

- ❌ "This is production-ready" — it is not.
- ❌ "CMU login is connected" — authentication is local in this build.
- ❌ "This is live on the Faculty LAN" — this is a local build.
- ❌ "Data here is real student records" — it is seed/demo data.
- ❌ "We've passed Go/No-Go" — Go/No-Go conditions are not all met.
- ❌ "Roles are verified with real CMU data" — roles come from the local database.

---

**End of DEMO_USER_JOURNEY_SCRIPT.md**
