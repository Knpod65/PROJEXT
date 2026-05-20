# Rollback & Incident Runbook — EMS Exam Management System

> Version: 2026-05-20  
> Target: IT Operations + Development Team  
> Purpose: Incident response and system recovery procedures

---

## Incident Severity Levels

| Severity | Response Time | Rollback Window | Examples |
|----------|---------------|-----------------|----------|
| **S1 - Critical** | 30 min | Immediate | Data loss, security breach, complete outage |
| **S2 - High** | 2 hours | 4 hours | Incorrect data, workflow failure |
| **S3 - Medium** | 1 business day | Scheduled fix | Minor bugs, cosmetic issues |
| **S4 - Low** | 3 business days | N/A | Feature requests, documentation |

---

## S1: Critical Incidents (Immediate Rollback)

### Scenario: Data Loss / Corruption

**Symptoms:**
- Missing student records
- Incorrect schedule data
- Database errors on all queries

**Procedure:**

```bash
# 1. Stop all writes immediately
docker compose stop app

# 2. Identify last good backup
ls -la /data/backups/db/ | head -5

# 3. Restore from backup
TIMESTAMP="20260520_020000"  # Use most recent good backup
gunzip -c /data/backups/db/ems_db_$TIMESTAMP.sql.gz | \
  docker compose exec -T db psql -U ems_admin -d ems_prod

# 4. Restore uploads (if corrupted)
rsync -av /data/backups/files/ /data/uploads/

# 5. Start application
docker compose start app

# 6. Verify restoration
curl http://localhost/health
curl http://localhost/api/health/ready
```

### Scenario: Security Breach

**Symptoms:**
- Unauthorized admin access detected
- Suspicious audit log entries
- Compromise of SECRET_KEY suspected

**Procedure:**

```bash
# 1. Rotate all secrets immediately
NEW_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
echo "SECRET_KEY=$NEW_SECRET" > .env.secrets

# 2. Revoke all sessions
docker compose exec db psql -U ems_admin -d ems_prod -c \
  "DELETE FROM sessions; DELETE FROM revoked_tokens;"

# 3. Force logout all users (new secret invalidates all JWTs)
docker compose restart app

# 4. Review audit logs for breach scope
docker compose exec db psql -U ems_admin -d ems_prod -c \
  "SELECT * FROM audit_logs WHERE created_at > '2026-05-01' ORDER BY created_at DESC LIMIT 100;"

# 5. Notify DPO and security team
```

---

## S2: High Severity (4-Hour Rollback)

### Scenario: Incorrect Data Deployment

**Symptoms:**
- Wrong exam schedule published
- Incorrect optimization baseline
- Data import error

**Procedure:**

```bash
# Option A: Database point-in-time recovery
# Find migration timestamp before bad deployment
docker compose exec db psql -U ems_admin -d ems_prod -c \
  "SELECT * FROM schema_migrations ORDER BY applied_at DESC LIMIT 5;"

# Re-run migration (if idempotent) or restore snapshot

# Option B: Transaction rollback
# If caught within transaction window (< 1 hour)
psql -U ems_admin -d ems_prod -c "ROLLBACK TO SAVEPOINT pre_import;"
```

### Scenario: Feature Regression

**Symptoms:**
- Key functionality broken after deploy
- API returning 500 errors
- UI components not loading

**Procedure:**

```bash
# 1. Identify last known good commit
git log --oneline -10

# 2. Rollback to previous release tag
git checkout tags/v1.2.0  # Replace with actual good tag

# 3. Rebuild and redeploy
docker compose build app
docker compose up -d app

# 4. Verify fix
curl http://localhost/health
```

---

## S3: Medium Severity (Scheduled Fix)

### Scenario: Workflow Error

**Symptoms:**
- Swap requests not processing
- Check-in confirmations failing
- Export generation slow

**Procedure:**

```bash
# 1. Collect diagnostics
docker compose logs --tail=100 app > /tmp/app_logs.txt
docker compose exec db psql -U ems_admin -d ems_prod -c \
  "SELECT count(*) FROM swap_requests WHERE status = 'pending';"

# 2. Apply hotfix (if available)
git pull origin main
git cherry-pick <hotfix_commit>
docker compose build app && docker compose up -d app

# 3. Monitor recovery
watch -n 30 "curl -s http://localhost/health"
```

---

## Common Troubleshooting

### Database Connection Issues

```bash
# Check database status
docker compose ps db

# View db logs
docker compose logs db --tail=50

# Test connection
docker compose exec app python -c \
  "from backend.database import SessionLocal; print(SessionLocal().execute('SELECT 1').scalar())"

# Restart database (last resort)
docker compose restart db
```

### Application Errors

```bash
# Check app logs
docker compose logs app --tail=100 --follow

# Run diagnostic endpoint
curl http://localhost/api/debug/system-info

# Check memory usage
docker stats ems_app
```

### File Upload Issues

```bash
# Check upload directory permissions
ls -la /data/uploads/
chown -R 1000:1000 /data/uploads

# Check disk space
df -h /data

# Check upload size limit
curl -I http://localhost/api/uploads/config
```

---

## Emergency Contacts

| Severity | Primary | Secondary |
|----------|---------|-----------|
| S1 | System Admin: +66 XXX XXXX | Lead Dev: +66 XXX XXXX |
| S2 | System Admin: +66 XXX XXXX | DevOps: +66 XXX XXXX |
| S3 | Team Lead: +66 XXX XXXX | Rotation: +66 XXX XXXX |
| Security | DPO: dpo@example.edu | Security: security@example.edu |

---

## Post-Incident Checklist

- [ ] Root cause documented
- [ ] Fix deployed and verified
- [ ] Monitoring restored
- [ ] Stakeholders notified
- [ ] Incident report filed
- [ ] Prevention measures identified