# PILOT_LAUNCH_SEQUENCE.md

**Date**: 2026-05-22  
**Purpose**: Phased sequence for moving from environment decision to controlled pilot execution.

---

## Stage 0 — Decision

- Select pilot target environment (using `PILOT_TARGET_DECISION_PACKAGE.md`)
- Assign owners (Environment Owner, IT Lead, EMS System Owner, DPO)
- Record decision in `PILOT_ENVIRONMENT_SETUP_RECORD.md`

**Owner**: Project / Faculty Lead  
**Output Evidence**: Completed decision section in `PILOT_ENVIRONMENT_SETUP_RECORD.md`  
**Pass Criteria**: Target chosen and owners assigned  
**Blocker if not met**: Cannot proceed to Stage 1

---

## Stage 1 — Configure Environment

- Provision host / VM / server
- Configure all production environment variables (see `PRODUCTION_ENV_HANDOFF_CHECKLIST.md` and `PILOT_CONFIGURATION_INTAKE_FORM.md`)
- Set up PostgreSQL and initial schema
- Apply security hardening (`SECRET_KEY`, `DEBUG=False`, allowed hosts, etc.)

**Owner**: IT / Deployment Owner  
**Output Evidence**: Filled `PILOT_CONFIGURATION_INTAKE_FORM.md` + verification in `PRODUCTION_ENV_HANDOFF_CHECKLIST.md`  
**Pass Criteria**: All critical variables verified without exposing secrets  
**Blocker if not met**: SECRET_KEY and DATABASE_URL blockers remain open

---

## Stage 2 — Deploy

- Deploy backend and frontend to the target
- Run database migrations
- Verify health endpoints
- Confirm login and basic navigation

**Owner**: Deployment Owner  
**Output Evidence**: `PILOT_DEPLOYMENT_SMOKE_EVIDENCE.md` (to be created)  
**Pass Criteria**: Health check passes, login works for at least one role  
**Blocker if not met**: Cannot proceed to backup or UAT

---

## Stage 3 — Backup & Restore Test

- Implement daily backup process
- Perform first backup
- Restore to a safe test target
- Validate data integrity and application functionality post-restore

**Owner**: Ops / DevOps  
**Output Evidence**: Completed `BACKUP_RESTORE_TEST_EVIDENCE.md`  
**Pass Criteria**: Restore successful + smoke checks pass  
**Blocker if not met**: Backup blocker remains open

---

## Stage 4 — Governance & PDPA

- DPO reviews retention policy, backup, audit, and export handling
- Obtain formal sign-off (or documented exception)

**Owner**: Admin + DPO  
**Output Evidence**: Signed `DPO_RETENTION_SIGNOFF_TEMPLATE.md`  
**Pass Criteria**: Sign-off received or exception approved by faculty leadership  
**Blocker if not met**: DPO blocker remains open

---

## Stage 5 — Pilot Account & UAT Preparation

- Create pilot accounts for Admin, Staff, Supervisor, Teacher, Executive roles
- Verify permissions and restrictions
- Prepare evidence folder and assign UAT observers

**Owner**: EMS System Owner  
**Output Evidence**: `PILOT_ACCOUNT_READINESS_RECORD.md` (to be created) + accounts ready  
**Pass Criteria**: All planned roles can log in with correct visibility  
**Blocker if not met**: Cannot start real UAT

---

## Stage 6 — UAT Execution & Go/No-Go

- Execute role-based UAT using `UAT_SESSION_EXECUTION_GUIDE.md` and `UAT_ROLE_WORKFLOW_CHECKLISTS.md`
- Capture observations with `PILOT_OBSERVATION_CAPTURE.md`
- Review all collected evidence
- Make formal Go/No-Go decision

**Owner**: Pilot Coordinator + Reviewers  
**Output Evidence**: Updated `UAT_GO_NO_GO_REPORT.md` and `PILOT_EXECUTION_EVIDENCE_SUMMARY.md`  
**Pass Criteria**: Evidence package complete and decision recorded

---

## Stage 7 — Controlled Pilot Execution

- Open pilot to approved users (10-20)
- Daily/weekly monitoring and feedback collection
- Issue triage using `PILOT_BUG_TRIAGE.md`
- Weekly governance review

**Owner**: EMS System Owner + Faculty  
**Success Criteria**: Stable operation with documented feedback for 4–8 weeks

---

**End of PILOT_LAUNCH_SEQUENCE.md**  
Each stage has clear owners, evidence requirements, and blocker conditions. No stage should be skipped when real evidence is required.