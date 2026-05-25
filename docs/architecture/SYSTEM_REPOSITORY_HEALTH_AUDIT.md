# SYSTEM_REPOSITORY_HEALTH_AUDIT.md

**Date**: 2026-05-25  
**Audit**: EMS 100% SYSTEM READINESS AUDIT  
**Source**: git ls-files, Get-ChildItem counts, targeted globs, prior architecture audits (2026-05-22)

---

## 1. Current Repository Structure Summary

**Real root**: C:\Users\DELL\Desktop\PROJEXT\opt\ems_system (confirmed)

**Working tree**: 1 modified file (`backend/requirements.txt` — tracked change, not untracked). No other modifications or untracked files reported in pre-flight.

**Total on-disk files** (approx): ~17,796 (heavily inflated by `backend/.venv/`, `frontend/node_modules/`, `.git/`, design assets, caches).

**Tracked source files** (meaningful, excluding venvs/node_modules/__pycache__):
- Backend Python: **333** *.py
- Frontend: **244** *.ts + *.tsx (in src/)
- Documentation: **293** *.md (in docs/)

**Git branch state**:
- Current: `main` @ 959752d (origin/main)
- Other: `wip/ems-orphan-services-transfer` @ 39f752c (untouched per rules)

---

## 2. Major Runtime Folders

| Folder | Role | Approx Size (source) | Notes |
|--------|------|----------------------|-------|
| `backend/` | FastAPI + SQLAlchemy core | 333 py files | 30+ routers, 178 services (per prior audit), 20 repositories, models.py, seed.py, multiple migrate_*.py, import_v2/, policies/, events/, serializers/, config/, tests/ |
| `frontend/` | React 18 SPA (Vite) | 244 ts/tsx | App.tsx, role-aware routing, AppShell, auth store, i18n (full en/th), services/, hooks/domain/, components/layout + feature, config/navigation.ts, legacy/V2 coexistence |
| `docker-compose*.yml` + `Dockerfile` | Containerized deployment | 3 compose + 1 Dockerfile | Variants for dev/local/prod; Gunicorn/Uvicorn + Nginx patterns referenced in audits |

---

## 3. Documentation Folders (High Volume)

- `docs/architecture/` — 100+ files: superior developer reviews, scorecards, hardening triage, Laravel gate docs, many historical D3/D4/D5/modernization passes, prototypes/
- `docs/deployment/` — Laravel contract questions, owner handoff packages, Faculty LAN pilot plans, IT handoff
- `docs/operations/` — 50+ : pilot blocker dashboards, UAT scripts/guides, demo scope/route/journey, backup/DPO templates, pilot execution evidence, error escalation, disaster recovery
- `docs/humanization/` — cognitive load audit, humanization strategy, journeys (workload-balancing), dashboard-guides (many), screenshot evidence alignment
- `docs/design/claude-design-handoff-package/` — full handoff bundle for redesign (master prompt, brief, context, screenshots manifest)
- `docs/exam_operation/` — modernization plans, gap analysis, workflow/calendar engines
- Root-level historical reports (2026-04): IMPLEMENTATION_STATUS, PHASE_2_PROGRESS, STITCH_ADAPTATION, ui_spec.md, etc.

**Total docs md**: 293 — documentation-rich repository.

---

## 4. Test Folders

- No top-level `tests/` directory.
- Backend tests live inside `backend/tests/` (1422 passing tests per 2026-05-22 audit; strong coverage on services/routers/models).
- Frontend: no unit/e2e test suites visible beyond `npm run build` + `check:i18n` (raw string scan).
- CI: `.github/workflows/` contains backend-validation, frontend-validation, architecture-validation, ems-ci.

---

## 5. Design / Screenshot / Asset Folders

- `docs/design/claude-design-handoff-package/` + likely `screenshots/` subdir (referenced in handoff README) — critical for demo presentation and redesign input.
- `docs/humanization/SCREENSHOT_EVIDENCE_ALIGNMENT_REPORT.md` — maps screenshots to UX claims.

---

## 6. Generated Artifacts / Caches / Suspicious Areas

- `backend/.pytest_cache/`, `/.pytest_cache/` — generated, safe to ignore.
- `frontend/src/docs/` — internal frontend docs (import-data-v2-spec.md, EMS_SYSTEM_OVERVIEW.md) — risk of drift vs live routes.
- `architecture/prototypes/` — explicitly prototype area (per prior audits).
- Historical root .md files (2026-04) outside docs/ — should be archived or moved.
- Suspected legacy frontend pages (flagged in superior reviews): Settings.tsx, Users.tsx, Workflow.tsx, Swaps.tsx, Import.tsx, RoleDashboard.tsx, PagePlaceholder.tsx + V2 route surfaces.
- Duplicate content risk: multiple overlapping audit/final readiness reports across layers (pre- vs post-May 2026).

---

## 7. Untracked / Modified Files (Current Pass)

Only:
- `M backend/requirements.txt`

No untracked files. Working tree otherwise clean. (Do not `git add .` per rules; explicit paths only.)

---

## 8. Stale / Prototype / Duplicate Areas

- Large number of historical architecture docs (D-series, modernization passes 2026-05-12, old FINAL_* reports).
- Frontend legacy/V2 surfaces coexisting with modern role-based pages.
- Multiple "final readiness" and "pilot readiness" docs that pre-date the 05-22 superior developer synthesis.
- Prototype folder in architecture/.

**Risk**: future contributors may edit the wrong source of truth.

---

## 9. Recommended Cleanup Actions (Post-Pilot, Do Not Execute Now)

1. After pilot usage data: measure real route/page hits → safely delete/archive confirmed unused legacy pages (Settings, Users, etc.) + their hooks/services.
2. Consolidate docs: move all current source-of-truth under `docs/architecture/current/` or similar; archive pre-2026-05-22 historical audits with clear index.
3. Review .gitignore / .dockerignore for completeness (ensure no secrets, large assets, or venv leaks).
4. Frontend internal `src/docs/` — either delete or sync with live architecture docs.
5. Remove or clearly mark `architecture/prototypes/` if no longer referenced.
6. Consider splitting oversized files (main.py, models.py, some services) as flagged in missing work register — after pilot stability.
7. Update MASTER_DOCUMENTATION_INDEX.md to point exclusively to the new 100% series + 05-22 superior set.

**Rule followed**: No files deleted or modified in this audit pass. All recommendations are documented only.

---

## 10. Health Assessment

- **Strengths**: Clear separation of backend/frontend, rich service layer, extensive docs, container assets, CI workflows, design handoff package ready.
- **Weaknesses**: venv/node_modules bloat in counts, legacy code + doc drift, historical doc sprawl, no top-level test dir, single modified requirements.txt (review why).
- **Readiness implication**: Structure supports demo well; pilot/production requires contract closure + evidence before any structural cleanup.

**Next in audit**: PHASE 3 — Validation Baseline (compile, pytest, npm build/i18n).

---
*Part of EMS 100% SYSTEM READINESS AUDIT. No code or destructive changes.*
