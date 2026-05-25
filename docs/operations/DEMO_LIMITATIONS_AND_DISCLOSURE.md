# DEMO_LIMITATIONS_AND_DISCLOSURE.md

**Date**: 2026-05-25  
**Audience**: All internal and external stakeholders for standalone EMS demo.

## What This Demo Proves

- EMS is a **substantial, mature institutional platform** (not a prototype).
- Core operational flows (schedule, submissions, print, checkins, import) work for multiple roles.
- Rich intelligence layer (Admin Intelligence, Workload fairness, Governance, Audit, Operational Health, Executive Analytics) is functional and data-driven.
- Role-based access, Thai/English i18n (1688 keys), and modern React architecture are production-grade.
- Recent polish (legacy hidden from demo nav, bundle improved to 560 kB, clean validation) makes it suitable for controlled stakeholder walkthroughs.
- Demo readiness: **96/100** (standalone).

## What This Demo Does NOT Prove

- **Faculty LAN / Laravel integration**: 0% implemented. Contract questions (203-line document) remain completely unanswered. Auth bridge not started (correctly — per all prior audits).
- **Real PostgreSQL + backup/restore**: Using local SQLite for this demo. No target Faculty DB, no executed backup evidence.
- **DPO / PDPA sign-off**: Policies and templates exist. No signed retention or CMU email flow approval for external auth.
- **Production readiness**: 28/100. No live environment, no load testing, no monitoring, no incident response proof.
- **Pilot readiness**: 42/100. Blocked by the above external items.
- **Full data volume / scale**: Seeded data only. Real semester + historical data not present.

## Explicit Scope Statement (Must Be Said in Every Demo)

"This is a **standalone EMS demo** using local seeded data and local authentication.  
Faculty LAN deployment, POLSCI OAuth / Laravel integration, real PostgreSQL, backup evidence, and DPO sign-off are **out of scope** for today's session and remain open items requiring IT and owner responses.  
We are not claiming pilot or production readiness."

## Why This Demo Is Still Valuable

- Proves the platform depth and architecture quality.
- Allows stakeholders to experience the new intelligence dashboards and role journeys.
- Demonstrates transparency: we show exactly what is ready (96/100 demo) and what is not (external dependencies).
- Provides a clean baseline before any future redesign or integrated pilot work.

## Con-1 / External Issues

Any external system integration issues (con-1) are explicitly excluded from this demo scope unless the stakeholder session specifically includes them (in which case they will be called out separately).

---
*Use this note as a handout or slide. Honesty builds trust.*
