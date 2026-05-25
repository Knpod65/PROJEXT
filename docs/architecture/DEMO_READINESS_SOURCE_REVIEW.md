# DEMO_READINESS_SOURCE_REVIEW.md

**Date**: 2026-05-22
**Purpose**: Record which source-of-truth docs were reviewed and which findings matter for demo vs. production.

---

## 1. Source Docs Read

| Doc | Read | Demo Relevance | Production/Blocking |
|-----|------|---------------|-------------------|
| `EMS_FULL_SYSTEM_SUPERIOR_DEVELOPER_REVIEW.md` | Yes | HIGH — UX gaps, load errors, screenshot issues | CRITICAL — Laravel auth unverified, production not ready |
| `PILOT_BLOCKER_DASHBOARD.md` | Yes | HIGH — block list feeding what must not be claimed | CRITICAL — all pilot blockers remain open |
| `UAT_GO_NO_GO_REPORT.md` | Yes | HIGH — current status GO WITH CONDITIONS | — |
| `PILOT_ENVIRONMENT_SETUP_RECORD.md` | Yes | MEDIUM — target selected, config TBD | HIGH |
| `LOCAL_REHEARSAL_PREFLIGHT_REPORT.md` | Yes | MEDIUM — compile + build pass locally | — |
| `SCREENSHOT_CAPTURE_REPORT.md` | Yes | HIGH — identifies captured errors/fix needs | — |
| `EMS_MISSING_WORK_REGISTER.md` | Yes | MEDIUM — missing work track | HIGH |
| `UNUSED_AND_DUPLICATE_FILE_AUDIT.md` | Yes | LOW — legacy pages, not demo-stoppers | LOW |
| `FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md` | Yes | HIGH — demo must NOT claim auth bridge complete | CRITICAL |
| `FACULTY_LAN_PILOT_IMPLEMENTATION_PLAN.md` | Yes | MEDIUM — stage roadmap for demo context | HIGH |

**Not found / skipped** (not on-disk, no fabrication):
- `EMS_SUPERIOR_DEVELOPER_SCORECARD.md` — MISSING
- `FRONTEND_SUPERIOR_ENGINEER_AUDIT.md` — MISSING
- `BACKEND_SUPERIOR_ENGINEER_AUDIT.md` — MISSING
- `UX_UI_HUMANIZATION_AUDIT.md` — MISSING
- `UI_UX_CONSISTENCY_REPORT.md` — MISSING

---

## 2. Findings That Matter for Demo

### 2a. Confirmed Demo-Blocking Issues (from Screenshot Report)

| Route | Issue | Source |
|-------|-------|--------|
| `/admin-intelligence-dashboard` | Renders load-error state; `dashboard.admin.loadErrorTitle` missing i18n | SCREENSHOT_CAPTURE_REPORT |
| `/analytics` (Executive) | Returns `Not Found` from backend | SCREENSHOT_CAPTURE_REPORT |
| `/platform-config` | Stuck in loading state | SCREENSHOT_CAPTURE_REPORT |
| `/governance` | Untranslated i18n keys (6 governance.* keys) | SCREENSHOT_CAPTURE_REPORT |
| Status labels | `status.submitted`, `status.approved`, `status.rejected`, etc. missing from i18n | SCREENSHOT_CAPTURE_REPORT |

These are **real UI gaps that will be visible during a demo** and must be resolved or acknowledged before stakeholder presentation.

### 2b. Missing i18n Keys

| Key | Context |
|-----|---------|
| `dashboard.admin.loadErrorTitle` | Admin intelligence load-error title |
| `governance.healthScore` | Governance cockpit |
| `governance.blockers` | Governance cockpit |
| `governance.overrides` | Governance cockpit |
| `governance.rollbacks` | Governance cockpit |
| `governance.escalations` | Governance cockpit |
| `governance.pendingApprovals` | Governance cockpit |
| `status.submitted` | Submission status label |
| `status.approved` | Submission status label |
| `status.rejected` | Submission status label |
| `status.released` | Swap/exam status label |
| `status.swap_open` | Swap status label |
| `status.confirmed` | Check-in status label |

Missing i18n keys show the raw key string to users — this looks broken in demos.

### 2c. Routes That Rendered as Empty State (Acceptable but Needs Data)

These routes rendered in the local pass but with mostly empty-state content:

- `/workload-duty-analytics`
- `/duty-workload`
- `/my-workload`
- `/attendance`
- `/audit-explorer`

Empty-state UX is acceptable for demo **if**: (a) data is seeded for the demo session, or (b) the empty state is visually clean with helpful instructional text.

---

## 3. Production-Only Findings (Can Defer)

These affect production readiness but are NOT demo blockers for a controlled local/stakeholder demo:

| Finding | Why Deferred for Demo |
|---------|----------------------|
| Laravel auth contract unverified | Demo uses local EMS auth, not CMU OAuth |
| PostgreSQL target not provisioned | Demo uses local SQLite |
| SECRET_KEY not hardened | Demo uses dev SECRET_KEY locally |
| Backup/restore not proven | Demo corpus; not intended for production data |
| DPO sign-off open | Demo data is synthetic |
| Login token in response body | Acceptable for demo; has low cryptographic risk locally |
| /health access policy mismatch | Documented but safe for local demo |
| UNUSED legacy pages | Not breaking demo routes; archive later |
| cmu_sso path decision | Not used in demo |

---

## 4. Local Rehearsal Evidence (Already Passed)

From `LOCAL_REHEARSAL_PREFLIGHT_REPORT.md`:
- `compileall backend` → PASSED
- `npm run build` → PASSED (~1.3 sec, known large chunk warning)

---

## 5. What Must NOT Be Shown as Complete During Demo

- [ ] Faculty LAN deployment
- [ ] Laravel CMU auth integration
- [ ] PostgreSQL pilot database
- [ ] DPO sign-off
- [ ] Backup/restore proof
- [ ] Production SECRET_KEY
- [ ] Full UAT completion
- [ ] Real user accounts (CMU email)
- [ ] Go/No-Go approval

Demo must be honest about all of the above being in progress.

---

## 6. Key Gaps to Fix Before Demo

Based on source-review, items to address in order:

1. **Missing i18n keys** — need to be added so raw key strings don't appear during demo
2. **`/analytics` (Executive) 404** — need to verify the backend endpoint exists
3. **`/admin-intelligence-dashboard` load error** — need to verify backend data source
4. **`/platform-config` loading state** — need to verify it resolves or is hidden pending data
5. **`/governance` untranslated keys** — add governance i18n keys
6. **Demo data / seed setup** — review and confirm demo accounts and data exist in local DB
7. **Demo route smoke map** — validate which pages actually load

---

**End of DEMO_READINESS_SOURCE_REVIEW.md**
