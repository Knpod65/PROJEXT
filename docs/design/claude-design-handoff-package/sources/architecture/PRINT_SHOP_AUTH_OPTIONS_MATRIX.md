# PRINT_SHOP_AUTH_OPTIONS_MATRIX.md

**Date**: 2026-05-25
**Purpose**: Compare safe authentication options for external print-shop users who may not have CMU email.

---

## Options Matrix

| Option | Description | Pros | Cons | Best Fit |
|---|---|---|---|---|
| Option A - Local EMS print-shop account | EMS owns a dedicated partner account and credentials | Fastest to pilot, least dependency on Laravel, can map tightly to `print_shop` role | Password lifecycle burden, another login surface, requires strong restrictions | Demo or short controlled internal pilot |
| Option B - Laravel external partner account | Faculty Laravel system owns non-CMU partner accounts and sessions | Centralized faculty auth ownership, aligns with Faculty LAN topology | Requires Laravel owner work and contract detail | Long-term integrated deployment |
| Option C - Signed one-time or time-limited print link | Staff issues scoped access link for a job or batch | Least privilege, no persistent password, good vendor containment | Link leakage risk, strong expiry and audit needed | Controlled pilot or vendor access |
| Option D - Manual staff-mediated print view | Staff mediates the print package outside partner login | No new external auth surface | Weak automation, weak audit continuity, not scalable | Demo fallback only |

---

## Recommendation by Horizon

- Demo: Option A or Option D
- Controlled pilot: Option C or Option B
- Long term: Option B or Option C with strong audit and PDPA controls

---

## Current EMS Constraint

EMS already contains a `print_shop` role and a print queue workflow, but current code does not decide who owns the external partner identity source.

That ownership decision must be made before implementing external auth.

---

**End of PRINT_SHOP_AUTH_OPTIONS_MATRIX.md**
