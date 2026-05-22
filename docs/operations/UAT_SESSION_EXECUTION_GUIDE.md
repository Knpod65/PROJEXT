# UAT_SESSION_EXECUTION_GUIDE.md

**Date**: 2026-05-22  
**Purpose**: Step-by-step guide for executing controlled pilot UAT sessions with real users.  
**Intended Audience**: Test coordinators, admins running pilot sessions.

---

## 1. Pilot Session Preparation

- Confirm pilot accounts have been created with correct roles (see UAT_ACCOUNT_MATRIX if exists, or IT_HANDOFF_PACKAGE.md).
- Verify production or staging environment is using real `DATABASE_URL` and `SECRET_KEY`.
- Confirm backup was taken before the session (or test restore evidence is attached).
- Prepare test data: at least one semester with schedules, workloads, and users.
- Reserve a quiet room or video call for the session.
- Have at least one observer/note-taker present.

---

## 2. Browser Preparation

- Use latest Chrome or Edge (recommended for Thai font rendering).
- Clear browser cache or use incognito/private window for each role test.
- Disable any password managers or extensions that may interfere with login.
- Have DevTools ready (F12) for console error capture if needed.
- Prepare screenshot tool (built-in Snipping Tool, ShareX, or browser extension).

---

## 3. Test Data Preparation

- Ensure the system has:
  - At least 3-5 departments with courses and sections
  - Published and draft schedules
  - Workload data for teachers
  - Governance workflow items in various states
- Have a "reset" plan or known-good snapshot in case of issues.

---

## 4. Login / Account Verification

- For each role, verify:
  - Correct login page appears
  - SSO fallback works if applicable
  - Role-based landing page / dashboard is correct
  - No privilege escalation possible (teacher cannot see admin views, etc.)

---

## 5. Role-by-Role Execution Order (Recommended)

Follow this sequence for controlled observation:

1. **Admin** (core operations + intelligence dashboards)
2. **Staff / Secretary** (scheduling, imports, exports)
3. **Supervisor / Dept Head** (department-scoped workload and governance)
4. **Teacher** (personal workload, schedule review, sign-off)
5. **Executive / DPO view** (high-level health, risk, PDPA-safe aggregates)

Test one role completely before moving to the next when possible.

---

## 6. Screenshot Capture Rules

- Capture before/after for every major action.
- Name files clearly: `YYYYMMDD_Role_Workflow_Step_Description.png`
- Capture both success states and any error/empty states.
- Always include browser URL and timestamp in the image if possible.
- Store in a dedicated folder per session (e.g., `pilot-uat-2026-05-XX/`).

---

## 7. Error Escalation During UAT

- Critical (data loss, security, crash): Stop session, notify on-call immediately, capture full console + network tab.
- Major (workflow broken, wrong data shown): Note, continue if possible, escalate after session.
- Minor (UI glitch, cosmetic): Log in observation template, continue.

---

## 8. What Counts as a Blocker (Must Fix Before Pilot Expansion)

- Login failure or role mis-assignment
- Data leakage across roles or PDPA violation
- Broken critical workflow (publish, sign-off, export)
- Application crash or unrecoverable error
- Incorrect workload or schedule calculations

---

## 9. What Counts as a Usability Issue (Note but Continue)

- Slow page load
- Confusing labels or empty states
- Minor layout issues on specific screen sizes
- Translation gaps
- Non-blocking export formatting

---

## 10. How to Collect Evidence

- Use the `PILOT_OBSERVATION_CAPTURE.md` template for every issue.
- Attach screenshots with clear names.
- Record pass/fail per item in `UAT_ROLE_WORKFLOW_CHECKLISTS.md`.
- At end of session, produce summary for `UAT_GO_NO_GO_REPORT.md`.

---

## Recommended Pilot Flow Summary

- **Session 1 (Admin + Staff)**: Core operations validation
- **Session 2 (Supervisors)**: Department scope and governance
- **Session 3 (Teachers)**: Personal views and workload
- **Session 4 (Executive / DPO)**: High-level dashboards and PDPA review

Each session should last 45–90 minutes depending on role complexity.

---

**End of UAT_SESSION_EXECUTION_GUIDE.md**  
This guide is ready for use in real pilot sessions. Combine with the role checklists and observation template below.