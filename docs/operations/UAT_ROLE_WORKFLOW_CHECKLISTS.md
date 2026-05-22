# UAT_ROLE_WORKFLOW_CHECKLISTS.md

**Date**: 2026-05-22  
**Purpose**: Detailed per-role workflow checklists for pilot UAT execution.  
**Usage**: Print or copy into session notes. Mark Pass/Fail + attach evidence.

---

## Admin Role Checklist

### Login & Dashboard
- Login with admin credentials → lands on Admin Intelligence Dashboard
  - Expected: Full system overview, health scores, risk bands
  - Evidence required: Screenshot of landing page
  - Pass / Fail / Notes: ________________

- Language switch (Thai ↔ English) works on all widgets
  - Expected: All labels, charts, and tables update
  - Evidence: Screenshot before/after switch
  - Pass / Fail / Notes: ________________

### Filters & Analytics
- Apply date range, department, and role filters
  - Expected: Data updates correctly, no cross-role leakage
  - Evidence: Screenshot of filtered results
  - Pass / Fail / Notes: ________________

- Workload analytics charts render with real data
  - Expected: No empty or broken charts
  - Evidence: Screenshot of charts
  - Pass / Fail / Notes: ________________

### Schedule & Governance
- View and publish a schedule
  - Expected: Publication workflow completes, audit log created
  - Evidence: Before/after + audit entry
  - Pass / Fail / Notes: ________________

- Export PDF/Excel from intelligence dashboard
  - Expected: File downloads, audit logged, no PII leakage
  - Evidence: Downloaded file sample + audit log
  - Pass / Fail / Notes: ________________

### Empty & Error States
- View a department with no data
  - Expected: Clear empty state message, no crash
  - Evidence: Screenshot
  - Pass / Fail / Notes: ________________

---

## Staff / Secretary Role Checklist

- Login → Staff dashboard with scheduling tools
- Import open courses and enrollments (test import)
- Create/edit schedule sections
- Run optimization (if permissions allow)
- Export paper distribution and workload reports
- Language switch and responsive check on laptop + tablet

**Evidence required for each major step above**: Screenshot + pass/fail.

---

## Supervisor / Department Head Role Checklist

- Login → Department-scoped workload view only
- Cannot see other departments' detailed data (PDPA check)
- Review and approve/reject workflow items in own department
- View cumulative workload charts for own teachers
- Export department report (no other faculty data)

**Evidence required**: Screenshots proving scope limitation + correct data.

---

## Teacher Role Checklist

- Login → Personal workload and exam schedule only
- View own invigilation and paper distribution duties
- Sign off on assigned items (if workflow allows)
- Language switch works
- Mobile/responsive view of personal schedule
- Empty states when no duties assigned

**Evidence required**: Screenshots of personal-only view + no leakage to other teachers.

---

## Executive / DPO View Checklist

- Login with restricted role → High-level health dashboard only
- All metrics are aggregate (no raw student/teacher PII)
- Risk bands and recommendations visible
- Export of executive summary works with audit
- PDPA-safe views confirmed

**Evidence required**: Screenshots demonstrating aggregate-only data.

---

## Cross-Role Common Checks (All Roles)

- Responsive behavior on desktop, tablet, mobile
- Empty states are helpful and not confusing
- Error states (e.g., network error, permission denied) are user-friendly
- No console errors in DevTools during normal flow
- Thai font and date formatting correct

**Record any issues** in `PILOT_OBSERVATION_CAPTURE.md`.

---

**End of UAT_ROLE_WORKFLOW_CHECKLISTS.md**  
Use together with `UAT_SESSION_EXECUTION_GUIDE.md` and `PILOT_OBSERVATION_CAPTURE.md` during real sessions.