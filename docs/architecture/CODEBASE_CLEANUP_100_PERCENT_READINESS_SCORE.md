# CODEBASE_CLEANUP_100_PERCENT_READINESS_SCORE.md

**Date**: 2026-05-25  
**Sources**: UNUSED_AND_DUPLICATE_FILE_AUDIT, SYSTEM_REPOSITORY_HEALTH_AUDIT (this pass), prior superior review, globs showing 293 md + legacy pages

**Current Cleanup Score: 55 / 100** (no deletes performed — correct per rules)

## Confirmed Unused / High Risk to Keep
- Frontend legacy pages (flagged repeatedly): Settings.tsx (non-V2), Users.tsx, Workflow.tsx, Swaps.tsx, Import.tsx, RoleDashboard.tsx, PagePlaceholder.tsx + associated hooks/services.
- Historical root .md files outside docs/ (2026-04 reports).
- architecture/prototypes/ folder.
- Duplicate audit content across pre- and post-May 2026 layers.
- frontend/src/docs/ (internal, drift risk).

## Probably Unused (Needs Usage Data in Pilot)
- Many older D3/D4/D5/modernization pass docs.
- Some migrate_*.py scripts that may have been superseded by v2 import.
- Certain event handlers or serializers if no longer wired.

## Risky to Delete Now
- Anything in active routers/services (even if "V1") until pilot traffic proves zero usage.
- Any doc that might still be referenced by IT handoff packages.
- Seed/migrate scripts (used in dev and possibly by ops).

## Cleanup Plan (Post-Pilot Only)
1. After pilot: collect route/page hit logs for 2-4 weeks.
2. Archive (do not delete) all zero-traffic legacy pages + their tests/docs.
3. Move historical audits to docs/archive/ with index.
4. Consolidate duplicate "final readiness" docs into the new 100% series.
5. Review .gitignore for generated (pytest, node_modules, dist, ems.db, etc.).
6. Delete only after team + pilot coordinator sign-off.

**Rule strictly followed**: Zero files deleted or modified in this entire 100% audit pass.

---
*Cleanup score is intentionally conservative. The codebase is large but not dangerous — it just has migration-era residue.*
