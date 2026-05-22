# PILOT_ENVIRONMENT_SETUP_RECORD.md (Expanded)

**Date**: 2026-05-22 (Updated)  
**Purpose**: Master record of pilot environment decision and readiness status.

---

## Pilot Environment Decision Status

**Current Status**: **BLOCKED — Pilot target environment not yet designated**

As documented in `PILOT_TARGET_DECISION_PACKAGE.md`, five environment options have been analyzed. A concrete choice has not been made.

**Last Update**: 2026-05-22

---

## Candidate Options Considered

The following options were evaluated (see `PILOT_TARGET_DECISION_PACKAGE.md` for full analysis):

- Option A — Local Internal Demo Machine (Rehearsal only)
- Option B — Faculty LAN Server / On-Premise Machine (Recommended for controlled pilot)
- Option C — Docker Host / VM (Strong repeatable option)
- Option D — Cloud VM (Possible with PDPA/budget approval)
- Option E — Existing University/Faculty Infrastructure (Good for later phases)

**Primary recommendation from analysis**: Option B or Option C for the initial controlled faculty pilot.

---

## Required Information Before Continuing

Before any configuration, deployment, backup testing, or real UAT can begin, the following must be recorded:

1. Selected pilot target environment (host/machine/URL)
2. Responsible IT person and system owner
3. Network scope and access method
4. Database endpoint details
5. Backup storage location and responsibility
6. Expected pilot start date

Until the above are provided and recorded in this document, the pilot remains blocked at the environment decision stage.

---

## Owner Assignment Table

| Role                        | Name / Team          | Responsibility                              | Contact          | Assigned Date |
|-----------------------------|----------------------|---------------------------------------------|------------------|---------------|
| Pilot Environment Owner     | (To be assigned)     | Final decision on target environment        |                  |               |
| IT / Infrastructure Lead    | (To be assigned)     | Provisioning, network, security, backup     |                  |               |
| EMS System Owner            | (To be assigned)     | Overall pilot coordination                  |                  |               |
| DPO / PDPA Reviewer         | (To be assigned)     | Retention sign-off and PDPA review          |                  |               |

---

## Target Environment Intake Form

(To be completed by the selected Environment Owner)

- **Environment Name**: _______________________________
- **Host / Server / VM Name**: _______________________________
- **IP Address / DNS**: _______________________________
- **Deployment Method**: (Docker Compose / Manual / Other) _______________________________
- **Database Type & Host**: _______________________________
- **Access URL (for pilot users)**: _______________________________
- **Network Scope**: (LAN-only / VPN / Limited external) _______________________________
- **Expected Number of Pilot Users**: _______________________________
- **Backup Responsibility**: _______________________________
- **Security / Secret Management**: _______________________________
- **Planned Pilot Start Date**: _______________________________

---

## Environment Readiness Criteria

Before declaring the environment "ready for pilot evidence collection", the following must be true:

- [ ] Target host confirmed and accessible to deployment team
- [ ] PostgreSQL database provisioned and reachable
- [ ] `SECRET_KEY` generated and stored securely (production strength)
- [ ] `DATABASE_URL` configured and tested
- [ ] `DEBUG=False` and production settings applied
- [ ] Backup mechanism implemented and first backup taken
- [ ] Restore test performed to a safe target
- [ ] DPO retention sign-off received or documented exception
- [ ] Pilot user accounts created and verified
- [ ] Smoke test passed (health, login, dashboards, exports)

---

## Evidence Collection Dependency Map

| Evidence Type                  | Can be collected without target? | Depends on |
|--------------------------------|----------------------------------|------------|
| Local rehearsal screenshots    | Yes                              | Local machine only |
| Production SECRET_KEY evidence | No                               | Target environment |
| Production DATABASE_URL        | No                               | Target environment |
| Real backup/restore evidence   | No                               | Target + database |
| DPO sign-off                   | Partially (policy review)        | DPO availability |
| Real UAT with users            | No                               | Target + accounts |
| Go/No-Go with real evidence    | No                               | All of the above |

**Statement**: No real deployment smoke test, backup/restore evidence, or UAT execution can be completed until the target environment section is filled by the responsible party.

---

## Blocker Closure Path

1. Pilot target environment designated → Record in this document + `PILOT_TARGET_DECISION_PACKAGE.md`
2. Environment provisioned and configured → Update `PRODUCTION_ENV_HANDOFF_CHECKLIST.md`
3. Backup/restore tested → Update `BACKUP_RESTORE_TEST_EVIDENCE.md`
4. DPO sign-off → Update `DPO_RETENTION_SIGNOFF_TEMPLATE.md`
5. Pilot accounts ready → Update `PILOT_ACCOUNT_READINESS_RECORD.md` (to be created)
6. Smoke tests passed → Update `PILOT_DEPLOYMENT_SMOKE_EVIDENCE.md` (to be created)
7. All 5 blockers verified → Update `PILOT_OPERATIONAL_BLOCKER_CLOSURE.md` and `UAT_GO_NO_GO_REPORT.md`

---

**End of PILOT_ENVIRONMENT_SETUP_RECORD.md (Expanded Version)**  
This document now serves as the single intake and tracking point for the pilot environment decision. No real deployment work can proceed until the intake form is completed.