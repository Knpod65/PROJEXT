# Dashboard Clarity Hardening

## Overview
This document defines improvements to metric descriptions, tooltips, explanations, and actionable guidance across all EMS dashboards to reduce user confusion and increase trust in operational metrics.

## Principles

1. **Every metric must answer**: What is this? Why does it matter? What should I do?
2. **No unexplained numbers**: Every score, count, or percentage must have context (target, threshold, trend)
3. **Actionable language**: Replace "review" with specific next steps when possible
4. **Consistent structure**: All metric cards follow the same explanation pattern
5. **Progressive disclosure**: Core info visible, details on hover/click

---

## Metric Explanation Template

Each metric card should include (visible or on hover):

### Visible by Default
- **Metric Name**: Clear, jargon-free label
- **Current Value**: With unit (e.g., "47 sections", "0.42 score")
- **Severity Badge**: Color-coded (good/info/warning/critical)

### On Hover / Info Icon
- **What This Measures**: One-sentence definition
- **Why This Matters**: Business/operational impact (1-2 sentences)
- **Target / Threshold**: What is "good"? (e.g., "Target: < 0.30", "Green: 0-0.30, Amber: 0.30-0.50, Red: > 0.50")
- **Recommended Action**: Specific next step (e.g., "Review staff availability and reassign overloaded invigilators")

### Optional (Advanced Users)
- **Calculation Method**: How is this derived? (expandable)
- **Data Sources**: Which backend services contribute? (expandable)
- **Last Updated**: Timestamp with freshness indicator

---

## Admin Intelligence Dashboard — Clarity Improvements

### Group 1: Exam Operations

#### Metric: Unscheduled Sections
**Current State**: Shows count with severity badge

**Hardening**:
- **Why This Matters**: "Unassigned sections block the publication-ready date and delay student exam notifications. Each unscheduled section represents a student cohort without confirmed exam logistics."
- **Target**: "Target: 0. Green: 0-1, Amber: 2-10, Red: >10"
- **Recommended Action**: "Navigate to Schedule page → Filter by 'Unscheduled' → Assign rooms and dates"

#### Metric: Scheduled Sections
**Current State**: Shows count

**Hardening**:
- **Why This Matters**: "Percentage of total sections with confirmed exam logistics. Higher is better; indicates operational readiness."
- **Context**: "X of Y total sections (Z%)"
- **Target**: "Target: 100%. Amber warning below 95%."

#### Metric: Rooms In Use
**Current State**: Shows count

**Hardening**:
- **Why This Matters**: "Active room utilization during exam period. Helps identify capacity constraints and venue planning needs."
- **Context**: "X rooms currently allocated across all exam sessions"
- **Target**: "No hard target; monitor for >80% of available rooms to flag capacity risk."

---

### Group 2: Optimization Quality

#### Metric: Quality Score
**Current State**: Shows score (0-100) with severity

**Hardening**:
- **What This Measures**: "Composite score reflecting optimization success: constraint satisfaction, fairness, and utilization balance."
- **Why This Matters**: "Higher scores indicate schedules that are more likely to be accepted by stakeholders with fewer conflicts and more equitable workload distribution."
- **Target**: "Target: ≥80 (Green). Amber: 60-79. Warning: 40-59. Critical: <40."
- **Recommended Action**: "Review Optimization Trace for low-scoring constraint categories. Consider re-running with adjusted weights."

#### Metric: Fairness Score (from Workload Analytics)
**Current State**: Shows imbalance score (0.0 - 1.0)

**Hardening**:
- **What This Measures**: "Statistical measure of workload distribution variance across staff. Lower is fairer."
- **Why This Matters**: "High imbalance indicates some staff are significantly over-burdened while others are under-utilized. This affects morale, burnout risk, and operational resilience."
- **Target**: "Green: 0.00-0.30 (fair). Amber: 0.30-0.50 (moderate imbalance). Red: >0.50 (high imbalance — action required)."
- **Recommended Action**: "Review overloaded staff list → Identify underloaded colleagues → Reassign duties to balance load."

---

### Group 3: Governance / Approval

#### Metric: Blocker Count
**Current State**: Shows count with severity

**Hardening**:
- **Why This Matters**: "Active governance blockers prevent schedule publication. Each blocker represents a policy violation, resource conflict, or approval gap that must be resolved before release."
- **Target**: "Target: 0. Any count >0 blocks publication readiness."
- **Recommended Action**: "Navigate to Governance Cockpit → Review blocker details by category (rooms, invigilators, policy) → Resolve or escalate."

#### Metric: Pending Approvals
**Current State**: Shows count

**Hardening**:
- **Why This Matters**: "Approvals awaiting action. Long-pending approvals risk delaying the publication timeline and indicate potential process bottlenecks."
- **Context**: "X pending, Y overdue (>48h), Z at-risk (24-48h)"
- **Target**: "Target: 0 overdue. Warning if any >48h pending."
- **Recommended Action**: "Review pending list → Prioritize overdue items → Escalate if approver unavailable."

---

### Group 4: Staff / Workload

#### Metric: Staff Imbalance Score
**Current State**: Shows score (0.0 - 1.0)

**Hardening**:
- **What This Measures**: "Normalized standard deviation of invigilation workload across all staff. 0.0 = perfectly balanced, 1.0 = maximum observed imbalance."
- **Why This Matters**: "Imbalance affects staff satisfaction, burnout risk, and operational resilience. High imbalance may indicate scheduling bias or capacity constraints."
- **Target**: "Green: 0.00-0.30. Amber: 0.30-0.50. Red: >0.50 (action recommended)."
- **Recommended Action**: "Review Overloaded Staff list → Compare with Underloaded Staff → Consider reassignment or availability adjustment."

#### Metric: Overloaded Staff Count
**Current State**: Shows count

**Hardening**:
- **Why This Matters**: "Staff whose invigilation load exceeds fair-share threshold by >50%. These individuals are at elevated burnout risk and may require support or reassignment."
- **Context**: "X staff overloaded by Y% on average"
- **Recommended Action**: "Review list → Contact overloaded staff → Explore redistribution options with underloaded colleagues."

---

### Group 5: Room / Capacity

#### Metric: Room Utilization Score
**Current State**: Shows percentage

**Hardening**:
- **What This Measures**: "Average percentage of room capacity utilized across all scheduled sessions. Higher = more efficient venue usage."
- **Why This Matters**: "Low utilization indicates wasted venue capacity and potential for consolidation. Very high utilization (>90%) risks bottlenecks and last-minute conflicts."
- **Target**: "Target: 60-80% (efficient). Amber: <60% (under-utilized) or >80% (high pressure)."
- **Recommended Action**: "Review under-utilized rooms → Consider consolidation. Review over-utilized rooms → Plan for overflow venues."

---

### Group 6: Teacher Submission

#### Metric: Submission Rate
**Current State**: Shows percentage

**Hardening**:
- **Why This Matters**: "Percentage of teachers who have submitted required exam materials. Low rates delay grading preparation and increase last-minute workload for academic services."
- **Target**: "Target: 100% by deadline. Amber warning: <95% within 3 days of deadline."
- **Recommended Action**: "Review non-submitters list → Send reminders → Escalate to department heads if needed."

---

### Group 7: Print / Export

#### Metric: Print Queue Size
**Current State**: Shows count

**Hardening**:
- **Why This Matters**: "Batches awaiting print shop processing. Large queues indicate potential delays in material distribution to students."
- **Target**: "Monitor for >50 items. Critical: >100 items (action required)."
- **Recommended Action**: "Review queue → Prioritize urgent batches → Consider additional print resources if sustained high volume."

#### Metric: Ready to Print
**Current State**: Shows count

**Hardening**:
- **Why This Matters**: "Batches approved and queued for immediate printing. Indicates current print shop workload."
- **Context**: "X batches ready, estimated Y hours to complete at current capacity"

---

### Group 8: QR / Pickup

#### Metric: QR Redeems (24h)
**Current State**: Shows count

**Hardening**:
- **Why This Matters**: "Successful QR code scans for exam material pickup in last 24 hours. High redeem rate indicates effective communication and smooth pickup logistics."
- **Target**: "Target: ≥90% of expected pickups. Amber: 70-89%. Red: <70%."
- **Recommended Action**: "Review low-redeem periods → Check communication channels → Verify QR code functionality."

---

### Group 9: PDPA / Security (Restricted)

#### Metric: PDPA Alerts (24h)
**Current State**: Shows count (restricted access)

**Hardening**:
- **Why This Matters**: "Security and privacy events detected in last 24 hours. Each alert represents a potential policy violation or data exposure requiring investigation."
- **Target**: "Target: 0 sustained. Any count >0 requires DPO review."
- **Recommended Action**: "DPO: Review alert log → Investigate high-severity events → Document resolution."

---

### Group 10: System / Operations

#### Metric: API Responsive
**Current State**: Shows uptime percentage

**Hardening**:
- **Why This Matters**: "API availability over monitoring period. Downtime affects all user-facing functionality and indicates infrastructure issues."
- **Target**: "Target: ≥99.5%. Amber: 99.0-99.4%. Red: <99.0%."
- **Recommended Action**: "IT: Review API logs → Identify outage patterns → Escalate to infrastructure team."

#### Metric: Database Connected
**Current State**: Boolean (OK / Error)

**Hardening**:
- **Why This Matters**: "Database connectivity status. Database failure blocks all data operations including schedule queries, submissions, and exports."
- **Target**: "Target: Connected (true). Any disconnection requires immediate IT response."
- **Recommended Action**: "IT: Check database service status → Verify connection string → Restart if needed."

#### Metric: Storage Usage
**Current State**: Shows percentage

**Hardening**:
- **Why This Matters**: "Percentage of storage capacity in use. High usage risks data loss, backup failures, and system instability."
- **Target**: "Target: <80%. Amber: 80-90%. Critical: >90% (immediate cleanup required)."
- **Recommended Action**: "IT: Review storage breakdown → Archive old data → Expand capacity if sustained high usage."

---

## Role Dashboard — Clarity Improvements

### Staff Role Dashboard

#### Metric: Active Invigilations
**Hardening**:
- **Why This Matters**: "Your current invigilation assignments requiring attention. Track these to ensure coverage and avoid conflicts."
- **Recommended Action**: "Click to view detailed schedule → Check for conflicts → Confirm availability"

#### Metric: Upcoming Blocks
**Hardening**:
- **Why This Matters**: "Scheduled time blocks in the near future. Plan for these to avoid double-booking and ensure adequate preparation time."
- **Recommended Action**: "Review for conflicts with personal schedule → Request swap if needed"

#### Metric: My Supervision Count
**Hardening**:
- **Why This Matters**: "Total supervision assignments across the exam period. Helps you anticipate workload and plan personal schedule."
- **Context**: "X assignments this period, average Y per staff member"

---

### Teacher Role Dashboard

#### Metric: My Upcoming Exams
**Hardening**:
- **Why This Matters**: "Exams you are scheduled to administer. Confirm dates, times, and rooms to ensure smooth exam delivery."
- **Recommended Action**: "Review room details → Plan arrival time → Prepare required materials"

#### Metric: Submission Status
**Hardening**:
- **Why This Matters**: "Status of your exam material submissions. Timely submission ensures grading preparation and avoids last-minute pressure."
- **Context**: "Deadline: [date]. Status: Submitted / Pending / Overdue"
- **Recommended Action**: "If pending: Submit materials → If overdue: Contact department head"

#### Metric: Exam Date / Room
**Hardening**:
- **Why This Matters**: "Confirmed logistics for your next exam. Verify building location, room capacity, and equipment availability."
- **Context**: "Building: [name]. Capacity: [X] seats. Equipment: [list]"
- **Recommended Action**: "Confirm room access → Plan travel time → Arrive 30 min early"

---

### Student Role Dashboard

#### Metric: Next Exam
**Hardening**:
- **Why This Matters**: "Your next scheduled examination. Confirm date, time, and location to ensure you arrive prepared."
- **Recommended Action**: "Review full timetable → Confirm room location → Arrive 15 min early"

#### Metric: Schedule Completeness
**Hardening**:
- **Why This Matters**: "Percentage of your exam schedule that is finalized. Higher = fewer surprises and better preparation time."
- **Target**: "Target: 100%. If <100%, contact administration for missing exam details."
- **Context**: "X of Y exams confirmed. Z exams pending assignment."

---

### Print Shop Role Dashboard

#### Metric: Print Queue Size
**Hardening**:
- **Why This Matters**: "Total batches awaiting processing. Large queues indicate high demand; prioritize urgent items to avoid student delays."
- **Context**: "X urgent (today), Y standard (this week)"
- **Recommended Action**: "Review urgent queue → Process high-priority batches first → Communicate delays if queue >50"

#### Metric: Ready to Print
**Hardening**:
- **Why This Matters**: "Approved batches queued for immediate printing. Indicates current workload and capacity."
- **Recommended Action**: "Process queue in order → Update status for stakeholders → Flag capacity issues if sustained high volume"

#### Metric: Awaiting Pickup
**Hardening**:
- **Why This Matters**: "Completed batches ready for collection. Notify stakeholders to minimize storage time and ensure timely distribution."
- **Recommended Action**: "Notify recipients → Track pickup within 48h → Follow up on uncollected items"

---

### Dept Supervisor Role Dashboard

#### Metric: Dept Unscheduled Count
**Hardening**:
- **Why This Matters**: "Sections in your department without confirmed exam logistics. These risk publication delays and student notification gaps."
- **Context**: "X of Y department sections unscheduled (Z%)"
- **Recommended Action**: "Review unscheduled list → Coordinate with course coordinators → Escalate persistent gaps"

#### Metric: Dept Submission Rate
**Hardening**:
- **Why This Matters**: "Percentage of teachers in your department who have submitted required materials. Low rates delay grading preparation."
- **Target**: "Target: 100% by deadline. Amber: <95% within 3 days of deadline."
- **Recommended Action**: "Review non-submitters → Send department reminders → Escalate to dean if needed"

---

### DPO Role Dashboard

#### Metric: PDPA Alerts (7d)
**Hardening**:
- **Why This Matters**: "Security and privacy events in the last 7 days. Each alert requires investigation to ensure compliance and protect sensitive data."
- **Target**: "Target: 0 sustained. Trending upward requires proactive review."
- **Recommended Action**: "Review alert log → Investigate high-severity events → Document resolution and preventive measures"

#### Metric: Audit Gaps
**Hardening**:
- **Why This Matters**: "Identified gaps in audit trail coverage. Gaps may indicate logging failures or process bypasses requiring remediation."
- **Target**: "Target: 0. Any gap requires investigation and logging verification."
- **Recommended Action**: "Review gap details → Verify logging configuration → Remediate process bypasses"

#### Metric: Restricted Exports (7d)
**Hardening**:
- **Why This Matters**: "Exports containing restricted or confidential data in the last 7 days. Track to ensure proper authorization and data handling."
- **Target**: "Monitor for unusual volume or patterns. Any unauthorized export requires immediate investigation."
- **Recommended Action**: "Review export log → Verify authorization chain → Investigate anomalies"

---

### IT Role Dashboard

#### Metric: API Responsive
**Hardening**:
- **Why This Matters**: "API availability percentage. Downtime affects all user-facing functionality and indicates infrastructure health."
- **Target**: "Target: ≥99.5%. Amber: 99.0-99.4%. Critical: <99.0% (immediate response)."
- **Recommended Action**: "Review API logs → Identify outage patterns → Engage infrastructure team for persistent issues"

#### Metric: Database Connected
**Hardening**:
- **Why This Matters**: "Database connectivity status. Database failure blocks all data operations and indicates critical infrastructure problems."
- **Target**: "Target: Connected. Any disconnection requires immediate investigation."
- **Recommended Action**: "Check database service status → Verify connection parameters → Restart or failover if needed"

#### Metric: Storage Usage
**Hardening**:
- **Why This Matters**: "Percentage of storage capacity in use. High usage risks data loss, backup failures, and system instability."
- **Target**: "Target: <80%. Amber: 80-90%. Critical: >90% (immediate cleanup or expansion)."
- **Recommended Action**: "Review storage breakdown → Archive old logs/data → Expand capacity or implement cleanup automation"

#### Metric: Scheduler Heartbeat
**Hardening**:
- **Why This Matters**: "Time since last scheduler cycle. Stale heartbeat indicates potential job failures or resource contention."
- **Target**: "Target: <15 minutes. Amber: 15-30 minutes. Critical: >30 minutes (investigate immediately)."
- **Recommended Action**: "Check scheduler service status → Review recent job logs → Restart or debug as needed"

---

## Global Clarity Improvements

### 1. Add "Why This Matters" to All Metric Tooltips
**Implementation**:
- Add info icon (ⓘ) next to every metric name
- On hover/click: Expandable panel with explanation
- Consistent format: "What / Why / Target / Action"

### 2. Add Target/Threshold Indicators
**Implementation**:
- For every scored metric, show target value or acceptable range
- Color-code current value against target (green = on target, amber = near target, red = off target)
- Example: "Imbalance Score: 0.42 (Target: <0.30 | Amber: 0.30-0.50 | Red: >0.50)"

### 3. Add Trend Indicators
**Implementation**:
- For metrics supporting historical comparison, show trend arrow (↑/↓/→)
- Context: "↑ 12% since yesterday" or "↓ 5 points from last week"
- Improves situational awareness without requiring manual comparison

### 4. Standardize Alert Language
**Before**: "Workload imbalance detected"
**After**: "Workload imbalance score (0.42) exceeds amber threshold (0.30). 3 staff members overloaded by average 45%. Review and reassign duties to restore balance."

### 5. Add "What Changed" Delta Cards
**Implementation**:
- At top of Admin Intelligence Dashboard: "Changes Since Yesterday"
- List metrics with significant changes (↑/↓ >10%)
- Example: "Unscheduled Sections: ↑ 8 (from 12 to 20) — Action: Assign rooms"

---

## Implementation Priority

### Phase 1 (Immediate — Week 1)
1. Add "Why This Matters" tooltips to top 10 most-viewed metrics
2. Add target/threshold indicators to all scored metrics (imbalance, quality, utilization)
3. Standardize alert language for CRITICAL and HIGH severity alerts

### Phase 2 (Week 2-3)
4. Add trend indicators to metrics with historical data
5. Implement "Changes Since Yesterday" summary card
6. Add "What Changed" delta tracking for key operational metrics

### Phase 3 (Week 4+)
7. Expand explanations to all remaining metrics
8. Add calculation method details for advanced users (expandable)
9. Implement user feedback loop for explanation clarity

---

## Success Metrics

- **Reduced Support Tickets**: Track "What does X metric mean?" questions (target: <5/week)
- **User Satisfaction Survey**: "Dashboard metrics are clear and actionable" (target: >80% agree/strongly agree)
- **Time to Decision**: Measure time from dashboard view to action taken (target: <2 minutes for common workflows)
- **False Alert Rate**: Track alerts dismissed without action (target: <20% of total alerts)

---

*Document version: 1.0*
*Created: 2026-05-20*
*Owner: UX / Product Team*
*Review Cycle: Bi-weekly during pilot*