# SAFE_QUICK_WINS_TO_REACH_DEMO_100.md

**Date**: 2026-05-25  
**Rule**: Only items that are:
- Safe (no Laravel contract, no production server, no DPO, low risk)
- Isolated
- Testable
- Needed for Demo 100%
- Do NOT implement in this pass unless explicitly instructed later.

## Identified Safe Quick Wins (Do Not Start Yet)

1. **Frontend polish for demo** (T006 partial)
   - Hide legacy non-V2 pages from demo navigation config.
   - Fix 5-10 real user-facing raw strings in AdminIntelligenceDashboard, AuditExplorer, Checkins (the ones flagged by i18n:raw that are not imports).
   - Update any obvious empty states that still look broken on demo accounts.
   - **Risk**: Very low. Purely presentational. Tests: build + i18n + manual demo rehearsal.
   - **Effort**: 4-8 hours.
   - **Acceptance**: Demo script runs end-to-end with no raw English in Thai mode, no legacy nav items for demo users, no crashing empty states.

2. **Bundle size quick win** (T007 partial)
   - Add 2-3 more manualChunks for the heaviest remaining shared libs (if any) or move one more heavy page to dynamic import.
   - Run `npm run build` and confirm warning either gone or explicitly accepted in docs.
   - **Risk**: Low (build-time only).
   - **Effort**: 2-4 hours.
   - **Acceptance**: Build log shows improvement or documented acceptance of remaining size for demo.

3. **Documentation hygiene (no code)**
   - Update MASTER_DOCUMENTATION_INDEX.md to point to the new 100% series + 05-22 superior set as current truth.
   - Add a one-line note in README-DEV.md or RUNBOOK.md: "Current 100% readiness assessment is in docs/architecture/EMS_100_PERCENT_* (2026-05-25)".
   - **Risk**: Zero.
   - **Effort**: 30 min.
   - **Acceptance**: Index and README reference the new docs.

4. **Add one browser smoke script (optional, low risk)**
   - Simple Playwright or manual script that hits the 8-10 key demo routes for the 4 seed accounts and screenshots them.
   - **Risk**: Low if kept as optional dev tool.
   - **Effort**: 2-3 hours.
   - **Acceptance**: Script runs locally and produces evidence for demo rehearsal.

5. **i18n coverage report (already scripted)**
   - Run `npm run check:i18n:coverage` if it exists and attach to demo assets (or note that parity is already 1688/1688).
   - **Risk**: Zero.

**Explicit Instruction**: Do NOT implement any of the above in the current 100% audit pass. They are documented for the next focused "Demo Polish" mini-sprint after this audit is committed.

**Forbidden in this pass (per absolute rules)**:
- Any change touching Laravel auth, external contracts, real DB, DPO items, or risky refactors.
- Deleting files.
- Committing unrelated changes.

---
*These are the only safe, high-value, zero-dependency items that can move Demo from 87 → 100 without waiting for anyone else.*
