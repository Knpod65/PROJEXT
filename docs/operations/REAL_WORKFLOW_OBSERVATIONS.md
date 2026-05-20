# Real Workflow Observations

## Overview
This document captures observations from real pilot usage of EMS dashboards and workflows. It identifies friction points, confusion areas, and opportunities for operational hardening.

## Observation Methodology

### Sources
- Pilot user feedback sessions (weekly)
- Screen recordings of common workflows
- Support ticket analysis
- Dashboard usage analytics (page load times, filter usage, export frequency)
- Direct observation of admin/staff/teacher workflows

### Observation Period
- Week 1-2: Admin + Staff focus
- Week 3-4: Add Supervisor workflows
- Week 5-6: Add Teacher workflows
- Ongoing: Continuous feedback collection

---

## Admin Workflows

### Workflow 1: Daily Operational Review
**Observed Behavior**:
- Admin opens Admin Intelligence Dashboard first thing in morning
- Reviews critical alerts row (typically 2-4 alerts)
- Clicks through to specific metric groups for details
- Cross-references with Workload Duty Analytics for fairness concerns

**Friction Points Identified**:
1. **Alert Descriptions Too Generic**
   - Current: "Workload imbalance detected"
   - User Comment: "Which staff? Which department? How bad?"
   - Impact: Requires clicking into analytics to understand scope

2. **No Quick Summary of Changes Since Yesterday**
   - Admin wants to know: "What got worse? What improved?"
   - Current state: Must compare manually across days
   - Requested: "Delta since last login" or "Changes in last 24h"

3. **Risk Band Explanations Unclear**
   - User Comment: "Why is overall health 'amber' today? What pushed it over?"
   - Current: Risk band shown but no breakdown of contributing factors
   - Requested: "Top 3 factors affecting health score"

**Recommended Hardening**:
- Add "Changes Since Yesterday" summary card at top of Admin Intelligence Dashboard
- Expand alert tooltips with specific counts and affected entities
- Add "Health Score Breakdown" panel showing contribution of each metric group

---

### Workflow 2: Governance Status Check
**Observed Behavior**:
- Admin reviews Governance Cockpit for pending approvals and blockers
- Checks Optimization Trace Explorer for recent optimization runs
- Verifies publication readiness before approving schedule release

**Friction Points Identified**:
1. **Blocker Details Insufficient**
   - Current: Shows "5 governance blockers"
   - User Comment: "What kind? Which departments? Can I resolve from here?"
   - Impact: Must navigate to multiple pages to understand and act

2. **Pending Approvals Lack Urgency Indicators**
   - Current: Shows count and list
   - User Comment: "Which ones are approaching SLA? Which are already overdue?"
   - Requested: Color-code by age (green <24h, amber 24-48h, red >48h)

3. **Optimization Quality Score Context Missing**
   - Current: Shows "Quality Score: 72"
   - User Comment: "Is 72 good or bad? What was it last time? What's the target?"
   - Requested: Trend indicator + target threshold annotation

**Recommended Hardening**:
- Add urgency indicators (age-based color coding) to pending approvals list
- Add blocker categorization (rooms, invigilators, conflicts, policy) with counts
- Add trend arrows and target lines to quality score display

---

### Workflow 3: Pre-Publication Checklist
**Observed Behavior**:
- Admin reviews all 10 metric groups before approving schedule publication
- Checks for any critical alerts
- Verifies workload balance and room utilization
- Confirms no PDPA issues in pdpaSecurity group

**Friction Points Identified**:
1. **No Single "Ready to Publish" Indicator**
   - Current: Admin must check all 10 groups manually
   - User Comment: "Is there a summary that says 'all clear' or 'X issues blocking'?"
   - Requested: Publication Readiness Score (0-100) with blocking issues highlighted

2. **PDPA Security Group Always Shows Restricted**
   - Current: pdpaSecurity metrics show "[RESTRICTED]" for non-DPO roles
   - User Comment: "I can't tell if there are PDPA issues or not. Should I be worried?"
   - Requested: Aggregate indicator (e.g., "PDPA Status: Clear" or "3 alerts — review required")

**Recommended Hardening**:
- Add "Publication Readiness Score" at top of Admin Intelligence Dashboard
- Show aggregate PDPA status (count of alerts, severity) without exposing restricted details
- Add "Blocking Issues Summary" card listing all critical/warning items preventing publication

---

## Staff Workflows

### Workflow 1: Daily Assignment Review
**Observed Behavior**:
- Staff opens Role Dashboard (staff view)
- Reviews active invigilations count
- Checks upcoming blocks for conflicts
- Reviews supervision assignments

**Friction Points Identified**:
1. **No Quick Link to Personal Schedule**
   - Current: Shows counts but no direct link to "My Assignments" page
   - User Comment: "I want to click '12 active invigilations' and see the list"
   - Requested: Clickable metrics that navigate to filtered schedule view

2. **Upcoming Blocks Lack Conflict Warnings**
   - Current: Shows upcoming blocks count
   - User Comment: "Do any of these conflict with my other duties?"
   - Requested: Highlight blocks with potential conflicts (double-booking, travel time)

**Recommended Hardening**:
- Make metric cards clickable with drill-down to filtered views
- Add conflict detection for upcoming blocks (highlight in amber/red)
- Add "My Schedule" quick link from Role Dashboard

---

### Workflow 2: Workload Balance Check
**Observed Behavior**:
- Staff reviews Workload Duty Analytics for department overview
- Checks imbalance score
- Identifies overloaded colleagues
- Plans redistribution

**Friction Points Identified**:
1. **Imbalance Score Interpretation Unclear**
   - Current: Shows "Imbalance Score: 0.42"
   - User Comment: "Is 0.42 good or bad? What's the threshold for action?"
   - Requested: Color-coded band (green <0.3, amber 0.3-0.5, red >0.5) + explanation

2. **Overloaded Staff List Lacks Contact Info**
   - Current: Shows names and duty counts
   - User Comment: "How do I contact them to discuss redistribution?"
   - Requested: Email or department contact link next to each overloaded staff member

**Recommended Hardening**:
- Add color-coded risk bands to imbalance score with threshold explanations
- Add contact/department links to overloaded staff list
- Add "Suggested Redistribution" recommendations (pair overloaded with underloaded)

---

## Teacher Workflows

### Workflow 1: Personal Exam Review
**Observed Behavior**:
- Teacher opens Role Dashboard (teacher view)
- Reviews "My Upcoming Exams" count
- Checks submission status
- Notes exam date and room

**Friction Points Identified**:
1. **Submission Status Unclear**
   - Current: Shows "Submission Status: n/a" or "Pending"
   - User Comment: "What exactly is pending? Which exam? What's the deadline?"
   - Requested: Link to specific submission with deadline and status

2. **No Reminder for Upcoming Deadlines**
   - Current: Static view, no proactive notifications
   - User Comment: "I want to know 3 days before a submission deadline"
   - Requested: Upcoming deadline alerts (3 days, 1 day before)

**Recommended Hardening**:
- Make submission status clickable with direct link to submission form
- Add deadline countdown and urgency indicators
- Add "Upcoming Deadlines" alert section (3-day, 1-day warnings)

---

### Workflow 2: Exam Preparation
**Observed Behavior**:
- Teacher reviews exam date, time, and room
- Checks if room is familiar
- Plans travel time

**Friction Points Identified**:
1. **Room Details Insufficient**
   - Current: Shows "Room: 301"
   - User Comment: "Where is building 3? How many seats? What equipment?"
   - Requested: Building name, capacity, equipment notes, map link

2. **No Travel Time Estimate**
   - Current: No context for planning arrival
   - User Comment: "How early should I arrive? Is there parking?"
   - Requested: Estimated travel time from campus main gate + parking notes

**Recommended Hardening**:
- Expand room display with building, capacity, equipment, accessibility notes
- Add "Recommended Arrival Time" based on exam start + travel estimate
- Add parking and building access notes for off-campus teachers

---

## Supervisor Workflows

### Workflow 1: Department Oversight
**Observed Behavior**:
- Supervisor opens Role Dashboard (dept_supervisor view)
- Reviews department unscheduled count
- Checks department submission rate
- Identifies at-risk sections

**Friction Points Identified**:
1. **Unscheduled Count Lacks Breakdown**
   - Current: Shows "15 unscheduled sections"
   - User Comment: "Which courses? Which exam periods? How urgent?"
   - Requested: Breakdown by course, exam type, urgency level

2. **Submission Rate Not Actionable**
   - Current: Shows "78% submitted"
   - User Comment: "Which 22% are missing? Who do I remind?"
   - Requested: List of non-submitters with contact info and reminder action

**Recommended Hardening**:
- Add breakdown table for unscheduled sections (by course, period, urgency)
- Add non-submitter list with email links and "Send Reminder" action
- Add at-risk sections highlighted with recommended actions

---

## Cross-Role Observations

### Common Confusion Points

1. **"What does this metric actually mean?"**
   - Observed across all roles
   - Metric names are clear, but business meaning is not
   - Example: "Staff Imbalance Score: 0.35" — what does 0.35 represent?

2. **"Is this number good or bad?"**
   - No target/threshold context for most metrics
   - Users don't know if action is required
   - Example: "Room Utilization: 62%" — is this acceptable?

3. **"What should I do about this?"**
   - Alerts and warnings lack clear next steps
   - Users know there's a problem but not how to fix it
   - Example: "Workload imbalance detected" — how do I rebalance?

### Recommended Global Hardening
- Add "Why This Matters" explanation to every metric (expandable tooltip or info icon)
- Add target/threshold indicators (green band, amber band, red band) for all scored metrics
- Add "Recommended Action" text to every alert and warning
- Add "What Changed" delta indicators for metrics that support trending

---

## Usability Friction Log

| Date | Role | Page | Friction | Severity | Workaround | Status |
|------|------|------|----------|----------|------------|--------|
| 2026-05-20 | Admin | Admin Intelligence | No "changes since yesterday" summary | Medium | Manual comparison | Open |
| 2026-05-20 | Staff | Role Dashboard | Metric cards not clickable | Low | Navigate manually | Open |
| 2026-05-21 | Teacher | Role Dashboard | Submission status unclear | Medium | Check email for reminders | Open |
| 2026-05-21 | Supervisor | Workload Analytics | No contact info for overloaded staff | Low | Look up in user directory | Open |

---

## Next Steps

1. Prioritize friction points by severity and user impact
2. Implement hardening improvements in iterative releases
3. Re-observe workflows after each hardening iteration
4. Update this document with resolution status
5. Track user satisfaction with dashboard clarity over pilot duration

---

*Document version: 1.0*
*Created: 2026-05-20*
*Owner: UX / Operations Team*
*Update Frequency: Weekly during pilot*