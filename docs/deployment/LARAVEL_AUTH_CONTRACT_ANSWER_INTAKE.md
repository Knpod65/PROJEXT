# LARAVEL_AUTH_CONTRACT_ANSWER_INTAKE.md

**Date**: 2026-05-25
**Purpose**: Structured intake sheet for answers returned by the Laravel owner and IT team.

---

## How to Use

1. Copy an unanswered item from `LARAVEL_AUTH_CONTRACT_QUESTIONS.md`.
2. Record the received answer below.
3. Add the evidence source.
4. Mark whether EMS has verified the answer against real code or configuration.

Do not store secrets in this document.

---

## Intake Ledger

| Question ID | Question Summary | Answer Received | Source | Date Received | Owner / Sender | Evidence Type | EMS Verified Against Real Code? | Confidence | Notes |
|---|---|---|---|---|---|---|---|---|---|
| A1 | Callback route path | TBD | TBD | TBD | TBD | TBD | No | Unknown | |
| B1 | Session key / `session("USS")` | TBD | TBD | TBD | TBD | TBD | No | Unknown | |
| B2 | Session payload fields | TBD | TBD | TBD | TBD | TBD | No | Unknown | |
| C1 | Meaning of `cmu_at` or equivalent | TBD | TBD | TBD | TBD | TBD | No | Unknown | |
| D1 | CMU email field name | TBD | TBD | TBD | TBD | TBD | No | Unknown | |
| I1 | POLSCI callback artifact type | TBD | TBD | TBD | TBD | TBD | No | Unknown | |
| I4 | EMS callback ownership / ServiceUrl strategy | TBD | TBD | TBD | TBD | TBD | No | Unknown | |
| J1 | External print-shop account support | TBD | TBD | TBD | TBD | TBD | No | Unknown | |
| J2 | External account storage location | TBD | TBD | TBD | TBD | TBD | No | Unknown | |
| J4 | Can `session("USS")` represent non-CMU users | TBD | TBD | TBD | TBD | TBD | No | Unknown | |

---

## Verification Rule

An answer is not considered closed until EMS has checked it against one of:

- real Laravel route/controller code
- real Laravel session or middleware code
- real Nginx or deployment config
- real database or schema ownership evidence

Email statements or meeting notes alone are not enough to unblock implementation.

---

**End of LARAVEL_AUTH_CONTRACT_ANSWER_INTAKE.md**
