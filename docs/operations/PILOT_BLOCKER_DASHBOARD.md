# PILOT_BLOCKER_DASHBOARD.md

**Date**: 2026-05-22  
**Purpose**: Simple, living tracker for all pilot launch blockers. Update this document as evidence is collected.

---

## Pilot Blocker Status

| Blocker                          | Owner                  | Required Evidence                              | Current Status     | Blocking Level | Next Action                              | Due Date   |
|----------------------------------|------------------------|------------------------------------------------|--------------------|----------------|------------------------------------------|------------|
| Pilot target environment         | (To be assigned)       | Completed intake in `PILOT_ENVIRONMENT_SETUP_RECORD.md` | OPEN               | Critical       | IT/faculty decision + `IT_PILOT_ENVIRONMENT_REQUEST.md` | TBD        |
| SECRET_KEY production value      | DevOps / Deployment Owner | Production-grade key configured + verification in handoff checklist | OPEN               | Critical       | Configure in target environment          | TBD        |
| PostgreSQL DATABASE_URL          | DevOps / DBA           | Working PostgreSQL connection + health check   | OPEN               | High           | Provision database in target             | TBD        |
| Backup scheduled + tested        | Ops / DevOps           | Completed `BACKUP_RESTORE_TEST_EVIDENCE.md`    | OPEN               | High           | First backup + restore test              | TBD        |
| DPO retention sign-off           | Admin + DPO            | Signed `DPO_RETENTION_SIGNOFF_TEMPLATE.md`     | OPEN               | Medium         | DPO review                               | TBD        |
| Pilot accounts ready             | EMS System Owner       | Account creation log + role verification       | OPEN               | Medium         | Create accounts after environment ready  | TBD        |
| UAT execution                    | Pilot Coordinator      | Completed checklists + observation forms       | OPEN               | Medium         | Execute after accounts + environment     | TBD        |
| Go/No-Go approval                | Faculty Leadership     | Updated `UAT_GO_NO_GO_REPORT.md` with evidence | OPEN               | High           | Review all evidence                      | TBD        |

---

## Status Legend

- **OPEN** — No work started or no evidence yet
- **IN PROGRESS** — Work underway
- **EVIDENCE ATTACHED** — Proof collected but not yet verified
- **CLOSED** — Verified and accepted (only after real proof)
- **BLOCKED** — Waiting on another blocker

---

**Important Rule**: Never change status to CLOSED without attaching or linking real evidence in the referenced documents.

---

**End of PILOT_BLOCKER_DASHBOARD.md**  
This dashboard should be updated after every significant piece of evidence is collected. It provides a single view of what is still blocking the pilot launch.