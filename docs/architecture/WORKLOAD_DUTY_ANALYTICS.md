# Workload Duty Analytics

> Audience: Admin, operations staff, supervisors, teachers, QA, and architecture reviewers  
> Status: Available on `main` as an EMS OPS-DASH role-intelligence capability

---

## Purpose

Workload Duty Analytics gives EMS a role-aware operational dashboard for exam duty fairness. The dashboard treats both invigilation and paper distribution as real operational workload so the institution can track burden concentration, identify fairness risk, and rebalance work before the exam period becomes operationally unstable.

This matters because:
- invigilation alone does not capture the full exam-operation burden
- paper distribution is operational duty and must be counted alongside supervision
- fairness visibility supports staffing, governance, and audit review
- teacher-facing visibility improves trust in workload allocation

---

## Covered Roles

- `admin`
- `staff`
- `dept_supervisor`
- `esq_head`
- `secretary`
- `teacher`

Additional policy note:
- `student` has no access
- `dpo`, if enabled by policy, should remain aggregate-only

---

## Access Routes

- `/workload-duty-analytics` for `admin`
- `/duty-workload` for `staff`, `dept_supervisor`, `esq_head`, `secretary`
- `/my-workload` for `teacher`

These routes share the same page and API contract while preserving role-specific route guards.

---

## Metrics

The dashboard exposes:

- total invigilation duties
- total paper distribution duties
- combined duty count
- average duties per person
- max duties
- imbalance score
- overloaded people
- underloaded people

Operational interpretation:
- `combined_count` is the primary fairness workload unit
- `imbalance_score` is the main fairness-risk summary
- overloaded and underloaded lists identify fast rebalancing candidates

---

## Charts

- by-person graph
- daily cumulative graph
- time-slot graph

The charts are intentionally simple and chart-ready for pilot operations review.

---

## Filters

Supported filters:

- semester
- academic year
- period
- exam type
- role group
- person
- duty type

Default behavior:
- blank semester, year, period, and exam type act as broad filters
- role group defaults by effective role context
- duty type defaults to `all`
- teacher access still resolves to the teacher’s own workload even when broader person filters are attempted

---

## Data Sources

Normalized workload duty records may be assembled from:

- supervision / invigilator assignments
- paper distributor assignments
- QR / pickup records when available
- schedule records
- workload records when available

The backend aggregates these into a single analytics payload for consistent workload comparison.

---

## Normalized Duty Concept

The dashboard operates on a normalized duty concept shaped like:

```json
{
  "person_id": "string",
  "display_name": "string",
  "role_group": "admin | staff | supervisor | teacher",
  "duty_type": "invigilation | paper_distribution",
  "exam_date": "YYYY-MM-DD",
  "time_slot": "HH:MM-HH:MM",
  "course_id": "string",
  "section_no": "string",
  "source": "string"
}
```

This is a documented analytics concept for governance and QA. It does not change the public API contract.

---

## Fairness Logic

- `combined_count = invigilation_count + distribution_count`
- daily cumulative values are running totals ordered by exam date
- time-slot values count duty units inside each schedule window
- `imbalance_score` expresses how unevenly duty is distributed
- risk band communicates that imbalance in an operationally readable form

The dashboard helps answer:
- who is carrying too much operational burden?
- where are the busiest schedule windows?
- how does workload accumulate across the exam period?

---

## PDPA / Governance

- aggregate-safe operational dashboard by design
- teacher view defaults to own workload
- admin can review all workload allowed by policy
- student has no access
- DPO, if enabled, should remain aggregate-only
- no unnecessary raw student PII should appear in the UI
- no unnecessary raw internal identifiers should appear in the visible dashboard

Governance value:
- supports fair workload discussions
- supports staffing escalation before peak periods
- supports auditability of workload-balancing decisions

---

## Known Limitations

- raw data quality depends on assignment completeness
- historical paper distribution data may be incomplete where legacy capture was missing
- normalized role grouping may simplify multi-role users
- duplicate-duty detection should be reviewed in a later pass
- browser/component verification remains manual-doc based in the current pilot phase

---

## Future Enhancements

- export workload fairness report
- person-level schedule drilldown
- fairness simulation
- workload balancing recommendation workflow
- chart performance optimization for very large datasets
- lazy loading for the route chunk
