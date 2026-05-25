# FACULTY_WEB_PORTAL_IMPLEMENTATION_ROADMAP.md

**Date**: 2026-05-25

## Stages for Faculty Web Portal Deployment

### Stage 1 — Faculty Web Portal Contract Closure (Critical Gate)
- Goal: Verified answers to all reframed auth, mount path, proxy, and external user questions.
- Tasks: Dispatch packet (already prepared), follow-up, verification against real Laravel codebase.
- Owner: EMS lead + Faculty IT/Laravel owner
- Dependencies: None (can start immediately)
- Acceptance: All high-priority questions marked "Answered + Verified" in updated closure tracker.
- Readiness Impact: Moves Faculty Web Portal integration score significantly (currently ~38/100).

### Stage 2 — Frontend & Backend Web Compatibility Hardening
- Goal: Safe base path, API base URL, proxy header, and cookie configuration support.
- Tasks: Implement VITE_APP_BASE_PATH + VITE_API_BASE_URL (if not already), update docs, add tests, verify local dev unchanged.
- Owner: Frontend + Backend teams
- Dependencies: Stage 1 (exact paths) — safe config work can proceed in parallel
- Acceptance: Build + dev work for both root and example sub-path (/ems); no regressions in standalone demo.

**Status (2026-05-25)**: Frontend portion **COMPLETE**. All root assumptions and direct API strings centralized + validated (see hardening audits and updated subpath build log). Backend proxy/header work remains config-only (no code changes required). Ready for IT path confirmation.

### Stage 3 — PostgreSQL Target + Backup Setup
- Goal: Live PostgreSQL instance under faculty web hosting with tested backup/restore.
- Tasks: Provision DB, configure credentials, run migration dry-runs, execute and evidence backup/restore.
- Owner: Faculty web IT/DBA + EMS ops
- Dependencies: Stage 1 (ownership decisions)
- Acceptance: Connection from staging EMS works; backup evidence attached.

### Stage 4 — Auth Bridge Design Confirmation (Only After Contract)
- Goal: Finalized integration model (Laravel central vs direct, print shop lane, etc.).
- Tasks: Choose model, security review, produce detailed implementation plan.
- Owner: EMS architecture + security + IT
- Dependencies: Stage 1 complete
- Acceptance: Signed design + implementation plan.

### Stage 5 — Staging Deployment Under Faculty Web
- Goal: EMS running in a staging slice of the faculty web environment.
- Tasks: Apply proxy config, deploy frontend under chosen path, backend behind /ems-api (or equivalent), configure monitoring.
- Owner: EMS + Faculty web ops
- Dependencies: Stages 2–4
- Acceptance: All smoke routes work from faculty web URLs; auth fallback (standalone) still works.

### Stage 6 — Browser Smoke + UAT in Web Portal Context
- Goal: Real users (or proxies) test under the actual web portal.
- Tasks: End-to-end testing with CMU accounts (when bridge ready) and print shop lane.
- Owner: EMS + pilot users + IT
- Dependencies: Stage 5
- Acceptance: Signed UAT report with no critical blockers.

### Stage 7 — Controlled Rollout + Governance
- Goal: Limited production-like access with full audit and rollback capability.
- Tasks: Gradual enablement, monitoring, feedback loop, DPO final sign-off if needed.
- Owner: Leadership + EMS + faculty web team
- Dependencies: Stage 6 + all evidence
- Acceptance: Go decision with documented limitations.

### Stage 8 — Full Production Approval (If Desired)
- Requires everything above plus load testing, incident response, full hardening, external audit if mandated.

## Parallel Workstreams (Can Run Early)

- Stakeholder demo feedback processing and decision (use existing post-demo docs)
- Light UI design concept work (using existing handoff package)
- Internal data/import/operational hardening (independent of auth)

**Never start auth bridge code before Stage 1 is complete.**

---
*This roadmap is the current best plan after the pivot to Faculty Web Portal. It will be refined once contract answers arrive.*
