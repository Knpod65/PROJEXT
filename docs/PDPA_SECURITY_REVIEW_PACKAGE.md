# PDPA Security Review Package — EMS Exam Management System

> Version: 2026-05-20  
> Target: IT Security Review + DPO Sign-off  
> Purpose: Demonstrate PDPA compliance for pilot deployment

---

## 1. Data Classification

### Personal Data Categories

| Category | Examples | Source | Retention |
|----------|----------|--------|-----------|
| Student Academic Records | Student ID, name, schedule, enrollment | Registrar | Until graduation + 5 years |
| Staff/Employee Data | Name, role, contact, schedule | HR | Employment + 7 years |
| Authentication Data | Username, hashed password | CMU SSO | Until account deletion |
| Audit Trail Data | Actions, timestamps, IP hash | System generated | 1 year (configurable) |
| QR Check-in Data | Time, location, user anonymous ID | QR scan | 1 semester |

### Sensitive Data (Higher Protection)

- Exam submission files — encrypted at rest, audit-logged on access
- Check-in locations — stored with anonymous user hash
- IP addresses — SHA-256 hashed with per-install salt

---

## 2. Privacy Controls

### Access Control Matrix

| Role | Student Info | Schedule | Check-ins | Submissions | Admin Logs |
|------|--------------|----------|-----------|-------------|------------|
| Student | Self only | Self only | Self only | Self only | No |
| Teacher | Self only | Own sections | No | Own submissions | No |
| Staff | Self only | Department | Department | Department | Limited |
| Dept Supervisor | Department | Department | Department | Department | Department |
| Admin | All | All | All | All | All (audit) |

### Data Minimization

```python
# backend/utils/privacy.py
def hash_ip(ip_address: str, salt: str) -> str:
    """Store IP as one-way hash for audit, not raw IP"""
    return hashlib.sha256(f"{ip_address}{salt}".encode()).hexdigest()

def truncate_user_agent(ua: str) -> str:
    """Store first 32 chars only, then hash"""
    return hashlib.sha256(ua[:32].encode()).hexdigest()
```

### Anonymization Examples

```python
# Student schedule endpoint — PDPA compliant
@router.get("/public/schedule/{student_id}")
def get_student_schedule(
    student_id: str,
    current_user: User = Depends(get_current_user)
):
    # PDPA: Students can only access their own data
    if current_user.username != student_id:
        raise HTTPException(403, "Access denied")
    return db.query(StudentSchedule).filter_by(student_id=student_id).all()
```

---

## 3. Audit Logging

### Structured Audit Events

All audit events stored in `audit_logs` table:

| Event Type | PII Stored | Details |
|------------|------------|---------|
| `LOGIN` | No | username, timestamp, IP hash, user-agent hash |
| `EXPORT_SCHEDULE_PDF` | No | file_type, scope, row_count, semester |
| `CHECKIN_SUCCESS` | No | anonymous_user_hash, location, time |
| `VIEW_EXAM_FILE` | No | watermark_token, IP hash |
| `IMPORT_COMMIT_V2` | No | file_name, row_count, timestamp |

### Audit Log Schema

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    user_id UUID REFERENCES users(id),
    ip_hash VARCHAR(64),                    -- SHA-256 hash
    user_agent_hash VARCHAR(64),            -- SHA-256 hash
    metadata JSONB,                         -- Non-PII details only
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Verification Query

```sql
-- Check for any PII in audit logs
SELECT * FROM audit_logs 
WHERE metadata::text ILIKE '%name%' 
   OR metadata::text ILIKE '%email%'
   OR metadata::text ILIKE '%student_id%';
-- Expected: 0 rows
```

---

## 4. Data Retention

### Retention Schedule

| Data Type | Retention Period | Legal Basis |
|-----------|------------------|-------------|
| Audit logs | 1 year | Operational necessity |
| Check-in records | End of semester | Transaction completion |
| Schedule snapshots | 5 years | Academic records |
| Exported files | 30 days | Temp operational data |
| User sessions | 1 day | Security |
| Revoked tokens | 1 day | Security cleanup |

### Retention Implementation

```python
# backend/config/retention_policy.py
RETENTION_POLICY = {
    "audit_logs": timedelta(days=365),
    "checkin_logs": "end_of_semester",
    "schedule_snapshots": timedelta(days=5*365),
    "exported_files": timedelta(days=30),
}

# Dry-run helper
def generate_dry_run_report(db: Session) -> dict:
    """Show how many rows would be deleted"""
    counts = {}
    for table, policy in RETENTION_POLICY.items():
        if isinstance(policy, timedelta):
            cutoff = datetime.utcnow() - policy
            counts[table] = db.execute(
                f"SELECT count(*) FROM {table} WHERE created_at < :cutoff",
                {"cutoff": cutoff}
            ).scalar()
    return counts
```

---

## 5. Security Measures

### Encryption

| Data | At Rest | In Transit |
|------|---------|------------|
| Database | PostgreSQL TDE | TLS 1.3 |
| File uploads | AES-256 (filesystem) | HTTPS only |
| Backups | gzip + disk encryption | SCP/SFTP |
| Session cookies | HttpOnly + Secure flag | TLS required |

### Authentication

- CMU SSO integration (SAML/OAuth)
- Session cookies: HttpOnly, SameSite=Lax, Secure
- JWT tokens: 12-hour expiry, refresh flow
- Failed login: Account lockout after 5 attempts

### Network Security

```nginx
# Security headers (nginx.conf)
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Content-Security-Policy "default-src 'self'" always;
```

---

## 6. Incident Response

### Data Breach Procedure

1. **Detect**: Monitor alerts for unusual audit log volume
2. **Contain**: Disable compromised accounts, rotate secrets
3. **Assess**: Determine data categories affected
4. **Notify**: DPO within 72 hours if high risk
5. **Document**: Record in incident log

### Security Contact

| Role | Email | Phone |
|------|-------|-------|
| DPO | dpo@example.edu | +66 XXX XXXX |
| Security Team | security@example.edu | +66 XXX XXXX |
| Emergency | noc@example.edu | +66 XXX XXXX |

---

## 7. Compliance Checklist

- [x] Student data accessible only to authorized roles
- [x] IP addresses stored as SHA-256 hash only
- [x] User-agent truncated + hashed before storage
- [x] No PII in audit log metadata
- [x] Retention periods defined and configurable
- [x] Data deletion implements hard delete (not soft delete)
- [x] SSL/TLS enforced for all connections
- [x] Cookie security flags set (HttpOnly, Secure, SameSite)
- [x] JWT signed with strong secret key
- [x] Failed login attempt tracking

---

## 8. DPO Sign-off

To be completed after review:

| Item | Sign-off | Date |
|------|----------|------|
| Data classification audit | | |
| Retention schedule approval | | |
| Security controls verification | | |
| Incident response acknowledgment | | |

---

## 9. References

- `docs/PDPA_SECURITY_GUIDE.md` — Full guide
- `docs/PRODUCTION_READINESS_CHECKLIST.md` — General security checklist
- `backend/config/retention_policy.py` — Retention configuration