# PILOT_BLOCKER_DASHBOARD.md

**Date**: 2026-05-22 (Updated — Faculty LAN Target Selected)

---

## Pilot Blocker Status

| # | Blocker | Owner (TBD) | Required Evidence | Current Status | Blocking Level | Next Action | Linked Document |
|---|---|---|---|---|---|---|---|
| 1 | Pilot target environment designated | Faculty Leadership | Decision recorded in SETUP_RECORD | **IN PROGRESS** | Critical | Faculty LAN selected — confirm IT owner and infrastructure details | PILOT_TARGET_DECISION_PACKAGE.md |
| 2 | IT owner assigned | Faculty Leadership | Name + contact confirmed | OPEN | Critical | Assign during decision meeting | PILOT_HUMAN_ACTION_TRACKER.md |
| 3 | Laravel auth contract verified | Laravel owner + IT | LARAVEL_AUTH_CONTRACT_QUESTIONS.md answers confirmed | OPEN | Critical | Send contract questions document to Laravel owner | LARAVEL_AUTH_CONTRACT_QUESTIONS.md |
| 4 | CMU email field name confirmed | Laravel owner | Exact field name (cmu_mail / email / mail / account) verified against code | OPEN | Critical | Part of contract questions response | FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md |
| 5 | session("USS") payload verified | Laravel owner | Exact structure confirmed against real Laravel codebase | OPEN | Critical | Part of contract questions response | FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md |
| 6 | PostgreSQL deployment target verified | IT owner | DB host, port, database name, connection string confirmed | OPEN | High | Confirm after IT owner assigned | LARAVEL_AUTH_CONTRACT_QUESTIONS.md (Section E) |
| 7 | EMS route/mount path decided | EMS + IT | Path agreed (/ems, /exam, subdomain) and configured in Nginx | OPEN | High | Decide after Laravel owner consulted | PILOT_ROUTE_AND_AUTH_MAPPING.md |
| 8 | Auth bridge option selected | EMS + Laravel owner | Option A/B/C/D chosen from integration options matrix | OPEN | High | After contract verified | EMS_LARAVEL_INTEGRATION_OPTIONS.md |
| 9 | cmu_sso.py path decided | EMS team | Decision: activate direct OAuth stub vs. use Laravel bridge vs. both | OPEN | High | After bridge option selected | EMS_AUTH_BRIDGE_DESIGN.md |
| 10 | Production SECRET_KEY configured | IT + Deployment owner | Confirmed configured (yes/no only — no value in doc) | OPEN | Critical | Configure after target provisioned | PRODUCTION_ENV_HANDOFF_CHECKLIST.md |
| 11 | DATABASE_URL configured | IT + DBA | Working connection + health check passed | OPEN | Critical | Provision after target chosen | PRODUCTION_ENV_HANDOFF_CHECKLIST.md |
| 12 | EMS backend deployed | Deployment owner | Health endpoint /health returns OK | OPEN | High | Execute after environment configured | FACULTY_LAN_PILOT_IMPLEMENTATION_PLAN.md |
| 13 | Backup scheduled and tested | IT / Ops | Completed BACKUP_RESTORE_TEST_EVIDENCE | OPEN | High | Execute after deployment | BACKUP_RESTORE_TEST_EVIDENCE.md |
| 14 | DPO sign-off (includes CMU email data flow) | Admin + DPO | Signed DPO template + CMU email data flow reviewed | OPEN | Medium | Notify DPO of CMU email identity usage | DPO_RETENTION_SIGNOFF_TEMPLATE.md |
| 15 | Pilot accounts created | EMS team | Account list + role verification | OPEN | Medium | Create after target ready and auth bridge active | UAT_SESSION_EXECUTION_GUIDE.md |
| 16 | UAT execution | Pilot coordinator | Checklists + observations for all roles | OPEN | Medium | Run after accounts + target confirmed | UAT_ROLE_WORKFLOW_CHECKLISTS.md |
| 17 | Go/No-Go approval | Faculty Leadership | Updated GO/NO-GO report with evidence | OPEN | High | Review after UAT complete | UAT_GO_NO_GO_REPORT.md |

---

## Status Legend

| Status | Meaning |
|---|---|
| OPEN | Not started |
| IN PROGRESS | Active work or partial decision made |
| EVIDENCE ATTACHED | Evidence exists but not formally verified |
| CLOSED | Verified, evidenced, and sign-off obtained |

**Rule**: No blocker may be marked CLOSED without verified evidence. Do not close a blocker based on intent or verbal confirmation alone.

---

## Faculty LAN — New Blockers Added 2026-05-22

When Faculty LAN Server was selected as the pilot target, the following new blockers were added (items 3–9):

| Blocker | Priority |
|---|---|
| Laravel auth contract verified | Critical |
| CMU email field name confirmed | Critical |
| session("USS") payload verified | Critical |
| PostgreSQL deployment target verified | High |
| EMS route/mount path decided | High |
| Auth bridge option selected | High |
| cmu_sso.py path decided | High |

All seven are OPEN as of 2026-05-22.

---

## Next Human Actions Required

1. **Faculty Leadership**: Confirm IT owner contact and assign them to this project.
2. **EMS team**: Send `LARAVEL_AUTH_CONTRACT_QUESTIONS.md` to Laravel owner and IT owner.
3. **Laravel owner**: Fill in contract questions document and return to EMS team.
4. **IT owner**: Confirm server hostname/IP, PostgreSQL target, network scope.
5. **EMS + IT**: Decide EMS route/mount path and auth bridge option.
6. **DPO**: Notify of CMU email data flow for PDPA review.

---

**End of PILOT_BLOCKER_DASHBOARD.md (Updated 2026-05-22 — Faculty LAN target selected)**
