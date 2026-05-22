# PILOT_COMMUNICATION_PACKAGE.md

**Date**: 2026-05-22  
**Purpose**: Ready-to-use messages for different stakeholders.

---

## 1. Message to Faculty Executive / Admin

**Subject**: Request for Pilot Environment Decision – EMS Controlled Pilot

Dear [Faculty Executive / Admin],

The Exam Management System (EMS) has reached full technical and documentation readiness for a controlled pilot (10-20 users, single faculty).

We have completed:
- All core functionality, security hardening, and PDPA controls
- Comprehensive UAT preparation and operational evidence templates
- A full decision support package (options, IT request, launch sequence, blocker dashboard)

**The only remaining blocker** is the selection of a concrete pilot runtime target environment.

We have prepared:
- Executive Decision Brief
- IT Handoff Action Pack
- Environment Option Comparison Matrix
- Full launch sequence and human action tracker

We request a short decision meeting to select the pilot target (recommended: Faculty LAN Server or Docker/VM), assign the IT owner, and confirm the pilot timeline.

Please let us know a convenient time for the decision meeting.

Best regards,  
[EMS Project Team]

---

## 2. Message to IT / Infrastructure

**Subject**: Request to Provision Pilot Environment for EMS – Controlled Faculty Pilot

Dear IT Team,

We are preparing to launch a controlled pilot of the Exam Management System (EMS) for the Faculty of Political Science and Public Administration (10-20 users).

We have attached:
- IT Pilot Environment Request
- IT Handoff Action Pack
- Minimum technical requirements

We need your help to provision a suitable pilot environment (preferably a dedicated or Docker-capable host with PostgreSQL).

Key requirements:
- PostgreSQL database
- Support for secure SECRET_KEY and environment variables
- Daily backup capability
- LAN access for pilot users

Please review the attached documents and confirm a target host and timeline.

Thank you,  
[EMS Deployment Owner]

---

## 3. Message to DPO / Data Protection Reviewer

**Subject**: Request for Retention Policy Review and Sign-off – EMS Pilot

Dear DPO,

The EMS platform is preparing for a controlled pilot.

We have prepared:
- Retention policy review sections
- Backup, audit log, and export retention templates
- DPO Sign-off Template

We request your review of the current retention periods, backup policy, and audit/export handling for PDPA compliance.

Please use the attached DPO_RETENTION_SIGNOFF_TEMPLATE.md to provide your feedback or formal sign-off.

Thank you for your support,  
[Admin / EMS System Owner]

---

**End of PILOT_COMMUNICATION_PACKAGE.md**  
These messages are ready to be customized with actual names and sent.