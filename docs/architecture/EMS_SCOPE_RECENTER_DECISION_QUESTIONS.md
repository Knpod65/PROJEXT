# EMS Scope Recenter — Decision Questions

**Date:** 2026-06-30
**Purpose:** Ask the user clear product questions to confirm which pages should be hidden, kept, or merged. No technical knowledge required to answer these.

**Context:** The EMS has grown to 50 routes. Many pages were added to demonstrate platform maturity for demo/exec signoff. For the actual pilot with real faculty staff, simpler is better. Before making any navigation changes, the following questions need answers.

---

## How to Use This Document

- Answer YES or NO (or a short note) for each question
- You do not need to know file names or code — these are product decisions
- Questions are grouped by topic
- After answers are collected, Phase B (navigation cleanup) can begin

---

## Group 1: Pages to Hide from Sidebar

These questions are about removing items from the left sidebar. The pages remain accessible by direct URL for admin users — they are not deleted.

---

**Q1. Admin Intelligence Dashboard (`/admin-intelligence-dashboard`)**

This page shows a platform-level metrics dashboard for admin. It was built to demonstrate that EMS has analytics capabilities, not for daily exam operations use.

> Should this be hidden from the sidebar during the pilot? Real faculty admin users are unlikely to need this on a daily basis.

- [ ] YES — hide from sidebar (keep URL access for admin)
- [ ] NO — keep visible in sidebar
- [ ] Notes: ___________

---

**Q2. Executive Analytics (`/analytics`)**

This page shows institutional health and trend analysis across terms. It uses "executive" framing and institutional-level metrics. It is visible to admin, esq_head, and secretary.

> Should this be hidden from the sidebar? Trend analysis across terms is not needed for daily exam-period operations.

- [ ] YES — hide from sidebar (keep URL access)
- [ ] NO — keep visible in sidebar
- [ ] Notes: ___________

---

**Q3. Governance Cockpit (`/governance`)**

This page shows approval blockers and governance status in one place. However, blockers are already visible in the Dashboard and the Workflow page. The "governance cockpit" framing may be unfamiliar to Thai university staff.

> Should this be hidden from the sidebar? The information it shows overlaps with Dashboard and Workflow.

- [ ] YES — hide from sidebar (keep URL access)
- [ ] NO — keep visible in sidebar
- [ ] Notes: ___________

---

**Q4. Operational Health (`/operational-health`)**

This page shows backend service health (response times, database status, queue depths). It is an IT monitoring tool, not an exam operations tool.

> Should this be accessible only by direct URL? Real faculty staff do not need to see backend health metrics.

- [ ] YES — hide from sidebar (keep URL access for admin)
- [ ] NO — keep visible in sidebar
- [ ] Notes: ___________

---

**Q5. Audit Explorer (`/audit-explorer`)**

This page shows a log of audit events (who did what, when). It is a compliance and developer tool. It is currently visible to admin and esq_head.

> Should this be accessible only by direct URL? Audit review is not a daily faculty workflow task.

- [ ] YES — hide from sidebar
- [ ] NO — keep visible in sidebar
- [ ] Notes: ___________

---

**Q6. Optimizer Trace (`/optimizer-trace`)**

This page shows the internal candidate lineage and scoring from the optimizer. It requires understanding of how the optimization algorithm works to be useful.

> Should this be accessible only by direct URL? Most admin users who run the optimizer only need to see the resulting schedule, not the internal trace.

- [ ] YES — hide from sidebar
- [ ] NO — keep visible in sidebar
- [ ] Notes: ___________

---

**Q7. Platform Configuration (`/platform-config`)**

This page manages complex faculty governance configuration (D3 maturity level). The backend currently returns empty arrays for this page's data. The configuration is not yet operational.

> Should this be accessible only by direct URL? Platform config is a system setup tool, not a daily faculty need, and its data is not yet live.

- [ ] YES — hide from sidebar
- [ ] NO — keep visible in sidebar
- [ ] Notes: ___________

---

**Q8. Import Audit (`/import-audit`)**

This page lets admin review the logs from past import sessions (row-level audit of each import run). It's useful after an import but not needed in the daily sidebar.

> Should this be hidden from the main sidebar? Admin can still reach it by URL after running an import.

- [ ] YES — hide from sidebar
- [ ] NO — keep visible in sidebar
- [ ] Notes: ___________

---

## Group 2: Pages to Reconfigure

These questions are about how existing pages are accessed or labeled, not about hiding them.

---

**Q9. Historical Schedules — Role Access**

The Historical Schedules page (`/historical-schedules`) currently appears only in the admin sidebar. It shows a term-to-term comparison of exam schedule assignments — useful for verifying that optimization was fair to all staff.

The original audit request specifically noted: "ควรยังคงให้ทุกคนเห็นได้ เพื่อให้ตรวจสอบได้ว่า optimize แล้วมีความเป็นธรรมกับทุกคนหรือไม่" (should remain visible to all, so people can verify whether optimization was fair to everyone).

> Should Historical Schedules be visible to staff, teachers, and supervisors (not just admin), so everyone can verify fairness after optimization?

- [ ] YES — expand role access to staff, teachers, supervisors
- [ ] NO — keep admin-only
- [ ] YES, but only to staff and supervisors (not teachers)
- [ ] Notes: ___________

---

**Q10. Workload Analytics — Three Routes, One Concept**

Currently three separate routes (`/workload-duty-analytics` for admin, `/duty-workload` for staff/esq/sec/supervisor, `/my-workload` for teacher) all use the same page component with role-filtered data. Each role only sees one route in the sidebar, but they have different labels.

> Should all three workload routes be presented as a single "ภาระงานคุมสอบ" (Invigilation Workload) nav entry that automatically routes to the correct version for your role?

- [ ] YES — unify the label, keep the role-filtered routing as-is
- [ ] NO — keep three separate labels (one per role)
- [ ] Notes: ___________

---

## Group 3: Landing Page and Navigation Structure

---

**Q11. Default Landing Page per Role**

After login, each role is sent to a default page. Currently:

| Role | Current Default |
|------|----------------|
| admin | /dashboard |
| esq_head | /dashboard |
| secretary | /dashboard |
| dept_supervisor | /dashboard |
| staff | /dashboard |
| teacher | /dashboard (or /myexam?) |
| print_shop | /print-queue |

> Is the current default landing page correct for each role, or should any roles land somewhere different?

Roles needing a different default:
- teacher: Should it be `/myexam` instead of `/dashboard`?
- staff: Should it remain `/dashboard`?

Notes: ___________

---

**Q12. Payment Pages — Group Label**

Payment-related pages are grouped under "เอกสารประกอบการเบิก" (Payment Support Documents). This is the correct grouping.

> Should payment pages remain under this label only, without appearing under any other navigation group or label?

- [ ] YES — keep all payment pages grouped under เอกสารประกอบการเบิก
- [ ] NO — suggest alternative grouping:
- [ ] Notes: ___________

---

## Group 4: Roles and Visibility

---

**Q13. Pages That Should Never Appear for Certain Roles**

Confirm the following restrictions are correct:

| Role | Should NEVER see |
|------|----------------|
| teacher | Payment config, admin analytics, system health, developer tools |
| staff | Executive analytics, developer diagnostics, governance cockpit |
| print_shop | Everything except print queue |
| dept_supervisor | Payment configuration, analytics, developer tools |

> Do you agree with these restrictions, or are there exceptions?

- [ ] YES — these restrictions are correct
- [ ] NO — exceptions: ___________

---

**Q14. Real User Experience**

Based on actual feedback from faculty staff (if any has been collected):

> Are there any pages currently in the sidebar that real faculty staff have found confusing or have asked "what is this?" or "why is this here?"

Known candidates based on audit:
- Admin Intelligence Dashboard — enterprise framing
- Executive Analytics — not an exam-op term
- Governance Cockpit — unfamiliar to university admin context
- Optimizer Trace — very technical

Additional feedback: ___________

---

## Summary of Recommended Answers (Based on Audit Findings)

If you agree with the audit findings, these are the recommended answers:

| Question | Recommended Answer |
|---------|-------------------|
| Q1 Admin Intelligence Dashboard | YES — hide from sidebar |
| Q2 Executive Analytics | YES — hide from sidebar |
| Q3 Governance Cockpit | YES — hide from sidebar |
| Q4 Operational Health | YES — hide from sidebar |
| Q5 Audit Explorer | YES — hide from sidebar |
| Q6 Optimizer Trace | YES — hide from sidebar |
| Q7 Platform Config | YES — hide from sidebar |
| Q8 Import Audit | YES — hide from sidebar |
| Q9 Historical Schedules role access | YES — expand to staff/supervisors/teachers |
| Q10 Workload nav consolidation | YES — single label "ภาระงานคุมสอบ" |
| Q11 Default landing page | dashboard for most; /myexam for teacher is worth considering |
| Q12 Payment page grouping | YES — keep under เอกสารประกอบการเบิก |
| Q13 Role restrictions | YES — restrictions are correct |
| Q14 User feedback | Answer from actual staff feedback |

---

## What Happens After Answers Are Collected

Once these questions are answered:

1. **If Q1–Q8 are all YES:** Phase B can begin immediately. Only `navigation.ts` changes. Estimated 15–30 minutes of work.

2. **If Q9 is YES:** Role expansion for Historical Schedules is added to Phase B. One additional `navigation.ts` edit.

3. **If Q10 is YES:** Workload label consolidation is added to Phase B. One additional `navigation.ts` edit.

4. **Phase B total scope:** `navigation.ts` only. 8–10 line changes. Low risk. Reversible.

---

## What These Changes Will NOT Do

Answering these questions and implementing Phase B will:

- NOT change any route paths
- NOT change any backend APIs
- NOT change any role guards
- NOT change any payment logic
- NOT change any export logic
- NOT change any schedule or optimization logic
- NOT delete any code
- NOT remove any database tables

The only change is whether certain pages appear in the left sidebar.
