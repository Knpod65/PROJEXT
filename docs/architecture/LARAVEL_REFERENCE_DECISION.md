# Laravel Reference Decision
## EMS Academic Operations Platform - 2026-05-12

---

## 1. Decision

EMS should **not** be rewritten into Laravel/PHP now.

Laravel/PHP should be used as an architectural reference for discipline:
- route -> middleware/auth guard -> controller/router -> service/repository -> model -> view/response
- MVC separation
- SOLID
- DRY
- centralized auth/session logic
- centralized validation
- centralized audit logging

EMS should keep the current production direction:
- Frontend: React + TypeScript + Vite
- Backend: FastAPI + SQLAlchemy + Pydantic
- Database: SQLite dev / PostgreSQL-ready

---

## 2. Why EMS Should Remain FastAPI / React

### Domain fit
- EMS contains scheduling, optimization, data transformation, document generation, and workflow-heavy logic that fits the Python ecosystem well.

### Delivery fit
- The current FastAPI backend already has production-hardening work, typed configuration, RBAC guards, and audit patterns in place.

### Risk reduction
- A full rewrite would risk regressions in exam scheduling, submission, document, QR, and workflow behavior.

### Architectural compatibility
- FastAPI supports the same architectural discipline Laravel is being used to teach:
  - route modules
  - dependency-based middleware/guards
  - service layers
  - repository layers
  - policy helpers
  - typed validation through Pydantic

---

## 3. Comparison Table

| Option | Summary | Benefits | Risks | Recommendation |
|---|---|---|---|---|
| Full Laravel rewrite | Replace FastAPI backend with Laravel/PHP | Familiar to PHP/Laravel teams; visual alignment with faculty notes | High rewrite cost, high regression risk, duplicated effort, loss of Python-native scheduling/optimization strengths | Not recommended |
| Laravel Auth Gateway + EMS FastAPI | Laravel handles upstream faculty auth, EMS keeps business backend | Good if Faculty IT already operates a shared Laravel auth broker; preserves EMS domain logic | Extra trust boundary, more operations complexity, split audit ownership | Acceptable if mandated by Faculty IT |
| FastAPI-native callback/authen support | EMS handles callback/authen or verified assertion directly | Lowest change risk, single business backend, simpler audit trail, no stack split | EMS team must own external auth adapter | Recommended by default |

---

## 4. Recommended Direction

### Primary recommendation
- Keep EMS on FastAPI/React.
- Use Laravel as a reference for architectural discipline, not as a rewrite target.
- Add an EMS auth integration layer that can consume Faculty IT callback/authen or `cmu_at` verification results.

### Acceptable integration models
- Laravel Auth Gateway if Faculty IT already mandates it
- FastAPI-native callback/authen support if EMS can consume the contract directly

### Not recommended
- Full Laravel/PHP rewrite for EMS itself

---

## 5. Faculty IT Alignment Model

```text
Faculty IT / Laravel AuthMiddleware / AuthenController / callback/authen / cmu_at
    -> EMS Auth Integration Layer
    -> EMS JWT + HttpOnly cookie
    -> EMS permissions.py + permission_service
    -> React auth store and permission-based UI
```

This gives EMS the same control-discipline structure as the handwritten Laravel notes while preserving the current runtime stack.

---

## 6. Where Laravel Can Still Be Useful

Laravel may still be useful as:
- a Faculty Auth Gateway
- a shared identity provider or SSO bridge
- a separate internal admin portal if the institution wants one
- a compatibility layer for systems that already depend on Laravel middleware conventions

Laravel is useful at the integration edge. It is not currently justified as the core EMS runtime replacement.

---

## 7. Final Recommendation

EMS should remain FastAPI + React.

The Laravel reference should guide:
- layering
- naming discipline
- repository/service separation
- middleware-style authorization
- callback/authen compatibility
- DRY/SOLID cleanup

The Laravel reference should **not** trigger a backend stack rewrite.
