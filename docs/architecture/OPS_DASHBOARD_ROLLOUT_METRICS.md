# OPS Dashboard Rollout Metrics

> Scope: Workload Duty Analytics metric definitions for role-intelligence rollout

---

## Workload Duty Analytics Metrics

### `workload.totalInvigilationDuties`

- Title: Total Invigilation Duties
- Why it matters: shows the visible exam-supervision burden in the selected workload scope
- Recommended action: rebalance assignments if invigilation concentration is too high
- Intended route / drilldown: `/workload-duty-analytics`, `/duty-workload`, `/my-workload`
- Role audiences: admin, staff, department supervisor, teacher, executive

### `workload.totalDistributionDuties`

- Title: Total Paper Distribution Duties
- Why it matters: captures hidden operational work that is often missed when only supervision is counted
- Recommended action: rotate or redistribute distribution work when it clusters on too few people
- Intended route / drilldown: `/workload-duty-analytics`, `/duty-workload`, `/my-workload`
- Role audiences: admin, staff, department supervisor, teacher, executive

### `workload.combinedDutyCount`

- Title: Combined Duty Count
- Why it matters: fair workload requires invigilation and distribution to be evaluated together
- Recommended action: use combined duty load as the primary rebalance signal before publication deadlines
- Intended route / drilldown: `/workload-duty-analytics`, `/duty-workload`, `/my-workload`
- Role audiences: admin, staff, department supervisor, teacher, executive

### `workload.imbalanceScore`

- Title: Workload Imbalance Score
- Why it matters: indicates fairness risk across the visible workload population
- Recommended action: review overloaded and underloaded people and shift assignments when the score rises
- Intended route / drilldown: `/workload-duty-analytics`, `/duty-workload`, `/my-workload`
- Role audiences: admin, staff, department supervisor, teacher, executive

### `workload.timeSlotLoad`

- Title: Time-slot Duty Load
- Why it matters: identifies the busiest operational windows where staffing stress is highest
- Recommended action: review peak slots and redistribute duties away from overloaded windows
- Intended route / drilldown: `/workload-duty-analytics`, `/duty-workload`
- Role audiences: admin, staff, department supervisor, executive

### `workload.dailyCumulativeLoad`

- Title: Daily Cumulative Load
- Why it matters: shows how workload accumulates across the exam period and highlights heavy days
- Recommended action: review daily buildup early and rebalance before peak days lock in
- Intended route / drilldown: `/workload-duty-analytics`, `/duty-workload`
- Role audiences: admin, staff, department supervisor, executive

---

## Rollout Notes

- These metrics rely on `GET /api/dashboard/workload-duty-analytics`.
- The workload analytics view preserves route-guarded role access and does not alter existing auth behavior.
- Teacher rollout remains self-scoped by default.
- Executive and governance usage should stay aggregate-focused and avoid raw PII exposure.
