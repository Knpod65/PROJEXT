# BACKUP_RESTORE_TEST_EVIDENCE.md

**Date**: 2026-05-22  
**Purpose**: Formal evidence template and executable workflow for the first successful backup + restore test required for pilot readiness.  
**Owner**: Ops / DevOps

---

## Backup Execution Checklist

- [ ] Production database identified and accessible
- [ ] Backup command prepared (custom format recommended)
- [ ] Backup storage location confirmed (offsite / secondary)
- [ ] Backup started
- [ ] Backup completed successfully
- [ ] Backup file verified (size > 0, not corrupted)
- [ ] Backup file copied to offsite storage
- [ ] Timestamp recorded

**Backup Timestamp (UTC)**: _______________________________  
**Backup Command Used**:
```bash
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME -Fc -f /backups/ems_$(date +%Y%m%d_%H%M%S).dump
```
**Backup File Path** (full path): _______________________________  
**Backup File Size**: _______________ MB  
**Storage Location**: _______________________________  
**Responsible Person**: _______________________________  
**Date Performed**: _______________________________

---

## Restore Execution Checklist

- [ ] Restore target database prepared (test/staging instance, never production)
- [ ] Restore command prepared
- [ ] Restore started
- [ ] Restore completed without fatal errors
- [ ] Post-restore schema verification
- [ ] Row count verification on critical tables

**Restore Target**: _______________________________  
**Restore Command Used**:
```bash
pg_restore -h $RESTORE_HOST -U $RESTORE_USER -d $RESTORE_DB -v /backups/ems_YYYYMMDD_HHMMSS.dump
```
**Restore Start Time**: _______________________________  
**Restore End Time**: _______________________________  
**Errors Encountered**: [ ] None  [ ] Documented in Notes

---

## Smoke Validation After Restore

- [ ] Application can connect to restored database
- [ ] Health endpoint `/health` returns `{"status": "ok", "db": "connected"}`
- [ ] Sample login succeeds for at least one role
- [ ] Sample schedule query returns expected data
- [ ] No critical errors in application logs during smoke test

**Smoke Test Performed By**: _______________________________  
**Date/Time**: _______________________________

---

## Dashboard Verification (Post-Restore)

- [ ] Admin Intelligence Dashboard loads without errors
- [ ] Workload analytics charts render with data
- [ ] Governance workflow lists show expected entries
- [ ] Export endpoints return data without crash

**Dashboard Verification Result**: [ ] Pass  [ ] Fail (details below)

---

## Audit Log Verification (Post-Restore)

- [ ] Recent audit log entries are present
- [ ] No corruption in audit table
- [ ] PDPA-safe fields (IP hash, no raw PII) confirmed

**Audit Log Verification Result**: [ ] Pass  [ ] Fail

---

## Rollback Timing Test (Optional but Recommended)

- [ ] Time to detect issue: ________ minutes
- [ ] Time to initiate rollback: ________ minutes
- [ ] Time to restore from backup and verify: ________ minutes
- [ ] Total rollback window observed: ________ minutes

**Rollback Timing Result**: _______________________________

---

## Evidence Attachment Placeholders

- Backup file hash / screenshot of backup success: _______________________________
- Restore log excerpt or screenshot: _______________________________
- Health endpoint response screenshot: _______________________________
- Dashboard screenshot after restore: _______________________________
- Audit log sample screenshot: _______________________________
- Rollback timing log: _______________________________

---

## Result

**Overall Result**: [ ] Success  [ ] Partial  [ ] Failed

**Expected Outcome Examples**:
- Success: Full schema + data restored, application fully functional on restored DB, all smoke tests pass.
- Partial: Schema restored but some data missing or one dashboard broken.
- Failed: Restore errors, connection failures, or data corruption detected.

**Notes / Issues**:
_______________________________________________________________________________
_______________________________________________________________________________

**Next Action**:
- If successful: Schedule daily automated backup, attach evidence to `PILOT_OPERATIONAL_BLOCKER_CLOSURE.md`, mark blocker #3 as Verified.
- If issues: Document, re-test, and do not proceed to pilot until resolved.

---

**End of BACKUP_RESTORE_TEST_EVIDENCE.md**  
This expanded template now provides executable checklists and evidence placeholders for real operational validation. Attach completed version as proof for blocker #3.