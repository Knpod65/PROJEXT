# PILOT_ENVIRONMENT_DECISION_MATRIX.md

**Date**: 2026-05-22  
**Purpose**: Quantitative comparison of pilot environment options to support decision making.

---

## Scoring (1 = Poor, 5 = Excellent)

| Option                              | Setup Speed | Security Control | Backup Feasibility | UAT Suitability | IT Dependency | PDPA Risk Control | Cost | Maintainability | Rollback Readiness | Pilot Evidence Quality | Total (out of 50) |
|-------------------------------------|-------------|------------------|--------------------|-----------------|---------------|-------------------|------|-----------------|--------------------|------------------------|-------------------|
| A. Local Rehearsal Machine          | 5           | 1                | 1                  | 2               | 5             | 1                 | 5    | 3               | 2                  | 1                      | 26                |
| B. Faculty LAN Server               | 3           | 4                | 4                  | 5               | 3             | 5                 | 4    | 4               | 4                  | 5                      | 41                |
| C. Docker Host / VM                 | 3           | 5                | 5                  | 5               | 3             | 4                 | 4    | 5               | 5                  | 5                      | 44                |
| D. Cloud VM                         | 4           | 4                | 5                  | 4               | 2             | 3                 | 3    | 4               | 4                  | 4                      | 37                |
| E. Existing University Infrastructure | 2         | 5                | 5                  | 4               | 5             | 5                 | 5    | 4               | 5                  | 4                      | 44                |

---

## Weighted Recommendation

**For immediate controlled pilot (10-20 users, single faculty, PDPA sensitive)**:

- **Best overall**: Option C (Docker Host / VM) — 44 points, excellent repeatability and evidence quality.
- **Very close second**: Option B (Faculty LAN Server) — 41 points, best institutional fit.
- **Long-term best**: Option E (Existing University Infrastructure) — if coordination is feasible.
- **Local Rehearsal (Option A)**: Only for practice while real target is being prepared.

**Cloud (Option D)**: Acceptable only after PDPA and budget review.

---

## Conclusion

Unless a ready faculty server is immediately available, we recommend starting with **Option C (Docker/VM)** for the controlled pilot because of superior backup/restore and evidence capabilities, while keeping Option E as the migration path after the pilot.

---

**End of PILOT_ENVIRONMENT_DECISION_MATRIX.md**