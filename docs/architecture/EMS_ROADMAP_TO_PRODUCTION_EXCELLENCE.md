# EMS_ROADMAP_TO_PRODUCTION_EXCELLENCE.md

**Date**: 2026-05-22

---

## Stage 1 - Faculty LAN Contract Verification

- **Goal**: turn Laravel / Faculty LAN assumptions into verified facts
- **Tasks**: answer route, session, token, cookie, DB, mount-path, and logout questions; assign IT and Laravel owners
- **Owners**: Laravel owner, IT owner, EMS lead
- **Dependencies**: faculty-side code access and stakeholder response
- **Deliverables**: completed `LARAVEL_AUTH_CONTRACT_QUESTIONS.md`, bridge option decision, mount-path decision
- **Acceptance Criteria**: no major auth or routing assumptions remain marked TBD

## Stage 2 - Auth Bridge Implementation

- **Goal**: implement the selected verified bridge strategy safely
- **Tasks**: build the agreed bridge flow, keep EMS DB-authoritative roles, log bridge auth events, preserve fallback login during pilot
- **Owners**: backend owner, Laravel owner
- **Dependencies**: Stage 1 complete
- **Deliverables**: working bridge code, smoke validation, rollback plan
- **Acceptance Criteria**: user can authenticate through verified flow without exposing CMU token to frontend

## Stage 3 - PostgreSQL Deployment Setup

- **Goal**: establish the real EMS database target for Faculty LAN
- **Tasks**: provision separate EMS DB, define credentials, confirm ownership, confirm migration procedure
- **Owners**: IT / DBA, backend owner
- **Dependencies**: Stage 1 decisions
- **Deliverables**: working `DATABASE_URL`, DB ownership record, migration procedure
- **Acceptance Criteria**: EMS runs against real PostgreSQL target and no SQLite fallback is used on pilot host

## Stage 4 - Pilot Environment Deployment

- **Goal**: stand up EMS on the actual Faculty LAN target
- **Tasks**: configure Nginx/reverse proxy, deploy backend/frontend, set secrets, validate health and route mounting
- **Owners**: IT owner, deployment owner
- **Dependencies**: Stages 1-3
- **Deliverables**: deployed pilot environment, validated probe endpoints, documented URL/path
- **Acceptance Criteria**: target environment is reachable and basic smoke checks pass

## Stage 5 - Backup / Restore Evidence

- **Goal**: move backup strategy from documentation to proof
- **Tasks**: run backup, run restore, record timings and evidence
- **Owners**: IT / Ops
- **Dependencies**: Stage 4 complete
- **Deliverables**: completed restore evidence pack
- **Acceptance Criteria**: restore succeeds and evidence is attached to the blocker register

## Stage 6 - UAT Execution

- **Goal**: validate real user workflows on target infrastructure
- **Tasks**: create accounts, run role-based UAT sessions, collect observations, log defects
- **Owners**: pilot coordinator, EMS team, faculty users
- **Dependencies**: Stages 2-5
- **Deliverables**: completed UAT checklists, observations, go/no-go input
- **Acceptance Criteria**: at least one full role coverage wave is executed with no critical unresolved blockers

## Stage 7 - Controlled Pilot

- **Goal**: run limited real faculty usage safely
- **Tasks**: launch to agreed pilot cohort, monitor logs, support users, capture incidents
- **Owners**: faculty owner, EMS team, IT owner
- **Dependencies**: Stage 6
- **Deliverables**: pilot launch record, issue tracker, monitoring notes
- **Acceptance Criteria**: controlled pilot operates without critical security, auth, or data-loss incidents

## Stage 8 - Post-Pilot Refactor

- **Goal**: remove confusion and tighten maintainability after usage evidence exists
- **Tasks**: archive unused legacy pages, consolidate duplicate surfaces, reduce route/doc drift
- **Owners**: frontend owner, backend owner
- **Dependencies**: usage evidence from pilot
- **Deliverables**: cleanup pass, updated docs, reduced duplicate surface area
- **Acceptance Criteria**: canonical runtime surfaces are clear and stale legacy pages are retired

## Stage 9 - Production Hardening

- **Goal**: harden runtime behavior and governance beyond pilot tolerance
- **Tasks**: remove startup mutation behavior, unify hardening policy, add stronger UI/integration tests, tighten monitoring and incident response
- **Owners**: backend owner, frontend owner, IT/Ops
- **Dependencies**: post-pilot priorities confirmed
- **Deliverables**: hardening release and validation evidence
- **Acceptance Criteria**: production risks in this audit are either fixed or explicitly accepted by owners

## Stage 10 - Full Institutional Rollout

- **Goal**: expand beyond the controlled pilot with operational confidence
- **Tasks**: scale user onboarding, finalize training, refresh manuals/screenshots, widen support model, monitor adoption
- **Owners**: faculty leadership, EMS product/engineering owners, IT/Ops
- **Dependencies**: successful Stage 9 hardening
- **Deliverables**: rollout package, support plan, institutional sign-off
- **Acceptance Criteria**: production deployment is approved and supported as a stable institutional system
