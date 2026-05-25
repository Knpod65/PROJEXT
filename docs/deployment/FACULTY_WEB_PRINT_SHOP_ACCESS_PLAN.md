# FACULTY_WEB_PRINT_SHOP_ACCESS_PLAN.md

**Date**: 2026-05-25

## Context

Print shop / copy center users frequently do not have CMU email accounts. They must not be forced into fake CMU identity when EMS is deployed under the Faculty Web Portal.

## Options for Faculty Web Portal Deployment

### Option 1 — Laravel External Partner Accounts (Recommended Long-Term)
- Faculty web / Laravel creates "external partner" accounts for print shop staff.
- Login goes through the same central OAuth or a partner-specific flow.
- EMS receives verified external identity + scoped role.
- Pros: Centralized identity management, audit, consistent with faculty web.
- Cons: Requires Laravel owner work and contract detail.

### Option 2 — EMS-Managed External Accounts (Standalone Lane Preserved)
- Print shop users continue to use current EMS local accounts (or a dedicated external auth provider).
- When EMS is under faculty web, this becomes a secondary login path or separate /print-shop entry point.
- Pros: No dependency on Laravel for external users; current demo behavior preserved.
- Cons: Two identity systems; potential user confusion.

### Option 3 — Time-Limited Signed Print Job Links
- Staff generate secure, expiring links for specific print jobs.
- Print shop accesses via the link without full login.
- Pros: Minimal identity surface for externals.
- Cons: Limited to job-specific access; not full self-service portal.

### Option 4 — Staff-Mediated Workflow
- Print shop never logs into EMS directly.
- All requests come through internal staff interfaces.
- Pros: Simplest security model.
- Cons: Bottleneck for high-volume print shop operations.

## Recommendation for Web Portal Pilot

Start with a combination:
- CMU users: Faculty web OAuth / Laravel bridge (when contract closed).
- Print shop: Preserve current standalone external lane (Option 2) or move to Laravel external accounts (Option 1) once the model is agreed.

The hybrid model already documented in HYBRID_AUTH_MODEL_CMU_AND_PRINT_SHOP.md remains valid; only the deployment surface (web portal vs pure LAN) has changed.

## Audit & PDPA Note

Any external partner identity model must be reviewed by DPO for data minimization and consent.

---
*Print shop external access must remain a first-class, non-CMU pathway regardless of web portal deployment.*
