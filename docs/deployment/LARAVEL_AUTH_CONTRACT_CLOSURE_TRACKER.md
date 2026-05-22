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

**End of LARAVEL_AUTH_CONTRACT_CLOSURE_TRACKER.md**  
This is the single live contract tracking document. Update as answers arrive.