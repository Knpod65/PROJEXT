# PILOT_TARGET_DECISION_PACKAGE.md

**Date**: 2026-05-22 (Updated — Faculty LAN selected)
**Purpose**: Decision-support package for pilot environment selection and integration planning.
**Status**: DECISION MADE — Faculty LAN Server selected in principle. Pending infrastructure confirmation and Laravel/CMU auth contract verification.

---

## 1. Current Status Summary

As of HEAD `8e75db3` (updated 2026-05-22):

- **Pilot target environment**: **SELECTED — Faculty LAN Server (Option B)**
- **Institutional stack**: PHP / Laravel / PostgreSQL + EMS FastAPI + React frontend
- **Identity basis**: CMU email / faculty Laravel auth / CMU OAuth
- **Integration status**: PENDING — Laravel/CMU auth contract not yet verified

**Original blockers** (4 remain open): SECRET_KEY, DATABASE_URL, Backup/Restore, DPO sign-off.

**New blockers added** (Faculty LAN-specific): Laravel auth contract, CMU email field, session("USS") payload, PostgreSQL deployment target, EMS route/mount path, auth bridge option, cmu_sso.py path decision.

See `PILOT_BLOCKER_DASHBOARD.md` for the full live blocker list.

**Conclusion**: The pilot environment direction is decided. Progress is now blocked on the Laravel/CMU auth contract and IT infrastructure confirmation.

---

## 2. Candidate Pilot Environment Options

### Option A — Local Internal Demo Machine (Development Workstation)

**Description**: Run the pilot on the same or a dedicated local machine used for development.

**When Suitable**: Rehearsal, internal demo, very early validation only.

**Pros**:
- Fastest to set up
- No network or IT coordination needed
- Easy to iterate

**Cons**:
- Not suitable for real PDPA-controlled pilot data
- No separation between development and pilot
- Cannot be used for faculty-wide or official pilot

**Required Setup**: Docker or native Python/Node, local PostgreSQL, local `.env`

**Risk**: HIGH (data isolation, security, credibility of pilot results)

**Evidence Possible**: Local rehearsal screenshots and smoke tests only. Not countable as production pilot evidence.

**Recommendation**: Use only for rehearsal. Not recommended as official pilot target.

---

### Option B — Faculty LAN Server / On-Premise Machine

**Description**: Dedicated server or workstation inside the faculty network (Political Science and Public Administration).

**When Suitable**: Controlled single-faculty pilot (10-20 users) as described in `PILOT_ROLLOUT_FINAL_REPORT.md`.

**Pros**:
- Matches the planned "single faculty" scope
- Good PDPA control (data stays inside faculty)
- Easier IT approval within faculty
- Can use existing faculty backup policies

**Cons**:
- Requires faculty IT coordination
- Hardware must be provisioned or repurposed
- Backup responsibility falls on faculty IT

**Required Setup**:
- PostgreSQL instance
- Docker or direct deployment
- Secure storage for `SECRET_KEY`
- LAN-only or VPN access

**Network Requirements**: Internal LAN, restricted external access if needed.

**Recommended For**: Official controlled faculty pilot (preferred path per existing rollout plan).

---

### Option C — Docker Host / VM (Dedicated or Shared)

**Description**: A dedicated or semi-dedicated VM or physical host running Docker Compose or similar orchestration.

**When Suitable**: When repeatable, isolated environments are needed for pilot + future staging.

**Pros**:
- High repeatability
- Easy backup/restore via volumes
- Clean separation from production
- Good for controlled pilot + later expansion

**Cons**:
- Requires someone to manage the host/VM
- Initial setup effort higher than pure local

**Required Setup**:
- Docker + Docker Compose
- Persistent volume for PostgreSQL
- `.env` management
- Scheduled backup script

**Backup/Restore Feasibility**: High (volume snapshots + `pg_dump` easy to script).

**Recommendation**: Strong option for repeatable, auditable pilot.

---

### Option D — Cloud VM (AWS, Azure, GCP, etc.)

**Description**: Pilot instance running in a public cloud provider.

**When Suitable**: When on-premise hardware is not available or when external access is required.

**Pros**:
- Fast provisioning
- Managed database options (RDS, Cloud SQL)
- Scalable
- Good monitoring tools

**Cons**:
- PDPA / data residency concerns (Thai university data)
- Cost (even for small pilot)
- Additional security hardening required
- IT/faculty approval may be harder

**Security Considerations**: VPC, security groups, encrypted storage, IAM, secret management.

**PDPA Considerations**: Must confirm data residency and access controls with DPO.

**Recommendation**: Viable only if PDPA and budget concerns are cleared. Lower priority than on-premise options for this pilot.

---

### Option E — Existing University / Faculty Infrastructure

**Description**: Use an existing production or staging environment already managed by central university IT.

**When Suitable**: When the faculty already has a shared platform or the university wants to run EMS under central governance.

**Pros**:
- Professional operations
- Existing backup, monitoring, security
- Lower setup effort for faculty

**Cons**:
- Longer approval chain
- Less control for the faculty pilot team
- May have stricter change processes

**Coordination Requirements**: Formal request to central IT, SLA discussion, change control.

**IT Approval Requirements**: High.

**Recommendation**: Good long-term target, but may slow down the initial controlled pilot.

---

## 3. Decision Matrix

| Option                        | Setup Difficulty | Security Readiness | Backup Readiness | Network Accessibility | PDPA Risk | IT Dependency | Pilot Suitability (10-20 users) | Recommendation |
|-------------------------------|------------------|--------------------|------------------|-----------------------|-----------|---------------|-----------------------------------|----------------|
| A. Local Demo Machine         | Very Low         | Low                | Low              | Local only            | High      | None          | Not suitable                      | Rehearsal only |
| B. Faculty LAN Server         | Medium           | Medium-High        | Medium           | LAN + restricted      | Low       | Faculty IT    | Recommended                       | Preferred for controlled pilot |
| C. Docker Host / VM           | Medium           | High               | High             | Configurable          | Medium    | Moderate      | Highly recommended                | Strong alternative |
| D. Cloud VM                   | Low-Medium       | High (with effort) | High             | Public / restricted   | High      | Low           | Possible with approvals           | Only if on-prem unavailable |
| E. Existing University Infra  | Low              | High               | High             | Depends on SLA        | Low       | High          | Good for later phases             | Long-term target |

---

## 4. Recommended Default Path

**For the initial controlled pilot (single faculty, 10-20 users)**:

1. **Primary recommendation**: Option B (Faculty LAN Server) or Option C (Docker/VM on faculty infrastructure).
2. Use Option A (local) **only** for internal rehearsal and deployment practice while waiting for the real target.
3. Cloud (Option D) should be considered only after PDPA and budget review.
4. Option E is suitable for post-pilot expansion.

**Rationale**: Matches the scope defined in `PILOT_ROLLOUT_FINAL_REPORT.md` and keeps data within faculty control for the initial PDPA-sensitive pilot.

---

## 5. Decision Record (Updated 2026-05-22)

| Field | Value |
|---|---|
| Selected Option | B — Faculty LAN Server |
| Selected Host / Machine | TBD (IT to confirm) |
| Responsible IT Person | TBD |
| Responsible System Owner | TBD |
| Institutional Stack | PHP / Laravel / PostgreSQL + EMS |
| Identity Source | CMU email / Faculty Laravel auth |
| Target Pilot URL | TBD |
| Network Scope | Faculty LAN / controlled access |
| Expected Pilot Users | 10–20 |
| Decision Date | 2026-05-22 |
| Approval Status | Selected in principle — pending IT confirmation |

**Rationale for Option B**:
- Aligns with faculty web and existing Laravel/CMU auth infrastructure
- Supports LAN-controlled pilot (data stays inside faculty)
- Compatible with PHP/Laravel/PostgreSQL environment
- Allows integration with existing CMU email identity
- Matches the PDPA-controlled single-faculty scope defined in PILOT_ROLLOUT_FINAL_REPORT.md

---

## 6. Remaining Decisions (Added 2026-05-22)

The following decisions must be made before integration can begin:

| Decision | Options | Status |
|---|---|---|
| EMS mount route | /ems, /exam, separate subdomain | OPEN |
| Auth bridge option | A (gateway), B (code exchange), C (proxy header), D (separate login) | OPEN |
| PostgreSQL DB ownership | Shared with faculty web vs. separate EMS DB | OPEN |
| Backup owner | IT vs. EMS team | OPEN |
| DPO reviewer for CMU email data flow | TBD | OPEN |
| Pilot account list | Admin, staff, teacher, supervisor, governance | OPEN |
| cmu_sso.py path | Activate direct OAuth vs. use Laravel bridge vs. both | OPEN |

See `EMS_LARAVEL_INTEGRATION_OPTIONS.md` for the auth bridge analysis.
See `LARAVEL_AUTH_CONTRACT_QUESTIONS.md` for the IT/Laravel owner questions.
See `FACULTY_LAN_PILOT_IMPLEMENTATION_PLAN.md` for the staged implementation plan.

---

**End of PILOT_TARGET_DECISION_PACKAGE.md (Updated 2026-05-22)**
Faculty LAN Server selected. No values fabricated. All remaining items require IT and Laravel owner confirmation.