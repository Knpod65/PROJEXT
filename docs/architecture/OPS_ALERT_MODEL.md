# OPS Alert Model

## Overview

The operational alert foundation provides lightweight, dashboard-renderable alerts for critical operational conditions without requiring full async notification infrastructure (email/SMS/LINE).

## Alert Types

### 1. Missing Rooms Alert
**Alert Code**: `missing_rooms`

**Trigger Condition**:
- `unscheduled_sections > 10`

**Severity**: warning

**Related Metrics**:
- `unscheduled_sections`

**Recommended Action**:
- Review schedule and assign rooms/dates to unassigned sections

**Owner Role**: admin, dept_supervisor

---

### 2. Missing Invigilators Alert
**Alert Code**: `missing_invigilators`

**Trigger Condition**:
- `missing_invigilators > 5`

**Severity**: warning

**Related Metrics**:
- `missing_invigilators`

**Recommended Action**:
- Review supervision coverage and reassign invigilators

**Owner Role**: admin, staff

---

### 3. Publication Blocked Alert
**Alert Code**: `blocked_publication`

**Trigger Condition**:
- `blocker_count > 0`

**Severity**: critical

**Related Metrics**:
- `blocker_count`
- `pending_approvals`

**Recommended Action**:
- Review governance blockers and resolve conflicts

**Owner Role**: admin, esq_head, secretary

---

### 4. Optimization Hard Fail Alert
**Alert Code**: `optimization_hard_fail`

**Trigger Condition**:
- `optimization_quality_avg < 40.0`

**Severity**: critical

**Related Metrics**:
- `optimization_quality_avg`

**Recommended Action**:
- Re-run optimization cycle or review constraint violations

**Owner Role**: admin

---

### 5. PDPA Suspicious Activity Alert
**Alert Code**: `pdpa_suspicious_activity`

**Trigger Condition**:
- `pdpa_alert_count_24h > 5`

**Severity**: critical

**Related Metrics**:
- `pdpa_alert_count_24h`

**Recommended Action**:
- Review PDPA alert log with data protection officer

**Owner Role**: admin, esq_head, secretary, dpo

---

### 6. Print Queue Overload Alert
**Alert Code**: `print_queue_overload`

**Trigger Condition**:
- `print_queue_size > 50`

**Severity**: warning

**Related Metrics**:
- `print_queue_size`

**Recommended Action**:
- Check print queue and prioritize urgent jobs

**Owner Role**: admin, print_shop

---

### 7. Workload Imbalance Alert
**Alert Code**: `workload_imbalance`

**Trigger Condition**:
- `staff_imbalance_score > 0.5`

**Severity**: warning

**Related Metrics**:
- `staff_imbalance_score`

**Recommended Action**:
- Review supervision coverage and redistribute workload

**Owner Role**: admin, staff

---

### 8. Governance Pending Too Long Alert
**Alert Code**: `governance_pending_too_long`

**Trigger Condition**:
- `pending_approvals > 0` for more than 48 hours

**Severity**: warning

**Related Metrics**:
- `pending_approvals`

**Recommended Action**:
- Escalate pending approvals to appropriate authority

**Owner Role**: admin, esq_head, secretary

---

## Alert Data Model

```python
{
    "alert_code": str,                    # Unique identifier (snake_case)
    "severity": str,                      # "info" | "warning" | "critical"
    "title_i18n_key": str,                # Translation key for alert title
    "body_i18n_key": str,                 # Translation key for alert body
    "metric_codes": list[str],            # Related metric codes for context
    "recommended_action_i18n_key": str,   # Translation key for recommended action
    "timestamp": str,                     # ISO-8601 timestamp
    "owner_role": str | None,             # Primary role responsible (optional)
    "resolution_status": str | None,      # "open" | "acknowledged" | "resolved" (optional)
}
```

---

## Alert Generation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Sources                              │
├─────────────────────────────────────────────────────────────┤
│  • dashboard_stats (exam operations)                        │
│  • governance_analytics (blockers, approvals)               │
│  • workload_analytics (imbalance, overload)                 │
│  • optimization_quality (solver performance)                │
│  • pdpa_alerts (compliance events)                          │
│  • print_queue_size (logistics)                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              DashboardAlertService.generate_*()             │
├─────────────────────────────────────────────────────────────┤
│  • generate_operational_alerts()                            │
│  • generate_governance_pending_alert()                      │
│  • Custom alert generators (future)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Alert List                                │
├─────────────────────────────────────────────────────────────┤
│  [                                                             │
│    {                                                           │
│      "alert_code": "missing_rooms",                           │
│      "severity": "warning",                                   │
│      "title_i18n_key": "dashboard.alerts.missingRooms",       │
│      "metric_codes": ["unscheduled_sections"],                │
│      "recommended_action_i18n_key": "...",                    │
│      "timestamp": "2026-05-20T10:30:00Z"                      │
│    },                                                          │
│    ...                                                         │
│  ]                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Dashboard Rendering                             │
├─────────────────────────────────────────────────────────────┤
│  • AdminIntelligenceDashboard: CriticalAlertsRow            │
│  • RoleDashboard: Role-specific alert sections              │
│  • WorkloadDutyAnalytics: Fairness alert panel              │
│  • Notification badge (future)                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### Admin Intelligence Dashboard
- **Location**: CriticalAlertsRow (first 3 severity=critical metrics)
- **Display**: Red-bordered card above metric groups
- **Interaction**: Click to navigate to related metric or action

### Role Dashboard
- **Location**: Role-specific alert section (if applicable)
- **Display**: Contextual alerts for role's operational scope
- **Example**: Teacher sees invigilator coverage alerts for own exams

### Workload Duty Analytics
- **Location**: Fairness/Risk Panel
- **Display**: Workload imbalance and overload alerts
- **Action**: Links to workload redistribution workflow

---

## Future Enhancements (Deferred)

### Phase 2: Notification Infrastructure
- Email notifications for critical alerts
- SMS alerts for on-call personnel
- LINE notifications for Thai users
- In-app notification center

### Phase 3: Alert Management
- Alert acknowledgment workflow
- Alert resolution tracking
- Alert history and trends
- Custom alert rules and thresholds

### Phase 4: Advanced Alerting
- Machine learning-based anomaly detection
- Predictive alerts (e.g., "workload will exceed threshold in 3 days")
- Cross-dashboard correlation alerts
- Automated remediation suggestions

---

## Alert Severity Guidelines

| Severity | Color | Response Time | Example |
|----------|-------|---------------|---------|
| critical | Red | Immediate (<15 min) | Publication blocked, PDPA violation |
| warning | Amber | Within 1 hour | Missing rooms, queue overload |
| info | Blue | Within 4 hours | System health degraded, minor imbalance |

---

## i18n Keys

All alert titles, bodies, and recommended actions use i18n keys under the `dashboard.alerts.*` and `dashboard.actions.*` namespaces:

```typescript
"dashboard.alerts.missingRooms": "Rooms are not fully assigned for all sections."
"dashboard.alerts.missingInvigilators": "Invigilator coverage is incomplete."
"dashboard.alerts.blockedPublication": "Publication is blocked — review governance blockers."
"dashboard.alerts.pdpaAlert": "PDPA exposure detected — check security log."
"dashboard.alerts.optimizationHardFail": "Optimization quality below acceptable threshold."
"dashboard.alerts.printQueueOverload": "Print queue exceeds capacity threshold."
"dashboard.alerts.workloadImbalance": "Staff workload significantly imbalanced."
"dashboard.alerts.governancePendingTooLong": "Governance approvals pending beyond SLA."

"dashboard.actions.assignMissingRooms": "Assign missing rooms"
"dashboard.actions.reviewSupervisionCoverage": "Review supervision coverage"
"dashboard.actions.reviewGovernanceBlockers": "Review governance blockers"
"dashboard.actions.reviewPDPALog": "Review PDPA alert log"
"dashboard.actions.reviewOptimizerTrace": "Review optimization trace"
"dashboard.actions.checkPrintQueue": "Check print queue"
```

Thai translations provided in `th.ts` under the same keys.

---

*Document version: 1.0*
*Last updated: 2026-05-20*