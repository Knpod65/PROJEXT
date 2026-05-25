# DEMO_SCOPE_AND_BOUNDARIES.md

**Date**: 2026-05-22
**Status**: DRAFT — ready for stakeholder review before demo delivery
**Purpose**: Define exactly what this demo is and is not. Official boundary document for anyone presenting, training, or recording a demo session.

---

## 1. Demo Purpose

This demo is a **controlled internal demonstration** of the EMS (Exam Management System) application. Its purpose is to:

1. Show the EMS operational capability: schedule management, submission workflow, supervisor assignment, invigilation planning.
2. Show the dashboard intelligence layer: role-aware dashboards, workload signals, alerts, and health summaries.
3. Show role-based experience: admin, staff, teacher, and governance views from the same system.
4. Show governance and audit readiness: audit explorer, governance cockpit, operational health page.
5. Show visual consistency and humanization effort: Thai-language pages, i18n coverage, humanization screenshot atlas.
6. Show import/export capabilities where stable.

---

## 2. What the Demo IS Allowed to Show

| Capability | How |
|-----------|-----|
| EMS local login (username + password) | Standard EMS auth — local dev accounts only |
| Role-aware navigation | Admin, Staff, Teacher, Governance views |
| Dashboard overview | Platform metrics, status cards |
| Workload and duty analytics | Per-person, per-day, fairness signals |
| Schedule review | Exam schedule listing and filtering |
| Submission workflow | Submission listing and state labels |
| Governance cockpit | Governance dashboard view |
| Operational health | System health and readiness status |
| Audit explorer | Audit log query and review |
| Import/export surfaces | Import page, exports center (if stable in build) |
| Screenshot atlas / role manuals | Humanization package pages |
| Screenshots from the screenshot-atlas | Pre-captured image files |

---

## 3. What the Demo Must NOT Claim

The demo environment is **NOT** and **does not claim to be**:

- [ ] **Production deployment** — no real production environment, no production PostgreSQL, no production secrets.
- [ ] **Faculty LAN pilot live** — the Faculty LAN integration and Laravel auth bridge are in design stage, not implemented.
- [ ] **Laravel/CMU auth bridge complete** — the Laravel auth contract is unverified; no bridge code has been written.
- [ ] **DPO sign-off complete** — PDPA review is pending.
- [ ] **Backup/restore proven** — backup runbook exists; restore test evidence is pending.
- [ ] **Full UAT complete** — UAT checklists exist but have not been executed with real users.
- [ ] **Go/No-Go approval issued** — Go/No-Go conditions are documented but not met.
- [ ] **Real CMU identity integration** — demo uses local account-based login only.
- [ ] **Production-grade security** — local dev SECRET_KEY and SQLite fallback are in use.

---

## 4. Demo Constraints

| Constraint | Detail |
|-----------|--------|
| Environment | Local development environment (SQLite, local FastAPI + React) |
| Data | Demo/seed data only — no real personal data, no real CMU records |
| Accounts | Local EMS demo accounts with dev passwords only |
| Network | Not on Faculty LAN; not externally accessible |
| Backend | Local FastAPI on port 8000 |
| Frontend | Local React dev server or built static files |
| Secrets | All values in `.env.local` (dev defaults only) |
| i18n | Bilingual (Thai + English) — some keys may show untranslated fallback |

---

## 5. Demo Decision

**IN PROGRESS** — final decision pending route validation.

| Manifestation | Required Before Changing to GO |
|---------------|-------------------------------|
| GO FOR INTERNAL DEMO | All demo-critical routes render; no crash on main journey; limitations documented |
| GO FOR STAKEHOLDER DEMO WITH CONDITIONS | Above + stakeholder briefing on limitations; demo script available; known broken routes listed |
| NO-GO | Critical route crashes; key demo page unreachable; limitations unclear to presenters |

---

## 6. Demo Duration Options

| Duration | What to Show | What to Skip |
|----------|-------------|-------------|
| **5 min** | Login + Admin dashboard + one role example | Workload deep-dive, governance cockpit, import/export |
| **15 min** | 5-minute core + Staff role + Workload analytics + Submission flow | Governance cockpit detail, operational health, audit explorer detail |
| **30 min** | Full user journey (all roles + all stages) + Q&A prep | Nothing skipped; all demo-ready routes covered |

---

## 7. Demo Environment Quick Reference

| Item | Local Value (demo) |
|------|-------------------|
| Backend URL | `http://localhost:8000` |
| Frontend URL | `http://localhost:3000` (dev) or `http://localhost:8000` (proxy) |
| DB | SQLite (`backend/ems.db`) |
| ENV | `development` |
| SECRET_KEY | `dev-only-secret-change-in-production-minimum-32-chars` |
| CRON_SECRET | `dev-cron-secret-change-in-production` |
| Auth | Local username + password (no CMU OAuth) |

---

**End of DEMO_SCOPE_AND_BOUNDARIES.md**
