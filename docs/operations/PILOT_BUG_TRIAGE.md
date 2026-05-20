# Pilot Bug Triage System

## Overview
This document establishes a structured classification and tracking system for bugs and issues discovered during the controlled pilot phase of EMS.

## Severity Levels

### CRITICAL
**Definition**: System unusable, data loss/corruption, security incident, complete workflow failure affecting multiple users.

**Examples**:
- Dashboard crashes on load for all users
- Optimization produces invalid schedules that violate hard constraints
- PDPA data leakage in any dashboard response
- Database corruption or data loss
- Authentication failure for all roles

**Response Time**: Immediate (within 15 minutes during business hours)
**Escalation**: On-call engineer + platform lead
**Rollback Decision**: Automatic consideration if not resolved in 30 minutes

---

### HIGH
**Definition**: Major workflow broken, significant user impact, incorrect critical metrics, repeated failures.

**Examples**:
- Workload Duty Analytics shows incorrect counts for >50% of users
- Governance approval workflow stuck (cannot approve/reject)
- Export produces corrupted or incomplete files
- Teacher dashboard shows other teachers' data (visibility leak)
- Optimization quality score calculation produces NaN or negative values

**Response Time**: Within 1 hour
**Escalation**: Platform lead
**Rollback Decision**: Consider if not resolved in 2 hours

---

### MEDIUM
**Definition**: Noticeable friction, incorrect non-critical metrics, confusing UX, minor performance degradation.

**Examples**:
- Imbalance score threshold generates false overload alerts
- Dashboard metric descriptions unclear or misleading
- Filter dropdowns slow to populate (2-5 seconds)
- Missing tooltip explanations for fairness metrics
- Thai labels overflow in metric cards on mobile

**Response Time**: Within 4 hours
**Escalation**: Development team
**Rollback Decision**: Rarely required; schedule fix in next iteration

---

### LOW
**Definition**: Cosmetic issues, minor text problems, edge-case behaviors, documentation gaps.

**Examples**:
- Typo in metric description
- Inconsistent date formatting across pages
- Raw string scanner noise (pre-existing)
- Missing i18n key for obscure error message
- Chart legend text slightly clipped on very small viewports

**Response Time**: Next business day
**Escalation**: None required
**Rollback Decision**: Not applicable

---

## Reproducibility Tracking

### Status Values
- **Reproducible**: Issue can be consistently reproduced with documented steps
- **Intermittent**: Issue occurs sporadically, not consistently reproducible
- **Environment-Specific**: Issue only occurs in specific browser/OS/device combination
- **Data-Dependent**: Issue only occurs with specific data patterns or volumes
- **One-Time**: Issue observed once, not reproducible since

### Required Fields for Reproducibility
- Browser / OS / Device
- User role
- Specific page / endpoint
- Steps to reproduce (numbered list)
- Expected behavior
- Actual behavior
- Screenshots / screen recordings (if applicable)
- Console errors / network errors (if applicable)

---

## Affected Roles

Track which roles are impacted:

| Role | Critical | High | Medium | Low |
|------|----------|------|--------|-----|
| Admin | | | | |
| Staff | | | | |
| Dept Supervisor | | | | |
| Esq Head / Secretary | | | | |
| Teacher | | | | |
| Student | | | | |
| DPO | | | | |
| IT | | | | |

---

## Affected Modules

### Backend Modules
- `dashboard_intelligence.py` (OPS-DASH endpoints)
- `workload_duty_analytics_service.py`
- `admin_dashboard_intelligence_service.py`
- `role_dashboard_service.py`
- `dashboard_metric_service.py`
- `executive_dashboard_projection_service.py`
- `governance_analytics_service.py`
- `optimization_quality_service.py`
- `health_service.py`
- `pdpa_runtime_guard_service.py`

### Frontend Modules
- `AdminIntelligenceDashboard.tsx`
- `RoleDashboard.tsx`
- `WorkloadDutyAnalytics.tsx`
- `ExecutiveAnalytics.tsx`
- `GovernanceCockpit.tsx`
- `dashboardMetricPresenter.ts`
- `workloadDashboardPresenter.ts`
- `useAdminIntelligenceDashboard.ts`
- `useRoleDashboard.ts`
- `useWorkloadDutyAnalytics.ts`

### Infrastructure
- Database queries / performance
- API response times
- Frontend bundle loading
- i18n translation keys
- Responsive layout / CSS

---

## Workaround Tracking

For each bug, document:

### Immediate Workaround
- Description of workaround
- Steps for users to follow
- Effectiveness (complete / partial / none)
- User impact of workaround

### Permanent Fix
- Root cause analysis
- Proposed solution
- Estimated effort
- Target release / iteration

### Verification
- Test case added?
- Regression test added?
- Pilot user confirmation received?

---

## Bug Report Template

```markdown
## Bug Report #[ID]

**Title**: [Concise description]

**Severity**: CRITICAL | HIGH | MEDIUM | LOW

**Status**: Open | In Progress | Fixed | Verified | Closed

**Reported By**: [Role] - [Name/User ID]

**Date Reported**: [YYYY-MM-DD HH:MM]

**Affected Roles**: [List roles]

**Affected Modules**: [List modules]

**Reproducibility**: Reproducible | Intermittent | Environment-Specific | Data-Dependent | One-Time

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Behavior**:
[Description]

**Actual Behavior**:
[Description]

**Screenshots / Recordings**:
[Links or attachments]

**Console / Network Errors**:
[Error messages or logs]

**Workaround**:
[Description or "None available"]

**Root Cause** (if known):
[Analysis]

**Proposed Fix**:
[Solution description]

**Estimated Effort**:
[Hours/Days]

**Target Iteration**:
[Week/Phase]

**Verification**:
- [ ] Test case added
- [ ] Regression test added
- [ ] Pilot user confirmation received
- [ ] Deployed to staging
- [ ] Deployed to production
```

---

## Triage Process

### Daily Triage (During Pilot)
1. Review new bug reports from previous 24 hours
2. Classify severity and reproducibility
3. Assign to appropriate team member
4. Update workaround status for open issues
5. Escalate CRITICAL/HIGH issues to platform lead

### Weekly Review
1. Review all open bugs by severity
2. Identify patterns or systemic issues
3. Prioritize fixes for next iteration
4. Update pilot users on status of HIGH/CRITICAL issues
5. Document lessons learned

### Post-Pilot Retrospective
1. Analyze bug distribution by severity, module, role
2. Identify most impactful fixes
3. Recommend process improvements
4. Update triage system for future phases

---

## Escalation Matrix

| Severity | First Response | Escalation | Decision Authority |
|----------|----------------|------------|-------------------|
| CRITICAL | On-call engineer (15 min) | Platform lead (30 min) | Technical lead + Operations manager |
| HIGH | Development lead (1 hour) | Platform lead (2 hours) | Platform lead |
| MEDIUM | Assigned developer (4 hours) | Development lead (next day) | Development lead |
| LOW | Assigned developer (next day) | None | Developer discretion |

---

## Metrics to Track

### Volume Metrics
- Total bugs reported
- Bugs by severity (CRITICAL/HIGH/MEDIUM/LOW)
- Bugs by module
- Bugs by affected role
- Open vs closed bugs

### Response Metrics
- Average time to first response
- Average time to resolution
- Percentage of bugs with workarounds
- Percentage of bugs resolved before next iteration

### Quality Metrics
- Percentage of reproducible bugs
- Percentage of bugs with test cases added
- Recurrence rate (bugs that reappear after fix)
- User satisfaction with bug resolution

---

## Pilot-Specific Considerations

### Data Sensitivity
- All bug reports involving PDPA or sensitive data must be marked CONFIDENTIAL
- Screenshots containing PII must be redacted before storage
- Bug reports involving optimization internals may be RESTRICTED

### User Communication
- CRITICAL/HIGH bugs: Notify all affected pilot users within 1 hour
- MEDIUM bugs: Summarize in weekly pilot update
- LOW bugs: Include in iteration notes

### Documentation
- All CRITICAL/HIGH bugs must have root cause analysis documented
- All bugs affecting governance or PDPA must have compliance review
- All workarounds must be communicated to affected users

---

*Document version: 1.0*
*Created: 2026-05-20*
*Owner: Platform Operations Team*
*Review Cycle: Weekly during pilot*