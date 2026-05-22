# TESTING_QA_COVERAGE_AUDIT.md

**Date**: 2026-05-22

---

## Summary

Testing maturity is asymmetric:

- backend coverage is strong
- build and i18n checks are real
- frontend application test coverage is weak
- integrated pilot evidence is still incomplete

---

## Safe Validation Results In This Audit Pass

| Check | Result | Notes |
|---|---|---|
| `backend\.venv\Scripts\python.exe -m compileall backend -q` | PASS | No syntax failures |
| backend import smoke (`import main`) | PASS | `IMPORT_ROUTERS_ERROR` printed `None` |
| `backend\.venv\Scripts\python.exe -m pytest backend\tests -q` | PASS | `1422 passed`, `12 warnings` |
| `npm run build` | PASS with warning | Build succeeded; main chunk warning at `754.73 kB` |
| `npm run check:i18n` | PASS | `1688` keys in both `en` and `th` |
| `npm run check:i18n:raw` | WARNING MODE | Candidate raw strings still detected |

---

## What Is Well Tested

- backend services
- backend policies
- analytics and route contracts
- config validation behavior
- health service behavior
- optimization and workflow-related logic
- security-key enforcement tests

This is a significant strength.

---

## What Is Not Well Tested

| Area | Gap |
|---|---|
| Frontend unit tests | No meaningful app-level suite found in repo source |
| Frontend e2e tests | No Playwright/Cypress-style app suite found |
| Laravel auth bridge | No integration tests because bridge is not yet implemented |
| Faculty LAN route/proxy behavior | No real target-environment test evidence |
| Backup / restore | Runbooks and templates exist, but real evidence is still open |
| UAT | Go/no-go remains conditional; no completed real-wave evidence in this audit pass |
| Load testing | historical docs mention limited scale; no new load evidence generated here |

---

## Warning Debt

Observed during test / validation pass:

- SQLAlchemy deprecation around `declarative_base()`
- multiple Pydantic v2 class-config deprecation warnings
- development `SECRET_KEY` fallback warning when env is not set for local import
- frontend raw-string candidate scan remains noisy

These are not immediate pilot blockers by themselves, but they are legitimate technical debt.

---

## Tests Needed Before Faculty LAN Pilot

1. real deployment smoke on target infrastructure
2. backup and restore evidence run
3. contract-verified auth bridge rehearsal if Laravel bridge is selected
4. at least one full UAT wave with pilot users and recorded observations

---

## Tests Needed Before Production

1. frontend unit coverage for the highest-risk routed pages
2. at least one end-to-end browser suite for login, scheduling, submissions, workflow, and public student search
3. load / concurrency testing against target deployment shape
4. logout / session expiry coverage for the final Laravel auth strategy

---

## Audit Judgment

Testing maturity is **good for backend engineering confidence**, but **not yet sufficient to call the whole system fully production-proven**, because integrated frontend, infrastructure, backup, and external-auth evidence are still thinner than backend unit/service coverage.
