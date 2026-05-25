# STAKEHOLDER_DEMO_SCRIPT.md

**Date**: 2026-05-25  
**Purpose**: Ready-to-use scripts for 5 / 15 / 30 minute standalone EMS demos.  
**Critical Rule**: Every presenter must state clearly: "This is a **standalone EMS demo**. Faculty LAN / Laravel auth integration is planned but **not implemented**. We are not claiming pilot or production readiness."

---

## Version 1: 5-Minute Executive Demo (High-Level Overview)

**Flow** (4-5 minutes max):

1. **30 sec** — Login (use admin account) → Role Selection → "We support 7+ roles with one codebase."
2. **1 min** — Dashboard (admin view) — "Live operations at a glance."
3. **1.5 min** — Admin Intelligence Dashboard — "The new unified view: workload fairness, governance, rooms, PDPA, health, executive summary. All computed from real data."
4. **1 min** — One deep dive (e.g., Workload for teacher or Governance Cockpit) — "Fairness scoring + approval workflows."
5. **30 sec** — Close: "96/100 demo-ready as standalone. Full Faculty LAN integration and production hardening still require IT/Laravel contract closure (currently 25/100 on that axis). Questions?"

**What to say**:
- "Standalone demo today."
- "All data is seeded for this environment."
- "i18n complete (Thai/English)."

**What NOT to say**:
- Do not say "ready for pilot" or "production."
- Do not demo hidden legacy pages.

---

## Version 2: 15-Minute Operational Demo (Role Journeys)

**Pre-demo**:
- Start backend + frontend (or use built version).
- Confirm 4 seed accounts work.
- Legacy nav hidden.

**Detailed Flow** (15 min):

1. **Login + Role Selection** (2 min) — Show all 4 accounts.
2. **Teacher Journey** (3 min):
   - Login as pailin.phu/teacher123
   - My Workload → see personal fairness score
   - Schedule + Submissions
3. **Staff / Print Shop** (3 min):
   - printshop.ops/print123
   - Print queue + review + QR scanner
4. **Admin / Governance** (4 min):
   - mathawee.m/admin123 or napaporn.ph
   - Admin Intelligence (highlight new payload)
   - Governance Cockpit + Audit Explorer
5. **Wrap** (3 min):
   - Show i18n toggle
   - Mention bundle improvement and legacy cleanup
   - Explicit limitations slide (see DEMO_LIMITATIONS_AND_DISCLOSURE.md)

**Key Talking Points**:
- "Legacy pages hidden from demo navigation for clarity."
- "Heavy dashboards lazy-loaded for performance."

---

## Version 3: 30-Minute Deep Demo (Technical + Operational)

Use the full DEMO_USER_JOURNEY_SCRIPT.md as base, plus:

- Backend validation recap (1428 tests, clean compile)
- Frontend: 560 kB main chunk (improved), full i18n parity
- Navigation polish demo (show that legacy Users/Settings are hidden)
- Deep dive into one intelligence dashboard with live data explanation
- Q&A buffer (10 min) — be ready with answers from DEMO_LIMITATIONS...

**Always end with**:
"Demo readiness 96/100 (standalone). Pilot and production still blocked by external contract and evidence (42/100 and 28/100). We are transparent about the gaps."

---

## Prepared Answers to Expected Questions

**Q: Is this ready for our Faculty LAN?**  
A: No. Laravel auth contract still unanswered. We have excellent analysis but zero verified answers from IT/Laravel owner yet.

**Q: Can we use real data?**  
A: In this standalone demo we use seeded data. Real PostgreSQL target + backup evidence still pending.

**Q: What about DPO / PDPA?**  
A: Templates and policies exist. Signed DPO sign-off on CMU email flow through external auth is still required.

**Q: Why is the main bundle still 560 kB?**  
A: SPA with rich dashboards. We already split vendor and React Query. Further splitting possible but acceptable for current demo scale.

---
*Print or share this script + the Limitations note for every stakeholder session.*
