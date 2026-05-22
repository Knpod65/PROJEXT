# DEVOPS_FACULTY_LAN_DEPLOYMENT_AUDIT.md

**Date**: 2026-05-22

---

## Summary

EMS already has credible deployment assets for a Faculty LAN pilot:

- Dockerfile
- Docker Compose
- Nginx config
- backup cron pattern
- CI workflows

The remaining issues are not “no deployment support exists.” They are:

- hardened environment ownership
- Laravel / route / proxy contract verification
- backup evidence
- final pilot topology decisions

---

## Current Deployment Readiness

### Confirmed assets

- containerized backend runtime via Gunicorn/Uvicorn
- PostgreSQL service definition
- Nginx reverse proxy
- backup cron service
- backend / frontend CI workflows

### Confirmed concerns

- compose defaults still use placeholder credentials until replaced
- backend still binds `0.0.0.0`
- Nginx config is partly conceptual for HTTPS and Faculty LAN route mapping
- no verified Laravel co-hosting topology is committed as fact

---

## Faculty LAN Suitability

### Suitable

- internal single-faculty pilot
- reverse-proxy deployment behind Nginx
- dedicated EMS backend container / process
- separate PostgreSQL instance or DB on faculty infrastructure

### Not yet proven

- exact Laravel mount path
- whether EMS is hosted under `/ems`, another path, or a subdomain
- whether the Faculty LAN reverse proxy should terminate auth bridge traffic
- exact SSL policy inside the faculty network

---

## Recommended Minimum Pilot Topology

1. Faculty Nginx reverse proxy
2. Laravel faculty application
3. EMS backend service
4. EMS frontend static build or SPA served behind the same proxy
5. separate EMS PostgreSQL database
6. backup job owned and scheduled by IT/Ops

If Laravel bridge is used, server-to-server bridge calls must stay internal to Faculty LAN.

---

## Recommended Production Topology

1. dedicated reverse proxy with documented TLS policy
2. isolated EMS backend service
3. isolated EMS PostgreSQL database
4. scheduled backups with restore proof
5. monitoring/log aggregation
6. explicit incident rollback owner
7. documented handoff and change management

---

## Open DevOps Risks

| Risk | Evidence | Priority |
|---|---|---|
| Placeholder env defaults | `.env.example`, compose files | High |
| HTTP-first active nginx block, HTTPS block still commented | `nginx.conf` | Medium |
| Startup still mutates schema and seeds | backend startup behavior | High |
| Laravel route and cookie policy unverified | deployment docs remain draft | Critical |
| No real backup evidence attached yet | operations blockers remain open | High |
| Health endpoint access policy unclear | health router mismatch | Medium |

---

## Logging / Monitoring / Rollback

Positive:

- logging middleware exists
- request IDs exist
- operational docs include logging and monitoring guidance
- rollback and backup docs exist

Gap:

- evidence still needs to move from “documented plan” to “executed and proven on target infrastructure”

---

## Open Questions For IT

1. Where will EMS be mounted relative to Laravel?
2. Will EMS backend be directly reachable or only through reverse proxy?
3. Who owns PostgreSQL provisioning and credentials?
4. What is the SSL expectation for Faculty LAN traffic?
5. Who owns backup scheduling and restore verification?
6. Can Laravel implement the preferred one-time bridge-code endpoint?
7. What system owner signs off on go/no-go?

---

## Audit Judgment

EMS is **ready for deployment rehearsal** and **partially ready for Faculty LAN pilot deployment**, but not ready for a live integrated pilot until the Laravel contract, DB ownership, and operational evidence blockers are closed.
