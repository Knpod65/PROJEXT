# EMS_MISSING_WORK_REGISTER.md

**Date**: 2026-05-22

---

## Missing Work Register

| Category | Task | Why Needed | Owner | Evidence | Priority | Estimated Effort | Dependency |
|---|---|---|---|---|---|---|---|
| Blocker before pilot | Verify Laravel auth contract | Required before any bridge code or routing decision | Laravel owner + EMS lead | `LARAVEL_AUTH_CONTRACT_QUESTIONS.md` answered and verified | Critical | 1-3 days | Faculty owner response |
| Blocker before pilot | Confirm `session("USS")` payload and CMU email field | Needed for safe identity mapping | Laravel owner | code-backed contract answers | Critical | 1 day | Laravel code access |
| Blocker before pilot | Decide auth bridge option | Needed for implementation and test plan | EMS lead + Laravel owner + IT | signed option decision | Critical | 0.5 day | contract answers |
| Blocker before pilot | Decide EMS mount path on Faculty LAN | Affects proxy, cookies, docs, and UX links | IT + EMS lead | route/mount decision record | High | 0.5 day | IT consultation |
| Blocker before pilot | Provision real PostgreSQL target | Needed to avoid SQLite fallback | IT / DBA | working connection on target host | Critical | 1-2 days | infrastructure access |
| Required before pilot | Remove startup schema-create and seeding from normal runtime path | Production runtime should not mutate schema on boot | Backend owner | code change + smoke proof | High | 1-2 days | backend implementation |
| Required before pilot | Unify secret/env hardening rules | Avoid `ENV` vs `ENVIRONMENT` drift and mixed secret thresholds | Backend owner | code and deploy doc update | High | 0.5-1 day | backend implementation |
| Required before pilot | Configure production secrets and DB env on target | Required by readiness and security | IT / deployment owner | verified config checklist | Critical | 0.5 day | target host ready |
| Required before pilot | Execute backup and restore with evidence | Runbook exists but proof is still open | IT / Ops | completed evidence template | High | 0.5-1 day | target DB ready |
| Required before pilot | Obtain DPO sign-off including CMU email flow | Required for PDPA governance | DPO + system owner | signed template | High | 1-3 days | data-flow explanation |
| Required before pilot | Correct stale frontend internal route docs | Prevent future wrong-source changes | Frontend owner | updated or archived docs | Medium | 0.5 day | none |
| Required during pilot | Run at least one full UAT wave with real users | Needed to move from conditional go to evidence-backed decision | Pilot coordinator | checklists + observation pack | High | 1-2 days | accounts + target ready |
| Required during pilot | Measure actual usage of legacy routes/pages | Needed before safe deletion of legacy surfaces | Frontend + backend owners | access logs / route usage report | Medium | 1-2 days | pilot traffic |
| Required before production | Add frontend unit/e2e coverage | Backend tests are strong; frontend coverage lags | Frontend owner | test suite and CI pass | Medium | 3-5 days | feature stabilization |
| Required before production | Formalize migration ownership/tooling | Current manual migration style is fragile at scale | Backend owner + DBA | agreed migration process | High | 2-4 days | DB governance |
| Post-pilot improvement | Archive unused legacy pages and duplicate hooks/services | Improve maintainability and reduce confusion | Frontend owner | cleanup PR | Medium | 1-2 days | route usage confidence |
| Post-pilot improvement | Split `main.py` and `models.py` by concern | Reduce review and onboarding cost | Backend owner | refactor PR | Medium | 3-5 days | pilot stability |
| Nice-to-have | Reduce frontend main bundle size | Improves device responsiveness | Frontend owner | build report improvement | Low | 1-2 days | after page cleanup |
| Do not do yet | Implement Laravel bridge code before contract verification | Unsafe and likely to be wrong | EMS team | N/A | Critical | N/A | contract answers first |

---

## Most Important Next Action

**Send and close `LARAVEL_AUTH_CONTRACT_QUESTIONS.md` with the real Laravel owner.**

That action unblocks the largest number of downstream decisions.
