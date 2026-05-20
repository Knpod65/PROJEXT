# Rollback Validation Checklist

## Purpose
This checklist validates that the EMS platform can be safely rolled back in case of critical issues during pilot deployment.

## Rollback Decision Criteria

### Automatic Rollback Triggers
- [ ] Error rate > 5% sustained for 10+ minutes
- [ ] API response time p95 > 5 seconds sustained for 15+ minutes
- [ ] Database connection failures > 10% of requests
- [ ] Critical security vulnerability discovered in production
- [ ] Data corruption detected in audit logs
- [ ] PDPA compliance violation detected

### Manual Rollback Triggers
- [ ] User-reported critical functionality broken
- [ ] Dashboard metrics showing obviously incorrect data
- [ ] Governance workflow stuck (no approvals possible)
- [ ] Optimization producing invalid schedules
- [ ] Export functionality producing corrupted files

---

## Rollback Procedures

### Procedure 1: Hot Rollback (Zero-Downtime)

**When to Use:**
- Minor configuration issues
- Non-critical feature regression
- Quick fix available

**Steps:**
1. Identify the specific component to roll back (frontend, backend, database migration)
2. Deploy previous stable version via CI/CD pipeline
3. Verify health checks pass on new deployment
4. Monitor error rate for 15 minutes
5. Confirm with pilot users that issue is resolved
6. Document rollback reason and resolution

**Estimated Time:** 5-15 minutes

---

### Procedure 2: Warm Restart

**When to Use:**
- Application-level bug requiring full restart
- Memory leak or performance degradation
- Service dependency failure

**Steps:**
1. Notify pilot users of planned maintenance (if possible)
2. Stop application gracefully (SIGTERM)
3. Verify all connections closed
4. Deploy previous stable version
5. Start application
6. Verify health checks pass
7. Run smoke tests on critical paths
8. Monitor for 30 minutes
9. Resume normal operations

**Estimated Time:** 15-30 minutes

---

### Procedure 3: Cold Restart from Backup

**When to Use:**
- Database corruption detected
- Data integrity issue affecting multiple users
- Security breach requiring full restore

**Steps:**
1. **STOP ALL WRITES IMMEDIATELY**
   - Put application in maintenance mode
   - Disable all export/optimization endpoints
   - Notify all users

2. **Identify Point-in-Time for Restore**
   - Determine last known good state
   - Note all transactions since that point
   - Document affected users/records

3. **Restore Database**
   - Restore from backup to staging first (verify)
   - Apply to production only after staging verification
   - Verify data integrity post-restore

4. **Deploy Application**
   - Deploy previous stable version
   - Verify all health checks
   - Run data reconciliation scripts

5. **Reconcile In-Flight Transactions**
   - Review audit logs for transactions since restore point
   - Manually reconcile or re-apply if safe
   - Document all reconciliations

6. **Resume Operations**
   - Notify users of restored service
   - Monitor error rate for 1 hour
   - Provide support for affected users

**Estimated Time:** 2-6 hours (depending on data volume)

---

## Rollback Validation Tests

### Pre-Rollback Validation (Staging)

**Test 1: Application Startup**
- [ ] Previous version starts without errors
- [ ] Database connection established
- [ ] Health checks pass
- [ ] No startup warnings

**Test 2: Critical User Flows**
- [ ] User login works
- [ ] Dashboard loads correctly
- [ ] Schedule view accessible
- [ ] Export functionality works
- [ ] Optimization trigger works (if applicable)

**Test 3: Data Integrity**
- [ ] No data loss after rollback
- [ ] Audit logs intact
- [ ] User data consistent
- [ ] No orphaned records

**Test 4: Performance**
- [ ] Response times within baseline
- [ ] No memory leaks
- [ ] Database queries optimized

---

### Post-Rollback Validation (Production)

**Immediate Checks (First 5 Minutes)**
- [ ] Health check endpoints returning 200
- [ ] No critical errors in logs
- [ ] Login page accessible
- [ ] Dashboard loads for test user

**Short-Term Checks (First 30 Minutes)**
- [ ] Error rate < 1%
- [ ] p95 response time < 2 seconds
- [ ] All critical user flows functional
- [ ] No data corruption reports

**Medium-Term Checks (First 2 Hours)**
- [ ] Pilot users confirm resolution
- [ ] No new issues reported
- [ ] Monitoring dashboards stable
- [ ] Backup jobs running normally

---

## Communication Templates

### Template 1: Planned Maintenance Notification

```
Subject: [MAINTENANCE] EMS Platform Brief Downtime - [DATE/TIME]

Dear Pilot Users,

We will be performing a brief maintenance on the EMS platform at [TIME] to address [ISSUE DESCRIPTION].

Expected Duration: [X] minutes
Impact: [Dashboard access / Optimization / Exports / All services]

We apologize for any inconvenience and appreciate your patience as we work to improve platform stability.

Best regards,
Platform Operations Team
```

### Template 2: Rollback Notification

```
Subject: [UPDATE] EMS Platform Issue - Rollback in Progress

Dear Pilot Users,

We are currently experiencing [ISSUE DESCRIPTION] on the EMS platform. As a precautionary measure, we are rolling back to the previous stable version.

Current Status: Rollback in progress
Estimated Resolution: [X] minutes
Workaround: [If applicable]

We will provide another update within [X] minutes.

Thank you for your understanding.

Best regards,
Platform Operations Team
```

### Template 3: Resolution Confirmation

```
Subject: [RESOLVED] EMS Platform Issue - Service Restored

Dear Pilot Users,

The issue with [ISSUE DESCRIPTION] has been resolved. We have rolled back to the previous stable version and verified that all critical functionality is working correctly.

What was fixed: [Brief description]
Current status: All services operational
Next steps: [If applicable - investigation, permanent fix timeline]

Thank you for your patience and for participating in the pilot program. Your feedback is invaluable.

Best regards,
Platform Operations Team
```

---

## Rollback Decision Tree

```
START
  │
  ▼
Is issue critical? (data loss, security breach, complete outage)
  │
  ├── YES ──► Execute Cold Restart from Backup
  │            │
  │            ▼
  │         Validate data integrity
  │            │
  │            ▼
  │         Resume operations
  │
  └── NO ──► Is quick fix available?
               │
               ├── YES ──► Deploy hotfix (no rollback needed)
               │
               └── NO ──► Execute Hot Rollback or Warm Restart
                            │
                            ▼
                         Validate resolution
                            │
                            ▼
                         Resume operations
```

---

## Post-Rollback Actions

### Immediate (Within 1 Hour)
- [ ] Document rollback reason and timeline
- [ ] Capture relevant logs and metrics
- [ ] Notify all stakeholders
- [ ] Schedule post-incident review

### Short-Term (Within 24 Hours)
- [ ] Conduct post-incident review meeting
- [ ] Identify root cause
- [ ] Develop permanent fix plan
- [ ] Update runbooks if necessary

### Long-Term (Within 1 Week)
- [ ] Implement permanent fix
- [ ] Update deployment procedures
- [ ] Improve monitoring/alerting if gaps identified
- [ ] Share lessons learned with team

---

## Rollback Success Criteria

A rollback is considered successful when:
- [ ] All critical user flows functional
- [ ] Error rate < 1%
- [ ] No data loss or corruption
- [ ] Pilot users confirm resolution
- [ ] Monitoring stable for 2+ hours
- [ ] No new issues introduced

If rollback does not meet success criteria:
- Escalate to on-call engineer
- Consider cold restart from backup
- Engage development team for emergency fix

---
*Document version: 1.0*
*Last updated: 2026-05-20*
*Owner: Platform Operations Team*