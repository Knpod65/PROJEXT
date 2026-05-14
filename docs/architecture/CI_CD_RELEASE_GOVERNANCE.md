# CI/CD Release Governance

**Status:** Implemented — Phase 2  
**Date:** 2026-05-14  
**File:** `.github/workflows/ems-ci.yml`

---

## Purpose

Stop relying on manual validation before every merge. The CI workflow enforces
the same validation steps that were previously run by hand, automatically on
every push to `main`/`develop` and every PR targeting `main`.

---

## Workflow Overview

```
push / PR → GitHub Actions
  ├── backend job
  │   ├── python -m compileall backend -q
  │   ├── python -c "import main"
  │   └── python -m pytest backend/tests -q --tb=short
  └── frontend job
      ├── npm ci
      └── npm run build (tsc -b + vite build)
```

---

## Environment Setup (CI-specific)

| Variable | CI Value | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./backend/ems_ci.db` | Test isolation — no PostgreSQL needed |
| `SECRET_KEY` | GitHub Actions secret | Never a real key in YAML |
| `JSON_LOGS` | `false` | Prevents structured log format breaking test capture |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Required by settings validation |

The test suite uses `SimpleNamespace` mocks and does not connect to a real DB.
SQLite is used only because `import main` triggers `database.py` engine setup.

---

## Secret Scan

The backend job checks that no `.env` files are committed. This is a
lightweight guard — for a full secret scan, add `gitleaks` or `trufflehog` as
a future enhancement.

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Python 3.11 (not 3.14) | CI must match a stable, widely supported runtime; 3.14 is too new for most pip packages to guarantee wheel availability |
| SQLite in CI | Tests are mock-based; PostgreSQL service container is unnecessary overhead |
| `--tb=short` in pytest | Compact failure output — full tracebacks available via `pytest --tb=long` locally |
| Two separate jobs (backend/frontend) | Failures are isolated; frontend team and backend team see independent CI status |
| `cache-dependency-path: frontend/package-lock.json` | Node cache is keyed on lockfile hash for reproducibility |
| No `--no-verify` anywhere | Pre-commit hook compliance is required, not optional |

---

## Local Equivalents

Run the exact same commands locally before pushing:

```bash
# Backend
python -m compileall backend -q
python -c "import sys; sys.path.insert(0,'backend'); import main"
python -m pytest backend/tests -q --tb=short

# Frontend
cd frontend && npm ci && npm run build
```

---

## Governance Rules

1. **CI must pass before merge** — no exceptions for "small" changes.
2. **Secrets never in YAML** — use GitHub repository secrets for `SECRET_KEY` and any DB credentials.
3. **No `.env` committed** — the CI secret scan will fail the build.
4. **No runtime DB files committed** — `*.db` in `backend/` produces a CI warning.
5. **Both jobs must pass** — a passing backend job does not compensate for a failing frontend build.

---

## Future Enhancements

| Enhancement | When |
|---|---|
| `gitleaks` secret scanning | After IT security review |
| Separate `lint` job (ruff / flake8) | After agreeing on a linting standard |
| Docker-based integration test | After PostgreSQL migration |
| Coverage report + badge | After test coverage baseline is set |
| Deploy-on-merge to staging | Requires staging environment provisioning |
