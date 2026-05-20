# P1 Final System State Audit — EMS Exam Management System

> Date: 2026-05-20  
> Purpose: Capture system state at pilot readiness milestone

---

## Backend Architecture

### Core Services

| Service | Location | Purpose |
|---------|----------|---------|
| `main.py` | `backend/main.py` | FastAPI application entry |
| `database.py` | `backend/database.py` | SQLAlchemy session management |
| `models.py` | `backend/models.py` | SQLAlchemy ORM definitions |
| `permissions.py` | `backend/permissions.py` | Role guards and decorators |
| `permission_service.py` | `backend/services/permission_service.py` | Policy helpers |
| `auth_utils.py` | `backend/auth_utils.py` | JWT utilities |

### Migration Scripts

| Script | Purpose |
|--------|---------|
| `migrate.py` | Main migration runner |
| `migrate_v2.py` | V2 schema changes |
| `migrate_term_lifecycle.py` | Period lifecycle |
| `migrate_historical_schedule_snapshots.py` | Snapshot tables |
| `migrate_exam_ownership.py` | Student schedule ownership |

### Key Configuration

```python
# backend/config/retention_policy.py
RETENTION_POLICY = {
    "audit_logs": timedelta(days=365),
    "checkin_logs": "end_of_semester",
    "schedule_snapshots": timedelta(days=5*365),
    "exported_files": timedelta(days=30),
}
```

---

## Frontend Architecture

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `usePermission.ts` | `frontend/src/hooks/usePermission.ts` | Permission hook |
| `Optimizer.tsx` | `frontend/src/pages/Optimizer.tsx` | Schedule optimization |
| `SettingsV2.tsx` | `frontend/src/pages/SettingsV2.tsx` | Settings ViewModel |
| `WorkflowV2.tsx` | `frontend/src/pages/WorkflowV2.tsx` | Workflow management |
| `SwapsV2.tsx` | `frontend/src/pages/SwapsV2.tsx` | Swap requests |

### i18n Structure

```
frontend/src/i18n/
├── en/
│   └── common.json
├── th/
│   └── common.json
└── i18n.ts
```

---

## Authorization Model

### Roles (7 Total)

1. `admin` — Full system access
2. `dept_supervisor` — Department-level operations
3. `esq_head` — Examination scheduling
4. `secretary` — Administrative tasks
5. `staff` — Operations support
6. `teacher` — Exam invigilation
7. `student` — Schedule view only

### Policy Helpers (L5 Additions)

```typescript
// frontend/src/hooks/usePermission.ts
export function usePermission() {
  return {
    canRunOptimizationRecheck: (user: User) =>
      ['admin', 'esq_head'].includes(user.role),
    canImpersonateAdmin: (user: User) =>
      user.role === 'admin',
    canViewGovernanceReport: (user: User) =>
      ['admin', 'esq_head'].includes(user.role),
  };
}
```

---

## Audit Coverage

### Events Logged

| Event Type | Table | Fields Logged |
|------------|-------|---------------|
| LOGIN | audit_logs | user_id, IP hash, user-agent hash |
| LOGOUT | audit_logs | user_id |
| EXPORT_* | audit_logs | file_type, scope, row_count |
| CHECKIN_* | checkin_logs | user_hash, location, time |
| INIT_OPTIMIZATION_SESSION | audit_logs | user_id, scope |
| SIGN_OPTIMIZATION_SESSION | audit_logs | user_id, flags_count |
| IMPORT_* | audit_logs | file_name, row_count |

### PII Handling

- IP addresses: SHA-256 hash with per-install salt
- User-agent: SHA-256 hash of first 32 chars only
- No student names/IDs in audit metadata

---

## Database Schema (Key Tables)

| Table | Rows | Purpose |
|-------|------|---------|
| `users` | ~200 | User accounts |
| `exam_schedules` | ~2000 | Exam schedule data |
| `audit_logs` | ~50000 | Audit trail |
| `swap_requests` | ~1000 | Swap requests |
| `checkin_logs` | ~15000 | QR check-in records |
| `historical_snapshots` | 2 versions | Semester 2/2568 |

---

## Test Coverage

```
Backend: 1256 tests passing
- auth tests: 45
- schedule tests: 312
- swap tests: 187
- checkin tests: 76
- export tests: 98
- permission tests: 89

Frontend: Build clean, TypeScript strict mode
```

---

## Environment Requirements

### Production (.env)

```bash
ENV=production
SECRET_KEY=<generated>
DATABASE_URL=postgresql://ems:pwd@db:5432/ems_prod
CORS_ALLOWED_ORIGINS=https://exam.example.edu
POSTGRES_USER=ems_admin
POSTGRES_PASSWORD=<strong>
POSTGRES_DB=ems_prod
CRON_SECRET=<generated>
RETENTION_CLEANUP_ENABLED=False
```

### Ports

| Service | Port | Internal |
|---------|------|----------|
| Nginx | 80, 443 | — |
| App | 8000 | app:8000 |
| DB | 5432 | db:5432 |

---

## Health Checks

| Endpoint | Response | Purpose |
|----------|----------|---------|
| `/health` | `{"status": "ok", "db": "connected"}` | Basic health |
| `/api/health/ready` | `{"ready": true}` | Deep health |
| `/api/health/stats` | `{"cpu": ..., "mem": ...}` | Metrics |

---

## Known Gaps (Documented, Not Blocking)

1. PDF export headers use hard-coded Thai strings (acceptable)
2. Submission message audit not yet implemented (next sprint)
3. 2 invigilators unresolved in DB (HR data sync needed)
4. Historical snapshot gaps reflect source PDF quality, not system errors