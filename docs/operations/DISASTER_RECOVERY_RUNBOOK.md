# Disaster Recovery Runbook

**System**: EMS (Exam Management System)
**Last Updated**: 2026-05-22
**Owner**: System Owner + IT + DPO

## 1. Incident Levels

| Level | Description                                      | Example                                      | Response Time Target |
|-------|--------------------------------------------------|----------------------------------------------|----------------------|
| P1    | Complete system down or data loss                | Database corruption, full outage             | Immediate            |
| P2    | Major functionality broken, high user impact     | Workload analytics down, submission blocked  | < 30 minutes         |
| P3    | Partial degradation, limited user impact         | One dashboard slow, minor export failure     | < 2 hours            |
| P4    | Minor issue, workaround exists                   | Cosmetic UI bug, non-critical report error   | Next business day    |

## 2. Trigger Conditions (When to Activate This Runbook)

- Application health endpoint returns non-200 for > 5 minutes
- Database connection failures in logs
- Critical data corruption detected (e.g., missing schedules, duplicate submissions)
- Security incident involving data exposure
- Failed deployment that cannot be quickly rolled back
- Loss of access to primary database or storage

## 3. Immediate Response (First 15 Minutes)

1. **Assess** — Check `/health` and key dashboards.
2. **Notify** — Alert:
   - System Owner
   - IT On-call
   - DPO (if personal data may be affected)
3. **Decide** — Choose path:
   - **Rollback** (preferred if recent deployment caused issue)
   - **Restore from Backup** (if data corruption)
   - **Partial Degradation Mode** (if full restore not immediately possible)

## 4. Rollback Path (Preferred for Recent Deployments)

See `docs/deployment/ROLLBACK_EXECUTION_GUIDE.md`

Trigger conditions:
- Deployment within last 4 hours caused the incident
- Health checks failing after deployment
- User reports critical breakage post-deploy

## 5. Restore from Backup Path

1. Stop application (or put in maintenance mode).
2. Restore database using `BACKUP_AND_RESTORE_RUNBOOK.md`.
3. Restore uploaded files if necessary.
4. Run verification checklist from Backup Runbook.
5. Restart application.
6. Confirm critical workflows (login, dashboard, submissions).

**Estimated Recovery Time Objective (RTO)**: 2–4 hours for full restore (pilot scale)

## 6. Communication Template

**Subject**: [P1/P2] EMS Incident – [Brief Description]

**To**: All Pilot Users + Relevant Stakeholders

**Body**:
```
Dear colleagues,

We are currently experiencing [brief issue description] in the EMS system.

Impact: [who is affected]

We are working on [rollback / restore / mitigation].

Expected resolution: [time estimate]

We will provide updates every [30/60] minutes.

Thank you for your patience.
EMS Team
```

## 7. Decision Owners

| Decision                    | Primary Owner       | Backup Owner     |
|-----------------------------|---------------------|------------------|
| Trigger Disaster Recovery   | System Owner        | IT Lead          |
| Choose Rollback vs Restore  | System Owner + IT   | DPO (if data)    |
| Approve communication       | System Owner        | Communications   |
| Declare incident closed     | System Owner        | —                |

## 8. Recovery Time & Point Objectives (Pilot)

- **RTO** (Recovery Time Objective): 4 hours maximum
- **RPO** (Recovery Point Objective): Last successful daily backup (max 24h data loss)
- **Pilot Scale Assumption**: Single faculty, moderate data volume

## 9. Evidence to Record

For every activation of this runbook, record:
- Incident start time
- Detection method
- Decision (Rollback / Restore / Other)
- Commands executed (with timestamps)
- Verification results
- Time to full recovery
- Post-incident review notes

## 10. Post-Incident Review (PIR)

Must be conducted within 5 business days for P1/P2 incidents.

Agenda:
- Timeline reconstruction
- Root cause
- What worked / what didn’t
- Updates needed to runbooks
- Preventive actions

**Owner**: System Owner

---

**This runbook must be reviewed and updated at least once per semester or after every major incident.**
