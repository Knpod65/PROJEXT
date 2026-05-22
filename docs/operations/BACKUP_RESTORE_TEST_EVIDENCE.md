# BACKUP_RESTORE_TEST_EVIDENCE.md

**Date**: 2026-05-22  
**Purpose**: Formal evidence template for the first successful backup + restore test required for pilot readiness.  
**Owner**: Ops / DevOps

---

## Backup Execution Record

- **Backup Timestamp (UTC)**: _______________________________
- **Backup Command Used**:
  ```bash
  pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME -Fc -f /backups/ems_$(date +%Y%m%d_%H%M%S).dump
  ```
- **Backup File Path** (full path on storage): _______________________________
- **Backup File Size**: _______________
- **Storage Location** (offsite / secondary site): _______________________________
- **Retention Policy Applied**: 30 days minimum (per runbook)
- **Responsible Person**: _______________________________
- **Date Performed**: _______________________________

---

## Restore Test Record

- **Restore Target** (test database / staging instance): _______________________________
- **Restore Command Used**:
  ```bash
  pg_restore -h $RESTORE_HOST -U $RESTORE_USER -d $RESTORE_DB -v /backups/ems_YYYYMMDD_HHMMSS.dump
  ```
- **Restore Start Time**: _______________________________
- **Restore End Time**: _______________________________
- **Errors Encountered**: [ ] None  [ ] Documented below

---

## Restore Verification Checklist

- [ ] Database schema matches production (tables, indexes, constraints)
- [ ] Row counts for critical tables (schedules, users, submissions, audit_logs) within expected range
- [ ] No data corruption detected (sample queries succeed)
- [ ] Application can connect to restored database
- [ ] Health endpoint reports `db: connected`
- [ ] Sample login and schedule query succeed in test environment
- [ ] No PII leakage observed in restored data (spot check)

**Verification Performed By**: _______________________________  
**Date**: _______________________________

---

## Result

**Overall Result**: [ ] Success  [ ] Partial  [ ] Failed (details attached)

**Notes / Issues**:
_______________________________________________________________________________
_______________________________________________________________________________

**Next Action**:
- If successful: schedule daily automated backup and update `PILOT_OPERATIONAL_BLOCKER_CLOSURE.md`
- If issues: document and re-test before pilot

---

**End of BACKUP_RESTORE_TEST_EVIDENCE.md**  
Attach this completed template (or link to internal ticket) as evidence for blocker #3.