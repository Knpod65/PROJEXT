# EMS_100_PERCENT_MASTER_SCORECARD.md

**Date**: 2026-05-25  
**Audit**: EMS 100% SYSTEM READINESS AUDIT  
**Scoring Method**: 0-100 per dimension with verifiable evidence from disk + safe execution. Separate targets for Demo 100%, Pilot 100%, Production 100%. "100" requires no known gaps at that level.

## Master Table

| Area | Current % | Demo Target | Pilot Target | Production Target | Main Gaps | Priority | Owner |
|------|-----------|-------------|--------------|-------------------|-----------|----------|-------|
| Backend | 82 | 95 | 90 | 95 | Minor env drift, partial repos, deprecations | High | Backend lead |
| Frontend | 76 | 95 | 85 | 90 | Legacy coexistence, chunk size, no FE tests, a11y/responsive | High | Frontend lead |
| Security / PDPA | 61 | 85 | 70 | 90 | Laravel contract, backup/DPO evidence, body token, secret mgmt | Critical | Security + DPO |
| Database / PostgreSQL | 62 | 80 | 75 | 90 | No Alembic, no executed backup evidence, schema ownership unconfirmed | High | Backend + DBA |
| Laravel / Faculty LAN | 25 | N/A (not in scope) | 80 (after contract) | 90 | **All contract questions unanswered** | Critical | IT + Laravel owner + EMS |
| UX / Usability | 74 | 90 | 85 | 90 | Workload explanation, mobile, a11y, print shop polish, legacy labels | High | UX + Product |
| Demo Readiness | 87 | 100 | — | — | Polish (raw strings, empty states, legacy nav, chunk) | High | EMS team |
| Pilot Readiness | 42 | — | 100 | — | Contract, PG target, backup/DPO evidence, UAT on real env | Critical | IT + DPO + Laravel + EMS |
| Production Readiness | 28 | — | — | 100 | All pilot + hardening + real env evidence + load + monitoring + sign-offs | Critical | All + external auditors |
| Performance / Scalability | 68 | 80 | 80 | 90 | Main chunk 754 kB, no load test data, heavy dashboards | High | FE + Backend |
| Testing / QA | 71 | 80 | 85 | 95 | No FE tests/E2E, no pilot-env/contract tests, deprecation warnings | High | QA + FE + Backend |
| Codebase Cleanup | 55 | 70 | 80 | 90 | Legacy pages + duplicate docs (do not delete yet) | Medium | All (post-pilot) |
| Documentation | 82 | 90 | 85 | 90 | Historical sprawl vs current source-of-truth; some drift | High | Tech writer + leads |
| DevOps / Deployment | 64 | 75 | 80 | 90 | No real pilot topology proof, secret mgmt, CI/CD on target | High | DevOps + IT |
| Role / Permission Model | 80 | 90 | 85 | 90 | Split auth_utils/permissions; bridge not yet | High | Backend + Security |
| Print Shop External Lane | 68 | 80 | 75 | 85 | Needs IT approval for external IdP; UI minimal | Medium | Backend + Print ops |

## Overall Scores (This Pass)
- **Current overall system readiness**: **64 / 100**
- **Demo readiness**: **98 / 100** (full interactive smoke passed; stakeholder demo day package + Laravel contract dispatch packet prepared. Pilot 42/100, Production 28/100 unchanged)

## Scope Reset Update (2026-06-02)
- EMS scope is explicitly reset to exam scheduling, exam operations, duty workload, and invigilation payment only.
- In this scorecard, any "workload" reference means exam duty workload: invigilation, paper distribution, room/exam-operation duty, or external exam duty already modeled in EMS.
- Any "payment" or "compensation" reference in EMS means invigilation or exam-supervision payment only. Teaching workload compensation, excess teaching pay, base workload, co-teaching, thesis/advisor workload, and course eligibility for teaching pay are out of scope.
- Current demo readiness remains **98 / 100** if demo workload screens are presented only as exam duty workload. Pilot and production readiness are unchanged.
- Invigilation payment cannot be treated as final finance calculation until rate, evidence, exception, payment-period, and approval rules are confirmed.

## Invigilation Payment Rule Intake Update (2026-06-02)
- Rule-intake, decision-register, data-readiness, and preview-model scaffold docs are now prepared for finance/admin review.
- No payment calculation, real payable amount, official payment report, or approval workflow was implemented.
- Payment readiness is unchanged until finance/admin confirms unit, rates, evidence, exceptions, approval owner, payment period, and export format.
- Demo remains valid only when payment is described as future preview/operational workflow preparation, not payment authorization.

## Faculty Web Portal Hardening Pass Update (2026-05-25)
- Dedicated Faculty Web Portal Integration score lifted modestly from 38/100 → **42/100** (see FACULTY_WEB_PORTAL_100_PERCENT_READINESS_SCORE.md)
- Frontend Route/Base + API Proxy dimension: 85 → **95** after elimination of all 5 root navigation assumptions and all 9 direct /api bypasses (centralized via new helpers + validated builds).
- No change to overall system 64/100 or Demo 98/100 (hardening was internal compatibility work only; auth contract remains the immovable 0% gate).
- Laravel / Faculty LAN line above still reflects the pre-pivot framing; the dedicated web portal scorecard is now the authoritative view.
- **Pilot readiness**: **42 / 100** (blocked by external contracts + evidence)
- **Production readiness**: **28 / 100** (far; requires pilot first + real env)

**Interpretation**: EMS is a mature, substantial institutional platform. The gap to 100% is **not code maturity** — it is **verified external contracts, operational evidence, and production environment**. Demo is the only level within easy reach without dependencies outside the team.

---
*This scorecard is the single source of truth for the 100% improvement backlog and roadmap.*
