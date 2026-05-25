# FACULTY_WEB_POSTGRESQL_DEPLOYMENT_PLAN.md

**Date**: 2026-05-25

## Recommended Approach for Faculty Web Portal Deployment

**Strong recommendation**: Use a **dedicated EMS PostgreSQL database** (or at minimum a dedicated schema) under the faculty web hosting environment.

Do not co-locate EMS tables with existing Laravel application tables unless a formal data governance contract exists.

## Key Principles

- EMS owns its schema and data.
- Separate credentials for EMS (least privilege).
- Clear backup/restore ownership (IT/faculty web team or EMS ops, with SLA).
- Migrations owned by EMS team (Alembic or equivalent recommended long-term).
- No real production data without DPO / governance approval.
- Demo / seed data policy: local SQLite or isolated dev DB only.

## Environment Variables (Faculty Web Hosting)

```
DATABASE_URL=postgresql://ems_user:***@faculty-db-host:5432/ems_db
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
...
```

Connection must go through the faculty web hosting network (not direct LAN assumption anymore).

## Backup / Restore Requirements

- Must be tested and evidenced before any pilot with real data.
- Ownership and schedule to be confirmed with faculty web / IT.
- See BACKUP_AND_RESTORE_RUNBOOK.md (keep as-is; execution evidence still required).

## Migration & Seed Policy

- Normal startup must never run create_all or seed on production web portal DB.
- Current hardening (ENVIRONMENT != development + explicit guard) already supports this.
- Manual migration jobs or dedicated migration service for web portal deploys.

## Risks if Using Shared DB Without Contract

- Schema conflicts
- Permission / ownership disputes
- Backup scope confusion
- PDPA / data lineage issues

---
*Separate EMS DB or schema is the cleanest path for Faculty Web Portal integration.*
