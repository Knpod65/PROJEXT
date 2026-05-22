# DPO_RETENTION_SIGNOFF_TEMPLATE.md

**Date**: 2026-05-22  
**Purpose**: Formal sign-off template for Data Protection Officer (DPO) review of EMS data retention, backup, audit, and export policies.  
**Required before**: Enabling automated retention cleanup or declaring pilot fully operational.

---

## Policy Areas Reviewed

### 1. Retention Policy (backend/config/retention_policy.py and related)

- Retention periods defined for:
  - Schedules and submissions
  - User activity / audit logs
  - Exports and generated reports
  - Personal data (student/teacher identifiers)
- Dry-run report generated and reviewed: [ ] Yes  [ ] No
- Evidence link / attachment: _______________________________

### 2. Backup Retention

- Backup retention period: 30 days minimum (as per BACKUP_AND_RESTORE_RUNBOOK.md)
- Offsite storage location reviewed
- Backup encryption / access controls reviewed
- Evidence link: _______________________________

### 3. Audit Log Retention

- Audit logs (database + application) retention period defined
- Access to audit logs restricted to authorized roles only
- PDPA compliance of audit content confirmed (no raw PII in exports)
- Evidence link: _______________________________

### 4. Export Retention

- Exported files (PDF, Excel, CSV) retention and deletion policy defined
- Export audit trail covers all export types
- Evidence link: _______________________________

---

## DPO Review & Sign-Off

**I have reviewed the above retention, backup, audit, and export policies for the EMS system.**

- [ ] Policies are appropriate for PDPA compliance and institutional requirements.
- [ ] Retention periods are justified and documented.
- [ ] Backup and restore procedures support the retention policy.
- [ ] No concerns with current implementation (or concerns noted below).

**DPO Name**: _______________________________  
**Title / Department**: _______________________________  
**Signature / Electronic Approval**: _______________________________  
**Date**: _______________________________

**Additional Comments or Conditions**:
_______________________________________________________________________________
_______________________________________________________________________________

---

## Admin / System Owner Counter-Sign (if required)

**Name**: _______________________________  
**Date**: _______________________________

---

**End of DPO_RETENTION_SIGNOFF_TEMPLATE.md**  
Completed and signed version must be attached to `PILOT_OPERATIONAL_BLOCKER_CLOSURE.md` as evidence for blocker #4.