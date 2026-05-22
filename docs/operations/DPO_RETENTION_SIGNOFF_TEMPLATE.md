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

**Policy Reviewed By**: _______________________________  
**Retention Period Approved**: _______________________________ (e.g., 90 days for operational data, 1 year for audit)

### 2. Backup Retention
- Backup retention period: 30 days minimum (as per BACKUP_AND_RESTORE_RUNBOOK.md)
- Offsite storage location reviewed: [ ] Yes
- Backup encryption / access controls reviewed: [ ] Yes
- Evidence link: _______________________________

**Backup Retention Approved**: [ ] Yes  [ ] No (notes below)

### 3. Audit Log Retention
- Audit logs (database + application) retention period defined: _______________________________
- Access to audit logs restricted to authorized roles only: [ ] Yes
- PDPA compliance of audit content confirmed (no raw PII in exports): [ ] Yes
- Evidence link: _______________________________

**Audit Log Retention Approved**: [ ] Yes  [ ] No

### 4. Export Retention
- Exported files (PDF, Excel, CSV) retention and deletion policy defined: _______________________________
- Export audit trail covers all export types: [ ] Yes
- Evidence link: _______________________________

**Export Retention Approved**: [ ] Yes  [ ] No

---

## PDPA Concerns & Mitigation Notes

**PDPA Concerns Identified**:
_______________________________________________________________________________
_______________________________________________________________________________

**Mitigation Notes / Actions**:
_______________________________________________________________________________
_______________________________________________________________________________

---

## DPO Review & Sign-Off

**I have reviewed the above retention, backup, audit, and export policies for the EMS system.**

- [ ] Policies are appropriate for PDPA compliance and institutional requirements.
- [ ] Retention periods are justified and documented.
- [ ] Backup and restore procedures support the retention policy.
- [ ] Audit and export handling meets PDPA requirements.
- [ ] No concerns with current implementation (or concerns noted above).

**DPO Name**: _______________________________  
**Title / Department**: _______________________________  
**Signature / Electronic Approval**: _______________________________  
**Date**: _______________________________

**Approval Decision**: [ ] Approved  [ ] Approved with Conditions  [ ] Rejected

**Conditions or Rejection Reason** (if applicable):
_______________________________________________________________________________

---

## Admin / System Owner Counter-Sign (if required)

**Name**: _______________________________  
**Date**: _______________________________  
**Signature**: _______________________________

---

**End of DPO_RETENTION_SIGNOFF_TEMPLATE.md**  
Completed and signed version must be attached to `PILOT_OPERATIONAL_BLOCKER_CLOSURE.md` as evidence for blocker #4. All fields are ready for real governance sign-off.