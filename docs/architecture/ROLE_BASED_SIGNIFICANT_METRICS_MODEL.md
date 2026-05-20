# Role-Based Significant Metrics Model

**Phase:** OPS-DASH-s0
**Purpose:** Define the metric model for every EMS role so each dashboard answers:
1. What is happening?
2. Why does it matter?
3. Who should act?
4. What should be done next?

---

## Metric Anatomy

Every metric must carry these fields:

| Field | Purpose |
|-------|---------|
| `metric_code` | Unique ID, used in drilldown / deep-link routes |
| `title_i18n_key` | i18n key — NOT a raw display string |
| `description_i18n_key` | i18n key for the one-line explanation of the metric |
| `value` | Current value — int, float, or string |
| `unit` | What the number means (e.g. "sections", "%", "count") |
| `trend` | `up` \| `down` \| `flat` \| `unknown` |
| `trend_label_i18n_key` | i18n key for the trend direction text |
| `severity` | `good` \| `info` \| `warning` \| `critical` |
| `pdpa_level` | `public` \| `internal` \| `confidential` \| `restricted` |
| `why_it_matters_i18n_key` | i18n key explaining business / operational impact |
| `recommended_action_i18n_key` | i18n key for what the user should do |
| `owner_role` | Role responsible for acting on this metric |
| `drilldown_route` | URL path to drill into (or `null`) |
| `updated_at` | ISO-8601 timestamp or `null` |

---

## Role Profiles (10 roles)

### 1 · Admin

**Key Questions**
- Are all sections scheduled and published on time?
- Is the optimizer producing fair, valid schedules?
- Are governance approvals flowing?
- Are any staff members overloaded?
- Are rooms being used efficiently?
- Have all teachers submitted their exam materials?
- Is the print / export queue stuck?
- Is QR-based pickup operating normally?
- Any PDPA exposure in the last period?
- Is the system healthy?

**Admin Metric Domains**

#### Group 1 — Exam Operations

| Metric | Why It Matters | Recommended Action | Owner | PDPA | Freq |
|--------|---------------|--------------------|-------|------|------|
| `unscheduled_sections` | Sections without a room/date block publication | Assign rooms and dates immediately | admin | internal | hourly |
| `hard_fail_rate` | Sections that fail hard validation rules | Investigate failed validations | admin | internal | per optimize run |
| `blocked_publications` | Schedule publications blocked — governance gates hold final sign-off | Review governance blockers; escalate if needed | admin / esq_head | internal | per blockade |
| `room_conflict_count` | Two sections booked in same room at same time | Reassign conflicting sections | admin | internal | per optimize run |
| `missing_invigilators` | Sections with no assigned supervision | Fill supervision slots before publish | admin / staff | internal | daily |
| `new_unscheduled_count_24h` | Unscheduled sections created in last 24 h | Early warning — may indicate data quality issue | admin | internal | hourly |

#### Group 2 — Optimization Quality

| Metric | Why It Matters | Recommended Action | Owner | PDPA | Freq |
|--------|---------------|--------------------|-------|------|------|
| `conflict_count` | Room / time conflicts remain after optimization | Re-run optimizer with clearer constraints | admin | internal | per run |
| `fairness_score` | Load imbalance across teachers / sections | Adjust constraints, filter, or split sections | admin | internal | per run |
| `optimization_quality_score` | Composite quality from optimizer pipeline (0-100) | Investigate low scoring runs via trace explorer | admin | internal | per run |
| `recheck_rate` | Pct of schedules that required a recheck | Review recheck issues; may indicate unstable inputs | admin / staff | internal | daily |
| `steepness_index` | How sharply fairness degrades when quality increases | Decide quality–fairness trade-off | admin | internal | per run |

#### Group 3 — Governance / Approval

| Metric | Why It Matters | Recommended Action | Owner | PDPA | Freq |
|--------|---------------|--------------------|-------|------|------|
| `blocker_count` | Sections stuck in blocked state cannot be published | Clear blocker via workflow signing round | esq_head / admin | internal | hourly |
| `pending_approvals` | Awaiting signature — delays publication | Notify next signer | secretary / esq_head | internal | hourly |
| `escalation_count` | Workflow forced to escalate level — needs attention | Manual override or correct the root cause | admin | internal | hourly |
| `override_count` | Override log entries — approval gates bypassed | Audit override reason; confirm intentionality | esq_head / admin | confidential | per approve |
| `rollback_event_count` | Schedule reverted to a prior state | Investigate what triggered the rollback | admin | internal | per event |

#### Group 4 — Staff / Workload

| Metric | Why It Matters | Recommended Action | Owner | PDPA | Freq |
|--------|---------------|--------------------|-------|------|------|
| `staff_imbalance_score` | Std deviation normalized by mean load | Distribute overloaded invigilations | admin / staff | internal | daily |
| `avg_invigilation_load` | Avg. total slots or sections per staff member | Redistribute if avg > threshold | admin / staff | internal | daily |
| `overloaded_staff_count` | Staff carrying > threshold load | Reassign 1+ invigilation blocks | admin / staff | internal | daily |
| `supervision_fill_rate` | % of sections with a confirmed supervisor | Assign remaining supervisors | admin / staff | internal | daily |
| `workload_combined_duty_count` | Combined invigilation and paper-distribution burden across the visible population | Open workload duty analytics and rebalance concentrated duty load | admin / staff | internal | daily |
| `workload_imbalance_score` | Fairness risk score from workload duty analytics | Review `/workload-duty-analytics` and redistribute overloaded duties | admin / staff | internal | daily |
| `workload_time_slot_peak` | Highest duty concentration by schedule window | Shift or redistribute duties around the busiest time slot | admin / staff | internal | daily |

#### Group 5 — Room / Capacity

| Metric | Why It Matters | Recommended Action | Owner | PDPA | Freq |
|--------|---------------|--------------------|-------|------|------|
| `room_utilization_score` | Avg % of room time filled by scheduled sections | Reassign underutilized sections to fill gaps | admin | internal | daily |
| `underutilized_rooms` | Rooms with < threshold occupancy in the exam window | Reassign or consider reducing room allocation | admin | internal | daily |
| `overcapacity_rooms` | Sections booked beyond room capacity | Move to a larger room or split sections | admin | internal | per optimize run |
| `room_conflict_rate` | % of sections involved in a room-level clash | Fix room - replan — re-optimize | admin | internal | per run |

#### Group 6 — Teacher Submission

| Metric | Why It Matters | Recommended Action | Owner | PDPA | Freq |
|--------|---------------|--------------------|-------|------|------|
| `submission_rate` | % of sections with submitted exam materials | Send reminder for outstanding submissions | admin / teacher | public | daily |
| `not_submitted_count` | Sections still awaiting materials | Notify remaining teachers | admin / teacher | public | daily |
| `avg_review_time_hours` | Mean hours from submission to approval action | Accelerate review when approaching deadline | admin | internal | daily |
| `rejection_rate` | % of submissions rejected at first review | Investigate whether submission guidelines are clear | admin | internal | weekly |

#### Group 7 — Print / Export

| Metric | Why It Matters | Recommended Action | Owner | PDPA | Freq |
|--------|---------------|--------------------|-------|------|------|
| `print_queue_size` | Total entries in print queue — physically printed for students | Dispatch remaining batches | admin / print_shop | internal | hourly |
| `ready_to_print` | Exam PDFs that passed print review and are queued | Verify paper stock before running print | print_shop / admin | internal | hourly |
| `awaiting_pickup` | Printed paper not yet collected | Contact departments, escalate aged pickups | admin / staff | public | daily |
| `export_failure_count` | Export jobs that errored out in last 24 h | Check storage space, investigate error log | admin / IT | internal | hourly |

#### Group 8 — QR / Pickup

| Metric | Why It Matters | Recommended Action | Owner | PDPA | Freq |
|--------|---------------|--------------------|-------|------|------|
| `pickup_rate` | % of exam papers collected via QR vs total printed | Investigate low rates — QR scanner or distribution chain problem | print_shop / staff | internal | daily |
| `qr_redeems_24h` | Number of paper copies collected via QR scan today | Confirm physical stock matches digital records | print_shop | internal | hourly |
| `pickup_failure_count` | QR scans that returned errors | Check scanner configuration, review logs | IT / print_shop | internal | hourly |
| `collection_backlog count` | Printed but not yet collected items | Contact departments; escalate with SLA | admin / staff | internal | daily |

#### Group 9 — PDPA / Security

| Metric | Why It Matters | Recommended Action | Owner | PDPA | Freq |
|--------|---------------|--------------------|-------|------|------|
| `pdpa_alert_count` | Number of PDPA-sensitive events detected | Investigate each alert; escalate to DPO if unresolved | admin / DPO | internal | real-time |
| `restricted_export_count` | Exports containing fields marked `restricted` | Cancel export if padding_fill excepted — review | admin | restricted | real-time |
| `audit_gap_count` | Sealing gaps in the immutable audit trail | Patch gaps within 24 h; assign owner per gap | admin / DPO | confidential | daily |
| `dev_access_override_count` | Dev key used in non-dev environment | Rotate key, investigate anomaly | admin | restricted | real-time |
| `audit_log_integrity_score` | Format / skip check score of audit batch | Re-seal any incomplete batches | admin / DPO | internal | daily |

#### Group 10 — System / Operations

| Metric | Why It Matters | Recommended Action | Owner | PDPA | Freq |
|--------|---------------|--------------------|-------|------|------|
| `api_uptime_pct_24h` | % of health checks passing in last 24 h | Escalate to IT if below 99% | IT | public | hourly |
| `db_connection_ok` | DB connectivity status | Restart DB container; check migration lock | IT | public | 5 min |
| `storage_usage_pct` | Disk consumption across volumes | Safe to delete uploaded PDFs or prune old logs | IT | public | hourly |
| `scheduler_heartbeat_age_min` | Min idle between scheduler events | Investigate if > 15 min gap; check worker logs | IT | public | 5 min |
| `worker_pending_count` | Messages or jobs waiting for a background worker | Restart or add workers | IT | public | 5 min |
| `config_validation_health_pct` | % of platform config checks that pass | Review failed configuration validations | admin | internal | daily |

---

### 2 · Staff

**Key Questions**
- What examinations are invigilations or distribution slots assigned to me today?
- What upcoming operational blocks are in the schedule?
- Do any sections need urgent coverage?

| Metric | Why It Matters | Recommended Action | PDPA | Freq |
|--------|---------------|--------------------|------|------|
| `active_invigilations` | Number of sections I am assigned to supervise today | Arrive on time; confirm attendance via check-in | public | real-time / on-event |
| `upcoming_blocks_count` | Invigilation blocks starting within next 24 h | Prepare materials / check room assignment | internal | hourly |
| `my_supervision_count` | Active supervision records I hold covering this period | Confirm all records are current and accurate | public | daily |
| `my_distribution_slots` | Print distribution tasks I am assigned to | Prepare packages; scan QR on handover | public | on-event |
| `swap_requests_pending_my_action` | Swap requests awaiting my approval or rejection | Approve or reject within allowed window | internal | per-event |
| `room_keeper_duties` | Room open/close duty slots assigned today | Unlock / lock rooms at scheduled times | public | real-time |
| `my_combined_duty_count` | Combined invigilation and distribution duty load for my visible route | Open `/duty-workload` to confirm whether the current burden needs redistribution | internal | daily |
| `my_time_slot_load` | Which time slot carries my heaviest duty concentration | Prepare materials early for the busiest operational block | internal | daily |

**PDPA Rules:** no student names, no teacher names, no exam paper contents.

---

### 3 · Teacher

**Key Questions**
- When and where are my upcoming exams?
- Have I submitted exam materials for each section?
- What is the current review status of my submission?

| Metric | Why It Matters | Recommended Action | PDPA | Freq |
|--------|---------------|--------------------|------|------|
| `my_exam_count` | Sections assigned to me this period | Review schedule for conflicts | public | daily |
| `submission_status` | Submission state per section | Submit / resubmit materials before deadline | public | per-event |
| `upcoming_exam_dates` | Next exam date(s) per section | Prepare materials accordingly | public | daily |
| `submission_rejection_reason` | If rejected — why | Fix and resubmit before deadline | public | per-event |
| `room_assignment` | Room for each upcoming exam | Confirm room and address is correct | public | daily |
| `days_to_next_submission_deadline` | Days until submission lock | Submit early if deadline is imminent | public | daily |
| `my_combined_duty_count` | Combined invigilation and paper-distribution burden for the current teacher | Review `/my-workload` and request redistribution if the burden becomes unreasonable | internal | daily |
| `my_workload_imbalance_context` | Whether my duty load appears above or below the visible fairness baseline | Use workload analytics during staffing discussions with admin or supervisor | internal | daily |

**PDPA Rules:** own courses / sections only. No other teacher names. No student PII.

---

### 4 · Student

**Key Questions**
- When and where is my next exam?
- Is my exam schedule complete?

| Metric | Why It Matters | Recommended Action | PDPA | Freq |
|--------|---------------|--------------------|------|------|
| `up_next_count` | Number of exams in the next 7 days | Check dates and room list | public | daily |
| `next_exam_date` | Date of the nearest upcoming exam for this timetable | Mark calendar, print QR | public | daily |
| `exam_count_this_period` | Total exams in this academic period | None — informational | public | semesterly |
| `schedule_completeness_pct` | % of exam placements resolved for this timetable | View complete schedule; nothing required | public | daily |

**PDPA Rules:** own schedule only — no cross-student data. Count-based only unless drill-down to personal timetable.

---

### 5 · Print Shop

**Key Questions**
- How many batches are in the print queue?
- Which batches are ready to dispatch?
- How many are awaiting student pickup?

| Metric | Why It Matters | Recommended Action | PDPA | Freq |
|--------|---------------|--------------------|------|------|
| `queue_size` | Total items in the print queue | Process batches by priority | internal | hourly |
| `ready_to_print_count` | PDF batches cleared for print | Start print run | internal | hourly |
| `awaiting_pickup_count` | Ready but not yet collected | Report back at cut-off | public | daily |
| `printing_in_progress_count` | Batches currently being printed | Monitor for stuck jobs | internal | 30 min |
| `pickup_failure_count` | QR scan errors today | Inspect scanner and re-scan | internal | hourly |

**PDPA Rules:** no student personal data. No teacher names.

---

### 6 · Department Supervisor

**Key Questions**
- Is every section in my department scheduled?
- Are all teachers in my department submitting on time?
- Are any staff in my department overloaded?

| Metric | Why It Matters | Recommended Action | PDPA | Freq |
|--------|---------------|--------------------|------|------|
| `dept_unscheduled_count` | Sections in my dept without a room/date | Assign dates and escalate | admin for schedule update | internal | daily |
| `dept_submission_rate_pct` | % of sections in my dept that submitted materials | Email non-submitters | internal | daily |
| `dept_submitted_not_published_count` | Submissions ready but not yet published | Escalate publication if past deadline | internal | daily |
| `dept_overloaded_staff_count` | Staff in my dept over the load threshold | Talk to admin about redistribution | internal | weekly |
| `dept_conflict_count` | Scheduling conflicts only within my dept | Fix room/time assignment for conflicting sections | internal | per run |
| `dept_supervision_fill_rate` | % of my dept sections with a confirmed supervisor | Assign missing supervisors | internal | daily |
| `dept_combined_duty_count` | Combined invigilation and distribution burden across the visible department workload view | Use `/duty-workload` to inspect and rebalance department duty pressure | internal | daily |
| `dept_workload_imbalance_score` | Fairness score for the visible department-scoped duty distribution | Escalate high imbalance to admin for redistribution | internal | weekly |

**PDPA Rules:** own department data only. No cross-dept student or teacher PII.

---

### 7 · ESQ Head / Secretary

**Key Questions**
- What approvals are awaiting my signature?
- What publications are blocked by governance gates?
- Are any rollbacks or escalations pending action?

| Metric | Why It Matters | Recommended Action | PDPA | Freq |
|--------|---------------|--------------------|------|------|
| `pending_my_approval_count` | Workflow rounds needing my signature today | Review and sign / reserve next slot | internal | hourly |
| `escalation_awaiting_resolution` | Escalated items waiting for resolution | Act on escalation queue | internal | per-event |
| `publication_blockers_count` | Publications that cannot go live due to governance | Confirm governance gate resolution | internal | hourly |
| `rollback_events_recent` | Schedule rollbacks in last period | Confirm intention; re-publish if authorised | internal | daily |
| `workflow_progress_pct` | % of sections that have reached the final signature round | Push uncompleted sections through the pipeline | internal | daily |
| `override_count_period` | Total override log entries this period | Audit each entry; confirm intentional overrides | restricted | weekly |

**PDPA Rules:** read-only for files — no editor access to student exam papers. All override entries retained on restricted export list.

---

### 8 · IT / System Admin

**Key Questions**
- Are APIs responding within SLA?
- Is the database connected and migrations up to date?
- Is there enough disk space?
- Are background workers running?

| Metric | Why It Matters | Recommended Action | PDPA | Freq |
|--------|---------------|--------------------|------|------|
| `api_uptime_pct_24h` | % of health checks passing in last 24 h | Escalate to admin if < 99% | public | hourly |
| `db_connection_ok` | DB connectivity status | Restart DB container or cancel paused migration | public | 5 min |
| `storage_usage_pct_all_volumes` | Disk consumption across DB, uploads, exports, logs | Prune old retention back-ups before hitting 100% | public | hourly |
| `scheduler_heartbeat_age_min` | Minutes elapsed since last scheduler event | Restart worker if stale > 15 min | public | 5 min |
| `worker_pending_count_all_queues` | Jobs waiting across all background queues | Add worker or drain specific stale queue | public | 5 min |
| `config_validation_health_pct` | % of platform config checks passing | Review failed configuration checks | internal | daily |
| `migration_pending_count` | Unapplied migration files | Run migration against staging first | internal | daily |
| `last_backup_timestamp` | Age in hours since last successful backup | Trigger backup if > 24+ h elapsed | internal | hourly |

**PDPA Rules:** system health only. No academic-sensitive data, no student names, no exam paper content.

---

### 9 · DPO / PDPA Reviewer

**Key Questions**
- How many PDPA-sensitive events have occurred this period?
- Are there any unsealed audit gaps?
- How many restricted exports have been issued?

| Metric | Why It Matters | Recommended Action | PDPA | Freq |
|--------|---------------|--------------------|------|------|
| `pdpa_alert_count_7d` | Total PDPA alerts detected in the past week | Investigate each; ensure resolution confirmed by admin | internal | daily |
| `audit_gap_count` | Unsealed gaps in the immutable audit log | Assign patching owner; ensure R-00 logs follow maths | restricted | daily |
| `restricted_export_count_7d` | Exports that included restricted-level fields this week | Confirm each export was intentional and authorised | restricted | weekly |
| `export_events_restricted_by_role` | Which roles and what role made restricted exports | Review administrator roles | confidential | weekly |
| `retention_compliance_score` | % of records retained in line with the retention policy | Escalate any overdue records | internal | monthly |
| `import_pii_loaded_count_7d` | PII fields loaded from bulk-import last week | Run PII access audit for all records | confidential | weekly |

**PDPA Rules:** aggregates only. Raw PII never surfaced. Every metric should display count without identifiers.

---

### 10 · Executive / Dean

**Key Questions**
- What is the overall health of the exam cycle?
- What are the top 3 risks right now?
- Is the schedule on track to publish by the deadline?

| Metric | Why It Matters | Recommended Action | PDPA | Freq |
|--------|---------------|--------------------|------|------|
| `overall_health_score` | Composite 0–100 health index (already in executive_dashboard_projection_service) | View detailed breakdown if band is amber or red | public | daily |
| `risk_band` | Green / Amber / Red — colour-coded summary | Attend ops huddle if amber; invoke runbook if red | public | daily |
| `unresolved_blockers_count` | Sections blocked by governance gates | Confirm escalation to managing admin | internal | daily |
| `publication_readiness_score` | % of sections publication-ready | Identify infra and governance gaps to resolve now | internal | daily |
| `submission_completeness_pct` | % of sections that have submitt materials | Review: deadline may be unreachable | public | daily |
| `pdpa_exposure_count_this_period` | Total PDPA events this exam period | Note for audit; confirm no escalation pending | internal | daily |
| `optimization_quality_trend` | Quality trend vs. previous period | Investigate if trending down | public | weekly |
| `top_risks_summary` | Text summary of the most impactful risks this period | Assign action owners; schedule follow-up review | public | weekly |
| `next_milestone_date` | Next key deadline (e.g. print, signature, publish) | Confirm preparation is on track | public | weekly |
| `workload_imbalance_score` | Aggregate duty fairness risk across invigilation and paper distribution | Review workload analytics before staffing stress becomes a publication blocker | internal | daily |
| `combined_duty_load_trend` | Overall operational duty accumulation over the exam period | Ask admin to review peak periods and rebalance overloaded windows | internal | weekly |

**PDPA Rules:** aggregate health scores only. No individual staff, teacher, or student identifiers.

---

## Role → PDPA Clearance

| Role | Clearance | Notes |
|------|-----------|-------|
| admin | all | Unrestricted in system |
| esq_head | public + internal + confidential | Restricted exports require double-approval |
| secretary | public + internal + confidential | Same as esq_head |
| staff | public + internal | No confidential or restricted metrics |
| teacher | public + internal | Restricted to own sections |
| dept_supervisor | public + internal | Restricted to own department |
| print_shop | public + internal | No student/teacher PII |
| student | public | Own schedule only; aggregate counts |
| it | public + internal | No academic data or PII |
| dpo | all | All data available for compliance audit |
| executive | public + internal + confidential | No raw PII — aggregated scores and counts only |

---

## Metric Group → Data Source

| Group | Primary Data Source | Fallback Source |
|-------|--------------------|-----------------|
| examOperations | `dashboard_service.get_dashboard_stats()` | `schedule_query_service` |
| optimizationQuality | `executive_dashboard_projection_service` + `optimization_quality_service` | `optimization_trace_service` (partial) |
| governanceApproval | `governance_analytics_service.compute_governance_analytics()` | `workflow_reporting_service` |
| staffWorkload | `GET /api/dashboard/workload-duty-analytics` via `workload_duty_analytics_service` | `workload_analytics_service` + `supervision` table counts |
| roomCapacity | `room_utilization_analytics_service` | `schedule_query_service` + room queries |
| teacherSubmission | `dashboard_service.get_analytics()` | `submission_service` |
| printExport | `export_service` / `export_excel_service` | `ExamSchedule.print_duplex` flags |
| qrPickup | `exam_pickup` service | `checkin_event` scan count |
| pdpaSecurity | `pdpa_runtime_guard_service` | `audit_service` + `immutable_audit_service` |
| systemOperations | `health_service` | raw `db.execute()` health probes |

---

## Common Severity Thresholds

Used by `DashboardMetricService.classify_metric_severity()`:

| Metric Pattern | Critical | Warning | Info | Good |
|----------------|----------|---------|------|------|
| Missing items / count | ≥ 50 | ≥ 10 | ≥ 1 | 0 |
| Rate / percentage | ≥ 20% | ≥ 10% | ≥ 1% | 0% |
| Score 0-100 (inverted) | ≤ 30 | ≤ 50 | ≤ 70 | 100 |
| Score 0-100 (direct) | ≥ 80 | ≥ 60 | ≥ 40 | 0-40 |
| Age / delay (minutes) | ≥ 120 | ≥ 60 | ≥ 15 | < 15 |

---

## Common Trend Mappings

| Condition | Trend |
|-----------|-------|
| Value vs. last_period period / change > +5% (cost/risk metric is deterioration) | `up` |
| Value vs. last_period / change < -5% (cost/risk metric is improvement) | `down` |
| Change within ±5% | `flat` |
| No prior period data | `unknown` |
| Value refresh on-event (e.g. new submission) | `unknown` |
