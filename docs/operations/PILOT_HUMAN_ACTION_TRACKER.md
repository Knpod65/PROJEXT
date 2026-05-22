# PILOT_HUMAN_ACTION_TRACKER.md

**Date**: 2026-05-22  
**Purpose**: Track all human-dependent actions required to launch the controlled pilot.

---

| # | Action                              | Owner (to be assigned) | Evidence Required                              | Status     | Due Date | Blocker? | Notes |
|---|-------------------------------------|------------------------|------------------------------------------------|------------|----------|----------|-------|
| 1 | Choose pilot target environment     | Faculty Leadership     | Completed decision in SETUP_RECORD + DECISION_PACKAGE | OPEN       | TBD      | Yes      | Primary blocker |
| 2 | Assign IT / Infrastructure owner    | Faculty Leadership     | Name + contact in records                      | OPEN       | TBD      | Yes      | Required for provisioning |
| 3 | Assign EMS System Owner             | Project Lead           | Name recorded                                  | OPEN       | TBD      | No       | Can be assigned in parallel |
| 4 | Provide server/VM/Docker host       | IT Owner               | Host details + access method                   | OPEN       | TBD      | Yes      | Depends on #1 |
| 5 | Configure SECRET_KEY (production)   | IT + Deployment Owner  | Confirmation in HANDOFF_CHECKLIST              | OPEN       | TBD      | Yes      | Requires target |
| 6 | Configure DATABASE_URL              | IT + DBA               | Working connection + health check              | OPEN       | TBD      | Yes      | Requires target |
| 7 | Configure ALLOWED_HOSTS / DEBUG=False | Deployment Owner     | Verified in intake form                        | OPEN       | TBD      | Yes      | Requires target |
| 8 | Run first backup                    | IT / Ops               | Evidence in BACKUP_RESTORE_TEST_EVIDENCE       | OPEN       | TBD      | Yes      | After deployment |
| 9 | Run restore test                    | IT / Ops               | Successful restore + smoke                     | OPEN       | TBD      | Yes      | After #8 |
|10 | Complete DPO retention sign-off     | Admin + DPO            | Signed DPO_RETENTION_SIGNOFF_TEMPLATE          | OPEN       | TBD      | Yes      | Can start policy review now |
|11 | Create pilot user accounts          | EMS Team               | Account list + role verification               | OPEN       | TBD      | Yes      | After target ready |
|12 | Execute real UAT sessions           | Pilot Coordinator      | Completed checklists + observations            | OPEN       | TBD      | Yes      | After accounts + target |
|13 | Review and approve Go/No-Go         | Faculty Leadership     | Updated UAT_GO_NO_GO_REPORT                    | OPEN       | TBD      | Yes      | After UAT |
|14 | Approve controlled pilot launch     | Faculty Leadership     | Formal approval record                         | OPEN       | TBD      | Yes      | Final gate |

**Status Legend**: OPEN / IN PROGRESS / WAITING APPROVAL / EVIDENCE ATTACHED / CLOSED

All items are currently OPEN because no real pilot target has been designated yet.

---

**End of PILOT_HUMAN_ACTION_TRACKER.md**  
This tracker should be updated after every assignment or evidence attachment.