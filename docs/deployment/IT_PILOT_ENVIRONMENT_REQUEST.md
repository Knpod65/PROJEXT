# IT_PILOT_ENVIRONMENT_REQUEST.md

**Date**: 2026-05-22  
**Purpose**: Formal request package to be sent to IT / infrastructure team to provision a pilot runtime environment for the EMS controlled pilot.  
**Intended Recipient**: Faculty IT or central university infrastructure team.

---

## 1. What is EMS?

The Exam Management System (EMS) is a production-grade University Operations Governance Platform for the Faculty of Political Science and Public Administration. It handles:

- Exam scheduling and optimization
- Workload fairness analytics (invigilation & paper distribution)
- Multi-round governance approval workflows
- PDPA-compliant dashboards and exports
- Audit logging and operational intelligence

It is currently at technical readiness 85–99/100 and is prepared for a controlled pilot with 10-20 users.

---

## 2. Why a Pilot Environment is Needed

We have completed all code hardening, security enforcement (`SECRET_KEY`, RBAC, PDPA filtering), runbooks, and UAT preparation packages. However, we cannot collect real operational evidence or run the official pilot until a dedicated runtime environment is available.

---

## 3. Minimum Environment Requirements

- Backend: Python/FastAPI (or Dockerized equivalent)
- Frontend: Vite-built static files (served via nginx or similar)
- Database: PostgreSQL (required — SQLite is not acceptable for pilot)
- Persistent storage for uploaded files and exports
- Ability to run scheduled backups (`pg_dump`)
- Secure storage for `SECRET_KEY` (minimum 50+ characters, never in repo)
- HTTPS or tightly controlled LAN access
- Log access for the deployment owner

---

## 4. Recommended Environment Specifications (for 10-20 pilot users)

- CPU: 2–4 vCPU
- RAM: 4–8 GB
- Storage: 50–100 GB (with room for growth)
- Database: PostgreSQL 14+ with daily automated backups
- Deployment: Docker Compose (preferred) or equivalent orchestration
- Uptime target during pilot: 99% (business hours)

---

## 5. Required Network Access

- Internal faculty LAN access for pilot users (teachers, staff, supervisors)
- Optional: VPN or restricted external access for administrators
- No public internet exposure of admin interfaces unless explicitly approved by DPO

---

## 6. Required Environment Variables (to be provided securely)

The following must be configured (values will be supplied by the EMS team via secure channel):

- `SECRET_KEY` (production strength)
- `DATABASE_URL` (PostgreSQL connection string)
- `ENVIRONMENT=production`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `ALLOWED_ORIGINS`
- `LOG_LEVEL`
- `PDPA_RETENTION_DAYS`

---

## 7. Database Requirements

- Dedicated PostgreSQL database (not shared with other applications during pilot)
- Automated daily backup with minimum 30-day retention
- Ability to perform point-in-time restore for testing

---

## 8. Backup Requirements

- Daily automated `pg_dump` (custom format preferred)
- Offsite or secondary storage for backups
- Documented restore procedure tested at least once before pilot start

---

## 9. Security Requirements

- `SECRET_KEY` never committed to code or logs
- HTTPS or equivalent encryption in transit
- Role-based access control enforced by the application
- Audit logging enabled

---

## 10. Access Control Requirements

- Deployment owner must have:
  - SSH / remote access to the host
  - Ability to view logs
  - Ability to restart services
  - Database admin access (or ability to request it quickly)

---

## 11. Smoke Test Requirements (to be performed after deployment)

The EMS team will run the following after the environment is handed over:
- Backend health endpoint (`/health`)
- Frontend loading
- Login for multiple roles
- Workload analytics dashboards
- Export functionality
- Audit log visibility

---

## 12. Information Requested from IT

Please provide the following so we can proceed with configuration and evidence collection:

1. **Target host / VM name or IP**
2. **Access method** (SSH key, VPN, jump host, etc.)
3. **Database endpoint / connection details** (we will supply the schema and migrations)
4. **Backup method and storage location**
5. **Allowed users / network ranges** for pilot access
6. **Responsible IT contact person** during pilot
7. **Expected environment readiness / deployment date**

---

**Response Template for IT** (please reply with answers):

- Target Host: _______________________________
- Access Method: _______________________________
- Database: _______________________________
- Backup Strategy: _______________________________
- Allowed Networks/Users: _______________________________
- IT Contact: _______________________________
- Expected Ready Date: _______________________________

---

**End of IT_PILOT_ENVIRONMENT_REQUEST.md**  
This document is ready to be sent to the infrastructure team. No secrets are included.