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
- Workload screens, if shown, demonstrate exam duty workload only: invigilation, paper distribution, and related exam-operation duties.

## What This Demo Does NOT Prove

- **Faculty LAN / Laravel integration**: 0% implemented. Contract questions (203-line document) remain completely unanswered. Auth bridge not started (correctly — per all prior audits).
- **Real PostgreSQL + backup/restore**: Using local SQLite for this demo. No target Faculty DB, no executed backup evidence.
- **DPO / PDPA sign-off**: Policies and templates exist. No signed retention or CMU email flow approval for external auth.
- **Production readiness**: 28/100. No live environment, no load testing, no monitoring, no incident response proof.
- **Pilot readiness**: 42/100. Blocked by the above external items.
- **Full data volume / scale**: Seeded data only. Real semester + historical data not present.
- **Final invigilation payment calculation**: Not proven in this demo. Payment requires confirmed rate, evidence, exception, approval, and export rules.
- **Teaching workload compensation**: Explicitly out of scope. EMS does not calculate excess teaching pay, course eligibility for teaching payment, base workload, co-teaching payment, or thesis/advisor workload payment.
- **Payment rule intake**: Documentation scaffolding exists for rule collection and preview design only. It does not authorize payment or produce real payable amounts.
- **Payment preview readiness**: Current validation says payment preview implementation is not ready because all required rule answers remain pending.

## Explicit Scope Statement (Must Be Said in Every Demo)

"This is a **standalone EMS demo** using local seeded data and local authentication.  
Faculty LAN deployment, POLSCI OAuth / Laravel integration, real PostgreSQL, backup evidence, and DPO sign-off are **out of scope** for today's session and remain open items requiring IT and owner responses.  
Payment in EMS means invigilation payment only; teaching workload compensation is not part of this system.  
Any payment discussion today is preview/intake only until finance/admin confirms the rules.  
Current rule validation found no approved payment answers, so no payment preview or final payment claim should be made.  
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

## Invigilation Payment Model Correction (2026-06-02)

- Payment model documentation has been corrected to advance disbursement plus post-duty reconciliation.
- Missing check-in is a reconciliation trigger, not an automatic pre-payment block.
- No real amount, official payment report, refund, or offset decision is implemented for demo.
- Advance roster preview, if shown, must be described as no-amount roster review, not payment authorization.

## Advance Batch Preview Demo Disclosure (2026-06-02)

- The advance batch roster page is now available as a preview-only operational view.
- It may be shown to demonstrate roster review, blockers, warnings, and unresolved rule gaps.
- `PENDING_RATE_RULE` is intentional and means no payment amount has been calculated.
- The page must not be presented as payment authorization, final export, or production-ready finance output.
