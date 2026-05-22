# EXECUTIVE_PILOT_DECISION_BRIEF.md

**Date**: 2026-05-22  
**Audience**: Faculty Executive, Admin, IT Leadership  
**Purpose**: One-page decision brief to select the pilot runtime environment for the EMS controlled pilot.

---

## 1. Current EMS Readiness Status

- **Functional Platform**: Complete (scheduling, optimization, workload analytics, governance workflows, PDPA controls, audit logging)
- **Documentation & Runbooks**: Complete (backup, disaster recovery, logging, hardening reports)
- **UAT Preparation**: Complete (session guides, role checklists, observation templates, Go/No-Go framework)
- **Operational Evidence Templates**: Complete (SECRET_KEY, DATABASE_URL, backup/restore, DPO sign-off)
- **Decision Support Package**: Complete (target options, IT request, launch sequence, blocker dashboard)

**Remaining Blocker**: Concrete pilot runtime target environment has **not** been designated.

Until a target is chosen and provisioned, no real production evidence (SECRET_KEY, DATABASE_URL, backup, DPO sign-off, or UAT) can be collected.

---

## 2. Key Decision Needed

**Select one pilot runtime target environment** and assign owners so that configuration and evidence collection can begin immediately.

---

## 3. Recommended Options

**Option A — Local Rehearsal Machine**  
Suitable only for internal practice. Not acceptable for official pilot evidence.

**Option B — Faculty LAN Server / On-Premise Machine** (Recommended for controlled pilot)  
Best fit for single-faculty, 10-20 users, strong PDPA control.

**Option C — Docker Host / VM** (Strong alternative)  
Excellent repeatability, clean separation, easy backup/restore.

**Option D — Cloud VM**  
Flexible but requires PDPA and budget review.

**Option E — Existing University Infrastructure**  
Best for long-term but higher coordination effort.

---

## 4. Recommended Default

Unless a ready faculty server already exists, we recommend:

- **Primary**: Option B (Faculty LAN Server) or Option C (Docker/VM) for the controlled pilot.
- **Local machine**: Use only for rehearsal while the real target is being provisioned.

---

## 5. Why Local Machine Is Not Official Pilot Evidence

- Not institutionally governed
- No proper backup/restore policy or evidence
- No separation between development and pilot data
- Cannot support credible PDPA-controlled pilot

---

## 6. What Must Be Approved

- Selected pilot target environment
- Responsible IT / Infrastructure owner
- Responsible EMS deployment owner
- Network scope (LAN-only recommended for initial pilot)
- Pilot user group (10-20 users)
- Backup responsibility
- DPO review path and timeline

---

## 7. Decision Form (To Be Completed)

| Field                    | Value                                      |
|--------------------------|--------------------------------------------|
| Selected Option          | (A / B / C / D / E)                        |
| Specific Host / VM       |                                            |
| IT Owner                 |                                            |
| EMS Deployment Owner     |                                            |
| Target Pilot URL         |                                            |
| Network Scope            |                                            |
| Expected Pilot Users     |                                            |
| Target Pilot Start Date  |                                            |
| Approval Status          | (Pending / Approved / Rejected)            |
| Comments                 |                                            |

---

## 8. One-Page Summary Table

| Area                        | Current Status              | Decision Needed                  | Primary Owner     | Due Date |
|-----------------------------|-----------------------------|----------------------------------|-------------------|----------|
| Pilot Runtime Target        | Not designated              | Choose environment + owner       | Faculty Leadership| TBD      |
| Production SECRET_KEY       | Template ready              | Configure in target              | IT / DevOps       | TBD      |
| PostgreSQL DATABASE_URL     | Template ready              | Provision & configure            | IT / DBA          | TBD      |
| Backup & Restore Evidence   | Template ready              | Execute & document               | Ops / IT          | TBD      |
| DPO Retention Sign-off      | Template ready              | Review & sign                    | Admin + DPO       | TBD      |
| Pilot Accounts & UAT        | Preparation complete        | Execute after environment ready  | EMS Team          | TBD      |
| Go/No-Go Approval           | GO WITH CONDITIONS          | After all evidence collected     | Faculty Leadership| TBD      |

---

**Next Step**: IT / Faculty to complete the decision form above and return it to the EMS team. Once received, we will immediately begin configuration and evidence collection using the prepared packages.

**Contact**: EMS Project Team (to be assigned by owner)

---

**End of EXECUTIVE_PILOT_DECISION_BRIEF.md**  
Ready for distribution to executives and IT. No values fabricated.