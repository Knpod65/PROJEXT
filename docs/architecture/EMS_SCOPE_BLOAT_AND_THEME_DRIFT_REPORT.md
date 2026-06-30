# EMS Scope Bloat and Theme Drift Report

**Date:** 2026-06-30
**Purpose:** Evaluate suspicious pages against 10 diagnostic questions to identify scope bloat, theme drift, and cognitive load problems. No code changes in this pass.

---

## Diagnostic Questions

For each page under review, the following 10 questions are answered:

1. Does a real faculty user need this page on a weekly basis?
2. Does it help create or manage the exam timetable?
3. Does it help manage invigilation (assignment, availability, swaps)?
4. Does it help track exam paper / file handoff?
5. Does it help produce necessary draft finance documents?
6. Does it duplicate another page?
7. Does it require explanation before a user understands what it does?
8. Does it visually break the app theme (Yellow risk)?
9. Does it add maintenance burden without proportional value?
10. Should it be hidden, merged, simplified, or removed?

---

## Pages Under Review

---

### Page 1: Admin Intelligence Dashboard (`/admin-intelligence-dashboard`)

| Question | Answer | Notes |
|---------|--------|-------|
| 1. Weekly faculty need? | **No** | Admin may look once per term at most |
| 2. Helps exam timetable? | **No** | Shows platform metrics, not schedule data |
| 3. Helps invigilation? | **No** | No assignment or availability functionality |
| 4. Helps paper handoff? | **No** | No submissions/print/QR data |
| 5. Helps finance docs? | **No** | No payment calculation or export |
| 6. Duplicates another page? | **Partial** | Overlaps with Dashboard (operational metrics) |
| 7. Needs explanation first? | **Yes** | "Admin intelligence" requires context; faculty will not intuitively know what this does |
| 8. Theme-breaking? | **Yellow** | Uses data-dense visualization style; heavier than core pages |
| 9. Maintenance burden? | **High** | Complex component (lazy-loaded); partially wired; high hook complexity |
| 10. Action? | **HIDE_FROM_MAIN_NAV** | Keep route active for admin direct access; remove from sidebar |

**Evidence:** Added via `feat(ui): redesign admin intelligence dashboard` — motivated by demo maturity signaling, not by user request or operational need.

**Verdict:** This page demonstrates that the platform has intelligence capabilities, but it is not a daily tool for exam operations. It should not appear in the sidebar during pilot.

---

### Page 2: Executive Analytics (`/analytics`)

| Question | Answer | Notes |
|---------|--------|-------|
| 1. Weekly faculty need? | **No** | Institutional trend analysis is not a weekly exam-op task |
| 2. Helps exam timetable? | **No** | Shows trends, not the current schedule |
| 3. Helps invigilation? | **No** | No assignment functionality |
| 4. Helps paper handoff? | **No** | No handoff data |
| 5. Helps finance docs? | **No** | No payment functionality |
| 6. Duplicates another page? | **Yes** | Overlaps with Admin Intelligence Dashboard (both show analytics) |
| 7. Needs explanation first? | **Yes** | "Executive Analytics" is an enterprise term; faculty staff will not know what to do here |
| 8. Theme-breaking? | **Yellow** | Executive framing diverges from operational workflow style |
| 9. Maintenance burden? | **High** | Lazy-loaded; partially wired (D5 maturity); trend analysis requires historical data not yet in production |
| 10. Action? | **HIDE_FROM_MAIN_NAV** | Keep route; remove from sidebar entirely |

**Evidence:** D5 maturity designation in platform capability matrix. Currently accessible to admin, esq_head, secretary — but none of these roles need institutional trend analysis to run an exam period.

**Verdict:** Enterprise framing + D5 maturity + no daily operational value = remove from main nav immediately.

---

### Page 3: Governance Cockpit (`/governance`)

| Question | Answer | Notes |
|---------|--------|-------|
| 1. Weekly faculty need? | **Rarely** | Relevant during sign-off windows only |
| 2. Helps exam timetable? | **No** | Shows blockers, not schedule data |
| 3. Helps invigilation? | **Partial** | Blocker counts include assignment blockers |
| 4. Helps paper handoff? | **No** | No handoff data |
| 5. Helps finance docs? | **Partial** | Includes payment review status in some form |
| 6. Duplicates another page? | **Yes** | Dashboard already shows operational status; Workflow shows approval blockers |
| 7. Needs explanation first? | **Yes** | "Governance Cockpit" is an enterprise term; staff will not know this is a status aggregation tool |
| 8. Theme-breaking? | **Yellow** | Cockpit metaphor and governance framing diverges from exam-op workflow |
| 9. Maintenance burden? | **High** | D5 maturity; partially wired; governance concept doesn't have a clear Thai university equivalent |
| 10. Action? | **HIDE_FROM_MAIN_NAV** | Blocker visibility should live in Dashboard; workflow sign-off lives in Workflow |

**Evidence:** Governance Cockpit appears in same refactor commit as Executive Analytics, added as part of the "intelligence layer" build for demo signoff.

**Verdict:** The function is valuable (see all blockers in one place) but the framing is wrong and the page duplicates data already in Dashboard + Workflow. Hide from nav; consider merging blocker summary into Dashboard in Phase C.

---

### Page 4: Operational Health (`/operational-health`)

| Question | Answer | Notes |
|---------|--------|-------|
| 1. Weekly faculty need? | **No** | Faculty staff do not monitor backend service health |
| 2. Helps exam timetable? | **No** | System monitoring, not scheduling |
| 3. Helps invigilation? | **No** | No assignment functionality |
| 4. Helps paper handoff? | **No** | No handoff data |
| 5. Helps finance docs? | **No** | No payment functionality |
| 6. Duplicates another page? | **No** | Unique function |
| 7. Needs explanation first? | **Yes** | Health dashboards are IT/dev tools; faculty will not understand response time metrics |
| 8. Theme-breaking? | **Yellow** | Dev tool visual style does not match the exam-op workflow pages |
| 9. Maintenance burden? | **Medium** | Requires backend health endpoints; monitoring infrastructure |
| 10. Action? | **KEEP_INTERNAL_ADMIN_ONLY** | IT/dev tool; hide from sidebar; accessible by direct URL for admin |

**Verdict:** This page is legitimately useful for IT staff and developers monitoring the system. But it is not for faculty staff. It belongs in a developer/admin-only section, not the main sidebar.

---

### Page 5: Audit Explorer (`/audit-explorer`)

| Question | Answer | Notes |
|---------|--------|-------|
| 1. Weekly faculty need? | **No** | Audit review is infrequent and compliance-driven |
| 2. Helps exam timetable? | **No** | Shows audit events, not schedule data |
| 3. Helps invigilation? | **No** | No assignment functionality |
| 4. Helps paper handoff? | **No** | No handoff data |
| 5. Helps finance docs? | **No** | No payment functionality |
| 6. Duplicates another page? | **No** | Unique function (audit events) |
| 7. Needs explanation first? | **Yes** | Audit exploration requires technical context; faculty will not know why they're here |
| 8. Theme-breaking? | **Yellow** | Technical audit log style diverges from exam-op workflow pages |
| 9. Maintenance burden? | **Medium** | Depends on audit log infrastructure; filtering logic |
| 10. Action? | **KEEP_INTERNAL_ADMIN_ONLY** | Compliance/dev tool; hide from sidebar; URL-direct for admin/esq_head |

**Verdict:** Audit Explorer is a compliance and developer tool. It's important for PDPA compliance monitoring and incident investigation, but it should not appear in the sidebar for exam operations users.

---

### Page 6: Optimizer Trace Explorer (`/optimizer-trace`)

| Question | Answer | Notes |
|---------|--------|-------|
| 1. Weekly faculty need? | **No** | Only relevant after running optimization; debug use |
| 2. Helps exam timetable? | **Partial** | Shows how optimization decisions were made |
| 3. Helps invigilation? | **Partial** | Shows optimizer candidate lineage |
| 4. Helps paper handoff? | **No** | No handoff data |
| 5. Helps finance docs? | **No** | No payment functionality |
| 6. Duplicates another page? | **No** | Unique function |
| 7. Needs explanation first? | **Yes** | "Candidate lineage and scoring" requires deep technical knowledge of the optimizer |
| 8. Theme-breaking? | **Yellow** | Very high complexity; developer debug style |
| 9. Maintenance burden? | **Medium** | Tied to optimizer output format; lazy-loaded |
| 10. Action? | **KEEP_INTERNAL_ADMIN_ONLY** | Debug tool; hide from sidebar; accessible after optimization run for admin only |

**Verdict:** Optimizer Trace is a useful developer/admin debug tool to validate that optimization produced fair results. However, it requires understanding of optimization algorithm internals. Faculty staff who run the optimizer don't need to read trace output — they see the results on the schedule. Hide from sidebar; make available by direct URL after optimization.

---

### Page 7: Platform Configuration (`/platform-config`)

| Question | Answer | Notes |
|---------|--------|-------|
| 1. Weekly faculty need? | **No** | One-time or per-term configuration at most |
| 2. Helps exam timetable? | **No** | Faculty governance config, not schedule |
| 3. Helps invigilation? | **No** | No assignment functionality |
| 4. Helps paper handoff? | **No** | No handoff data |
| 5. Helps finance docs? | **No** | No payment functionality |
| 6. Duplicates another page? | **Partial** | Overlaps with Settings page in terms of system configuration |
| 7. Needs explanation first? | **Yes** | D3 faculty governance config requires deep institutional context |
| 8. Theme-breaking? | **Yellow** | Complex config UI style; empty arrays in backend snapshot imply functionality not yet operational |
| 9. Maintenance burden? | **High** | D3–D5 maturity; backend partially wired; governance config requires stakeholder decisions not yet made |
| 10. Action? | **KEEP_INTERNAL_ADMIN_ONLY** | Complex config; developer/IT setup tool; hide from sidebar |

**Critical note:** Backend snapshot shows empty arrays for Platform Config data. This means the page currently implies readiness for functionality that is not yet operational. Hiding it from the main nav prevents confusion about what the system can actually do.

**Verdict:** Platform Configuration is a system setup tool for IT and advanced admin users. The governance config it manages requires institutional decisions that are still pending. Hide from sidebar; keep URL access for admin.

---

### Page 8: Import Audit (`/import-audit`)

| Question | Answer | Notes |
|---------|--------|-------|
| 1. Weekly faculty need? | **Rarely** | Only needed after import runs (infrequent) |
| 2. Helps exam timetable? | **Partial** | Import feeds schedule data; audit helps verify |
| 3. Helps invigilation? | **No** | No assignment functionality |
| 4. Helps paper handoff? | **No** | No handoff data |
| 5. Helps finance docs? | **No** | No payment functionality |
| 6. Duplicates another page? | **No** | Unique function (import session logs) |
| 7. Needs explanation first? | **Partial** | More understandable than dev tools; admin can figure it out |
| 8. Theme-breaking? | **No** | Theme-consistent with import workflow |
| 9. Maintenance burden? | **Low** | Simple log browser; no complex wiring |
| 10. Action? | **KEEP_INTERNAL_ADMIN_ONLY** | Admin review tool; hide from main nav; admin can use directly after import |

**Verdict:** Import Audit is a legitimate admin tool but not a daily workflow item. After an import run, admin may want to review it — but it should not be a persistent nav item. Move to URL-direct admin access only.

---

### Page 9: Historical Schedules (`/historical-schedules`)

| Question | Answer | Notes |
|---------|--------|-------|
| 1. Weekly faculty need? | **Seasonally** | Primarily useful after optimization; post-term fairness review |
| 2. Helps exam timetable? | **Partial** | Shows comparison to previous terms |
| 3. Helps invigilation? | **Partial** | Historical assignment patterns help verify fairness |
| 4. Helps paper handoff? | **No** | No handoff data |
| 5. Helps finance docs? | **No** | No payment functionality |
| 6. Duplicates another page? | **No** | Unique function |
| 7. Needs explanation first? | **No** | "ประวัติตาราง" is self-explanatory once described |
| 8. Theme-breaking? | **No** | Theme-consistent |
| 9. Maintenance burden? | **Low** | Historical snapshot data; limited update frequency |
| 10. Action? | **KEEP_BUT_SIMPLIFY** | Expand role access; reduce nav prominence |

**Special note on role access:** The original audit request included the note: "ควรยังคงให้ทุกคนเห็นได้ เพื่อให้ตรวจสอบได้ว่า optimize แล้วมีความเป็นธรรมกับทุกคนหรือไม่" (should remain visible to all, so they can verify whether optimization was fair to everyone).

**Verdict:** Historical Schedules is legitimate and should remain accessible. However, it is currently admin-only in the nav. Consider expanding role access so staff and teachers can verify fairness. Lower nav prominence (secondary section) is appropriate.

---

### Page 10: Workload Duty Analytics (`/workload-duty-analytics`, `/duty-workload`, `/my-workload`)

| Question | Answer | Notes |
|---------|--------|-------|
| 1. Weekly faculty need? | **Sometimes** | Useful during assignment review and post-optimization verification |
| 2. Helps exam timetable? | **No** | Shows duty distribution, not schedule |
| 3. Helps invigilation? | **Yes** | Directly shows exam duty workload per person |
| 4. Helps paper handoff? | **No** | No handoff data |
| 5. Helps finance docs? | **Partial** | Workload data feeds into payment calculation |
| 6. Duplicates another page? | **Partial** | Three routes for one component creates apparent duplication |
| 7. Needs explanation first? | **No** | Workload is self-explanatory |
| 8. Theme-breaking? | **No** | Theme-consistent |
| 9. Maintenance burden? | **Low** | Single component used by all three routes |
| 10. Action? | **KEEP_BUT_SIMPLIFY** | Consolidate three nav entries into one labeled "ภาระงานคุมสอบ" |

**Technical note:** All three routes (`/workload-duty-analytics`, `/duty-workload`, `/my-workload`) use the same `WorkloadDutyAnalytics` component with role-filtered data. The routes themselves are already role-guarded correctly. The simplification is in the nav presentation: present as a single "Invigilation Workload" entry that routes to the correct path per role.

**Verdict:** Keep all three routes. Simplify nav to show one entry per role (which already happens via role filtering). Label should be "ภาระงานคุมสอบ" and grouped with invigilation, not analytics.

---

## Summary Table

| Page | Route | Score (Yes answers to Qs 1–5) | Duplicate? | Needs Explain? | Theme Break? | Action |
|------|-------|-------------------------------|-----------|---------------|------------|--------|
| Admin Intelligence Dashboard | `/admin-intelligence-dashboard` | 0/5 | Partial | Yes | Yellow | HIDE_FROM_MAIN_NAV |
| Executive Analytics | `/analytics` | 0/5 | Yes | Yes | Yellow | HIDE_FROM_MAIN_NAV |
| Governance Cockpit | `/governance` | 0/5 | Yes | Yes | Yellow | HIDE_FROM_MAIN_NAV |
| Operational Health | `/operational-health` | 0/5 | No | Yes | Yellow | KEEP_INTERNAL_ADMIN_ONLY |
| Audit Explorer | `/audit-explorer` | 0/5 | No | Yes | Yellow | KEEP_INTERNAL_ADMIN_ONLY |
| Optimizer Trace | `/optimizer-trace` | 0/5 | No | Yes | Yellow | KEEP_INTERNAL_ADMIN_ONLY |
| Platform Config | `/platform-config` | 0/5 | Partial | Yes | Yellow | KEEP_INTERNAL_ADMIN_ONLY |
| Import Audit | `/import-audit` | 0/5 | No | Partial | No | KEEP_INTERNAL_ADMIN_ONLY |
| Historical Schedules | `/historical-schedules` | 1/5 | No | No | No | KEEP_BUT_SIMPLIFY |
| Workload Analytics (×3) | `/workload-duty-analytics` etc. | 2/5 | Partial | No | No | KEEP_BUT_SIMPLIFY |

**Pattern:** All pages scoring 0/5 on the five core questions (timetable, invigilation, handoff, finance, weekly use) are candidates for hiding from the main nav. None should be removed outright — they have legitimate value for admin, IT, and dev users.

---

## Theme Drift Assessment

Pages marked **Yellow** in the "Theme Break?" column share a common pattern:
- They use data-visualization-heavy layouts not seen in core operational pages
- They use terminology from enterprise software ("intelligence", "governance", "executive", "platform")
- They were often lazy-loaded, suggesting they were added later and are less performance-critical
- Their visual weight (chart density, metric cards, filter panels) is higher than the workflow-focused core pages

**The EMS visual theme** is: clean, role-colored, task-focused, Thai-first. The "Yellow" pages introduce an enterprise BI aesthetic that conflicts with this.

**Recommendation:** Hiding these pages from the main nav is sufficient for Phase B. No visual redesign is needed. If these pages remain admin-accessible by URL, their visual style is not a user-facing problem during the pilot.

---

## Maintenance Burden Summary

| Burden Level | Pages |
|-------------|-------|
| High | Admin Intelligence Dashboard, Executive Analytics, Governance Cockpit, Platform Config |
| Medium | Operational Health, Audit Explorer, Optimizer Trace |
| Low | Import Audit, Historical Schedules, Workload Analytics |

High-burden pages require the most care in any future cleanup. They are the most likely to have partial wiring, stale data, or D5 maturity features. This is another argument for hiding them from the pilot nav rather than surfacing them to faculty staff who will find them confusing or broken.
