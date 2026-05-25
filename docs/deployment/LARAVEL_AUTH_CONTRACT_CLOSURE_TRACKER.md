# LARAVEL_AUTH_CONTRACT_CLOSURE_TRACKER.md

**Date**: 2026-05-22  
**Owner**: EMS team + Laravel / IT owner (to be assigned)  
**Purpose**: Track every item in the Laravel/CMU auth contract until all are answered and verified.

---

## Contract Status Summary

| Item | Owner | Answer Received? | Answer | Risk If Unknown | Blocks Code? | Status |
|------|-------|-----------------|--------|-----------------|-------------|--------|
| Laravel owner identified | Faculty IT | [ ] Yes  [ ] No | TBD | Cannot proceed | Yes | OPEN |
| IT owner identified | Faculty IT | [ ] Yes  [ ] No | TBD | Cannot provision | Yes | OPEN |
| Callback route verified | Laravel owner | [ ] Yes  [ ] No | TBD | Incorrect bridge endpoint | Yes | OPEN |
| AuthMiddleware behavior confirmed | Laravel owner | [ ] Yes  [ ] No | TBD | Auth gate misconfigured | Yes | OPEN |
| session("USS") payload verified | Laravel owner | [ ] Yes  [ ] No | TBD | Identity mapping unsafe | Yes | OPEN |
| cmu_at meaning verified | Laravel owner | [ ] Yes  [ ] No | TBD | Token handling wrong | Yes | OPEN |
| CMU email field name confirmed | Laravel owner | [ ] Yes  [ ] No | TBD | Identity mapping wrong | Yes | OPEN |
| EMS mount path verified | IT + Laravel owner | [ ] Yes  [ ] No | TBD | Cookie/domain misconfiguration | Yes | OPEN |
| PostgreSQL target confirmed | IT / DBA | [ ] Yes  [ ] No | TBD | Wrong DB or SQLite fallback | Yes | OPEN |
| Deployment method confirmed | IT | [ ] Yes  [ ] No | TBD | Routing/cookie failures | Yes | OPEN |
| Logout behavior confirmed | Laravel owner | [ ] Yes  [ ] No | TBD | Session leak | Yes | OPEN |
| Cookie/session policy confirmed | Laravel owner | [ ] Yes  [ ] No | TBD | CSRF or session fixation | Yes | OPEN |

All items are OPEN as of 2026-05-22.

---

## Required Answers Detail (from LARAVEL_AUTH_CONTRACT_QUESTIONS.md)

Source: `docs/deployment/LARAVEL_AUTH_CONTRACT_QUESTIONS.md` (20+ questions across routes, session, token, identity, database, deployment, cookies, CSRF, logout, role mapping, audit logging).

**No answers have been received yet.**

---

## Current Decision

**Auth bridge implementation is BLOCKED until all required contract answers are received and verified against the real Laravel codebase.**

Do not begin bridge code, route changes, or deployment topology changes until this tracker is at least partially populated with verified answers.

---

---

## 2026-05-25 Additions: POLSCI OAuth + External Print Shop

| Item | Owner | Answer Received? | Answer | Risk If Unknown | Blocks Code? | Status |
|------|-------|-----------------|--------|-----------------|-------------|--------|
| POLSCI callback payload verified | Laravel owner | [ ] Yes  [ ] No | TBD | Bridge endpoint may parse the wrong artifact | Yes | OPEN |
| POLSCI callback parameter names verified | Laravel owner | [ ] Yes  [ ] No | TBD | EMS cannot safely consume callback output | Yes | OPEN |
| ServiceUrl strategy verified | Laravel owner + IT | [ ] Yes  [ ] No | TBD | EMS may be mounted on an unsupported callback path | Yes | OPEN |
| Existing portal callback ownership verified | Laravel owner | [ ] Yes  [ ] No | TBD | Bridge boundary may be implemented in the wrong layer | Yes | OPEN |
| Error callback behavior verified | Laravel owner | [ ] Yes  [ ] No | TBD | EMS cannot handle failures safely | Yes | OPEN |
| External print-shop identity owner selected | EMS + Laravel owner + IT | [ ] Yes  [ ] No | TBD | Print-shop lane cannot be implemented safely | Yes | OPEN |
| External print-shop account source selected | EMS + Laravel owner + IT | [ ] Yes  [ ] No | TBD | Wrong auth lane may be built | Yes | OPEN |
| Print-shop permission matrix approved | EMS owner | [ ] Yes  [ ] No | TBD | Over-privileged external access | Yes | OPEN |
| PDPA-minimized print-shop field set approved | EMS owner + DPO | [ ] Yes  [ ] No | TBD | Excessive personal data disclosure | Yes | OPEN |

Current expanded decision:

**Bridge implementation remains BLOCKED. The observed POLSCI OAuth login pattern is useful evidence, but it does not satisfy the Laravel callback contract or the external print-shop account contract.**

---

**End of LARAVEL_AUTH_CONTRACT_CLOSURE_TRACKER.md**  
This is the single live contract tracking document. Update as answers arrive.
