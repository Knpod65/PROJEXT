# PILOT_ENVIRONMENT_SETUP_RECORD.md

**Date**: 2026-05-22 (Updated — Faculty LAN Target Selected)
**Purpose**: Master record of pilot environment decision and readiness status.

---

## Pilot Environment Decision Status

**Current Status**: **TARGET SELECTED — Faculty LAN Server (pending technical contract)**

The pilot target environment has been designated as the Faculty LAN Server. The faculty institutional stack is PHP/Laravel/PostgreSQL, with CMU email as the identity basis via CMU OAuth. EMS (FastAPI backend + React frontend) will be deployed alongside or integrated with the existing faculty Laravel web system.

**Integration status**: PENDING — Laravel/CMU auth contract not yet verified.

**Previous status**: BLOCKED — Pilot target environment not yet designated (resolved 2026-05-22)

---

## Selected Pilot Environment

| Field | Value |
|---|---|
| Environment Type | Faculty LAN Server (Option B from PILOT_TARGET_DECISION_PACKAGE.md) |
| Stack | PHP / Laravel / PostgreSQL + EMS FastAPI backend + React frontend |
| Identity Source | CMU email / faculty Laravel auth / CMU OAuth |
| Integration Status | PENDING — Laravel/CMU auth contract not yet verified |
| Faculty LAN server hostname/IP | TBD |
| Responsible IT owner | TBD |
| Laravel owner | TBD |
| PostgreSQL owner | TBD |
| EMS deployment owner | TBD |
| Network scope | Faculty LAN / controlled access |
| Pilot URL | TBD |
| CMU auth callback owner | TBD |
| Session contract verified | NO |
| Role mapping verified | NO |
| Decision date | 2026-05-22 |
| Approval status | Selected in principle — pending infrastructure confirmation |

---

## Links to Decision and Integration Package

- Executive Brief: `docs/operations/EXECUTIVE_PILOT_DECISION_BRIEF.md`
- Full Option Analysis: `docs/operations/PILOT_TARGET_DECISION_PACKAGE.md`
- Quantitative Matrix: `docs/operations/PILOT_ENVIRONMENT_DECISION_MATRIX.md`
- IT Handoff Pack: `docs/deployment/IT_HANDOFF_ACTION_PACK.md`
- Human Action Tracker: `docs/operations/PILOT_HUMAN_ACTION_TRACKER.md`
- Communication Templates: `docs/operations/PILOT_COMMUNICATION_PACKAGE.md`
- Meeting Pack: `docs/operations/PILOT_DECISION_MEETING_PACK.md`
- Laravel Auth Integration Spec: `docs/deployment/FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md`
- Integration Options Matrix: `docs/deployment/EMS_LARAVEL_INTEGRATION_OPTIONS.md`
- Auth Contract Questions for IT: `docs/deployment/LARAVEL_AUTH_CONTRACT_QUESTIONS.md`
- EMS Auth Bridge Design: `docs/architecture/EMS_AUTH_BRIDGE_DESIGN.md`
- Pilot Route & Auth Mapping: `docs/deployment/PILOT_ROUTE_AND_AUTH_MAPPING.md`
- Faculty LAN Pilot Implementation Plan: `docs/deployment/FACULTY_LAN_PILOT_IMPLEMENTATION_PLAN.md`
- EMS Current Auth Flow Audit: `docs/architecture/EMS_CURRENT_AUTH_FLOW_AUDIT.md`

---

## Remaining Information Required to Proceed

- [x] Selected environment type — Faculty LAN Server
- [ ] Specific host/server/VM designation (TBD from IT)
- [ ] Network scope confirmed by IT
- [ ] Deployment owner assigned
- [ ] Database owner assigned
- [ ] Backup owner assigned
- [ ] DPO reviewer assigned
- [ ] Pilot user group defined
- [ ] Expected pilot start date
- [ ] Laravel auth contract verified (session("USS") payload, cmu_at handling, CMU email field)
- [ ] EMS mount route decided (/ems, /exam, or subdomain)
- [ ] PostgreSQL DB ownership confirmed (shared or separate)
- [ ] Auth bridge option selected (A, B, C, or D — see EMS_LARAVEL_INTEGRATION_OPTIONS.md)

---

## Current Blocker Status

## 2026-05-25 Auth Design Addendum

Observed new evidence:

- Faculty login endpoint observed at `https://account.pol.cmu.ac.th/oauth/login`
- Observed `ServiceUrl` callback points to `https://portal.mis.pol.cmu.ac.th/oauth/callback`
- Print-shop users may need controlled access without CMU email

Implication for the environment record:

- Faculty LAN remains the correct target in principle
- EMS must now plan for two auth lanes:
  - verified CMU / POLSCI users
  - external print-shop / partner users
- Neither lane may be implemented until its contract gates are satisfied

Additional information required to proceed:

- [ ] POLSCI callback payload contract verified
- [ ] `ServiceUrl` strategy verified
- [ ] External print-shop identity owner selected
- [ ] Print-shop access scope approved
- [ ] PostgreSQL target confirmed for the chosen auth rollout

---

See `docs/operations/PILOT_BLOCKER_DASHBOARD.md` and `docs/operations/PILOT_HUMAN_ACTION_TRACKER.md` for the live status of all blockers.

Environment target is now IN PROGRESS. All Laravel/CMU auth contract items remain OPEN.

---

**End of PILOT_ENVIRONMENT_SETUP_RECORD.md (Updated 2026-05-22 — Faculty LAN target selected)**
