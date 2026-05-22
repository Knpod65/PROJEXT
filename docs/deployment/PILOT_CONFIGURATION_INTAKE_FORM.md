# PILOT_CONFIGURATION_INTAKE_FORM.md

**Date**: 2026-05-22  
**Purpose**: Fillable intake form for the person who will configure and own the pilot environment.

---

## A. Environment Identity

- **Environment Name**: _______________________________
- **Host / Server / VM**: _______________________________
- **Network Scope**: (LAN-only / VPN / Limited external) _______________________________
- **Public / Internal URL**: _______________________________
- **Deployment Method**: (Docker Compose / Manual / Other) _______________________________
- **Responsible Deployment Owner**: _______________________________
- **Target Pilot Start Date**: _______________________________

---

## B. Backend Configuration

- **ENVIRONMENT** set to `production`: [ ] Yes  [ ] No
- **SECRET_KEY** configured (production strength, ≥50 chars): [ ] Yes  [ ] No
  - Storage method: (env file / secret manager / other) _______________________________
- **DATABASE_URL** configured and tested: [ ] Yes  [ ] No
- **ALLOWED_HOSTS** set: [ ] Yes  [ ] No
- **LOG_LEVEL** set: _______________________________
- **DEBUG=False** verified: [ ] Yes  [ ] No
- **Retention variables** (`PDPA_RETENTION_DAYS`, etc.) set: [ ] Yes  [ ] No

**Verification Date**: _______________________________  
**Verified By**: _______________________________

---

## C. Database

- **Database Type**: PostgreSQL (required)
- **Database Host / Instance**: _______________________________
- **Backup Method**: _______________________________
- **Backup Schedule**: _______________________________
- **Backup Retention**: _______________________________
- **Restore Test Target** (must be non-production): _______________________________
- **First Backup Completed**: [ ] Yes  [ ] No   Date: _______________

---

## D. Frontend

- **Frontend URL**: _______________________________
- **API Base URL**: _______________________________
- **Language Support** (Thai/English) verified: [ ] Yes  [ ] No
- **Browser Compatibility** tested: [ ] Yes  [ ] No

---

## E. Security / PDPA

- **DPO Reviewer Assigned**: _______________________________
- **Retention Policy Sign-off Received**: [ ] Yes  [ ] No  [ ] In Progress
- **Audit Log Retention** reviewed: [ ] Yes  [ ] No
- **Export Retention** reviewed: [ ] Yes  [ ] No
- **Backup Retention** reviewed: [ ] Yes  [ ] No

---

## F. UAT Preparation

- **Pilot Accounts Prepared**:
  - Admin: [ ] Yes  [ ] No
  - Staff: [ ] Yes  [ ] No
  - Supervisor: [ ] Yes  [ ] No
  - Teacher: [ ] Yes  [ ] No
  - Executive/Governance: [ ] Yes  [ ] No

- **Planned UAT Start Date**: _______________________________
- **Evidence Folder Location**: _______________________________

---

**End of PILOT_CONFIGURATION_INTAKE_FORM.md**  
This form should be completed by the deployment owner once the target environment is assigned and provisioned.