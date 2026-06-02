# EMS_ROADMAP_TO_100_PERCENT.md

**Date**: 2026-05-25  
**Based on**: Master Scorecard + Improvement Backlog + all phase scores

## Scope Reset Note (2026-06-02)

The roadmap is constrained to exam scheduling, exam operations, exam duty workload, and invigilation payment only. Any payment stage must use confirmed invigilation duty evidence and approved invigilation payment rules. Teaching workload compensation and teaching payment workbooks are not EMS sources of truth.

For the corrected payment sequence, use `EMS_CORRECTED_NEXT_PHASE_ROADMAP.md`.

## Stage 0 — Stabilize Repo & Validation (Done in this pass)
- Pre-flight git checks, full source review, repo health audit, validation baseline re-run (all green).
- Target: 100% of new 100% docs created.
- Owner: This audit.
- Acceptance: All 20+ required docs written, git status clean (docs only), no code changes yet.

## Stage 1 — Demo 100% (Target: 100%)
- Tasks: T006 (legacy hide + raw strings), T007 (chunk), T012 (rehearsal + assets).
- Owner: EMS team.
- Dependencies: None external.
- Acceptance: Demo rehearsal passes with polished empty states, no legacy in nav, i18n clean, build warning addressed or accepted, demo script + screenshots current.
- Target after: Demo readiness 100%, overall system ~72.

## Stage 2 — Faculty LAN Contract Closure (Critical Gate)
- Tasks: T001 (send + close LARAVEL_AUTH_CONTRACT_QUESTIONS), decide bridge option + mount path + proxy rules.
- Owner: IT + Laravel owner + EMS lead.
- Dependencies: Faculty IT responsiveness.
- Acceptance: All questions answered + code-verified; signed decision record; no TBDs left.
- Target after: Laravel score 70+, Pilot readiness jumps to ~55.

## Stage 3 — Pilot Environment Setup
- Tasks: T002 (real PG), T003 (backup/restore evidence), pilot accounts, topology config.
- Owner: IT + DBA + EMS.
- Dependencies: T001 answers (mount path affects proxy).
- Acceptance: Working target env, DATABASE_URL live, backup proof attached, accounts testable.
- Target after: DB 80, Pilot ~70.

## Stage 4 — Auth Bridge Implementation (Only After Contract)
- Tasks: Implement chosen safe option (likely Option B short-lived bridge), tests, fallback preserved.
- Owner: Backend + Laravel owner.
- Dependencies: Stage 2 complete.
- Acceptance: Auth works through verified flow; no CMU token to frontend; rollback plan; smoke on target.
- Target after: Security 80+, Pilot 80+.

## Stage 5 — Backup / DPO / UAT Evidence
- Tasks: T004 (DPO sign-off), T013 (UAT on real env + Go/No-Go).
- Owner: DPO + Pilot coordinator + EMS.
- Dependencies: Stages 2-4.
- Acceptance: Signed DPO, UAT pass, updated blocker dashboard, Go decision.
- Target after: Pilot 95+, Security/PDPA 85.

## Stage 6 — Controlled Pilot Execution
- Run pilot with real users on Faculty LAN.
- Collect usage data, issues, performance.
- Target: Pilot 100%.

## Stage 7 — Post-Pilot Hardening
- T009 (Alembic), T010 (secret manager), T014 (cleanup from usage data), FE tests, a11y, responsive.
- Target: Multiple areas to 85-90.

## Stage 8 — Production Readiness
- Full CI/CD on real infra, load/chaos, monitoring, incident response, external audit, rollback proven, all sign-offs.
- Target: Production 95+.

## Stage 9 — UI Redesign Implementation
- Only after Stage 1 (Demo 100%) and preferably after pilot feedback.
- Use claude-design-handoff-package + updated screenshot atlas.
- Do not start redesign before demo polish and contract clarity.

## Stage 10 — Long-Term Institutional Platform Maturity
- Multi-faculty isolation, advanced optimization, predictive intelligence, full governance automation, institutional SLAs.

**Critical Path**: Stage 0 (done) → 1 (demo) → 2 (contract) → 3-5 (pilot evidence) → 6 (pilot) → 7-8 (production).

**Do not skip gates** (especially contract before any bridge code).

---
*This roadmap is the agreed sequence. Any deviation requires explicit update to this document and the backlog.*
