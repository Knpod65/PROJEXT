# D5.0 — Final Production Readiness Gap Audit
## EMS Academic Operations Platform — 2026-05-19

> Scope: codebase on `main` after D4 complete (1256 backend tests passing, frontend build clean).
> This file is the scoping artifact for D5 slices D5.1–D5.12. All findings below are classified
> CRITICAL / HIGH / MEDIUM / LOW / DEFERRED. Items addressed by a D5 slice are marked RESOLVED
> in that slice's commit; untouched items remain here for visibility.

---

## 1. CRITICAL

| ID | Item | Root cause | Conscious status |
|----|------|-----------|-----------------|
| C-1 | No PDPA runtime guard at response time | `pdpa_policy.py` classifies fields in isolation per file; no service enforces at every API response boundary. Every new analytics/export endpoint is a manual compliance review. | Untouched — D5.7 addresses |
| C-2 | No production deployment runbook | `RUNBOOK.md` covers local dev + restore + secret gen. Zero production deploy/rollback/degraded-mode/dependency-recovery docs. | Untouched — D5.9 addresses |
| C-3 | Public /health serializes exception class | `backend/routers/health.py` catches `Exception` and calls `str(e)` in HTTP body. Under `debug=true` or if any handler re-raises, traceback features leak to unauthenticated callers. | Untouched — D5.9 addresses |
| C-4 | No secrets-in-env startup validation | `backend/main.py` warns `SECRET_KEY not set` but does not hard-fail. Process starts normally with `change-me` default. `docker-compose.yml` ships `change-me` as PINNED default. | Untouched — D5.9 addresses |

---

## 2. HIGH

| ID | Item | Root cause | D5 slice |
|----|------|-----------|---------|
| H-1 | No audit visibility UI | Audit logs accessible only as export download (`GET /api/exports/audit-logs`). No event timeline, mutation lineage, or governance event viewer. | D5.8 |
| H-2 | No governance cockpit | Governance data lives in `governance_analytics_service`, `executive_risk_service`, `publication_governance_service`, `governance_trace_service`. No frontend aggregate view. | D5.1 |
| H-3 | No optimization trace explorer | D2 trace engine complete; no frontend UI to inspect trace lineage, rejected alternatives, constraint hits, or quality scoring. | D5.2 |
| H-4 | No operational health dashboard | No single view of: backend health, analytics health, integration readiness, publication readiness, queue/backlog, or audit pipeline health. | D5.4 |
| H-5 | Dockerfile has no startup readiness probe | HEALTHCHECK uses `curl localhost:8000/health` — ok. But Docker has no readiness gate; app accepts requests before DB connects. `--start-period=30s` is too short for Docker Postgres TCP handshake. | D5.9 |
| H-6 | Duplicate CI workflows | `ems-ci.yml` is DEPRECATED but still lives and still runs. `backend-validation.yml` + `frontend-validation.yml` are active but lack: doc-presence check, PDPA audit, bundle-size gate, secrets-scan. | D5.10 |
| H-7 | `nginx.conf` `server_name _` wildcard in production | Requests to any hostname are accepted. Opens DNS rebinding in shared hosting environments. | D5.9 |
| H-8 | Bundle still large (~668KB gzip) | No route-based code splitting. `Optimizer.tsx` (22KB), `Checkins.tsx` (29KB), `External.tsx` (20KB), `WorkflowV2.tsx` (21KB) all eager-loaded. | D5.6 |
| H-9 | `docker-compose.yml` parent-relative volume paths | `../../data/postgres` is relative to compose file location, not CWD. Fragile for non-standard directory depth. | D5.9 |

---

## 3. MEDIUM

| ID | Item | Root cause | D5 slice |
|----|------|-----------|---------|
| M-1 | No admin tooling for D3 configuration | `platform_config_export_service.py` and `platform_config_import_service.py` exist. No frontend page to view/validate multi-faculty config, workload policy, governance flow, integration contracts, or analytics metrics. | D5.3 |
| M-2 | Inconsistent loading/error UX across 37 pages | Most pages implement `if (isLoading) return <div>Loading...</div>` inline. `ErrorBoundary` is class-based (correct) but no shared `LoadingState` / `ErrorState` / `PermissionDeniedState` / `PDPARestrictedState` component library. | D5.5 |
| M-3 | i18n coverage not complete | D4/D5 pages have mixed raw-JSX labels. Bilingual requirement (Thai/English) not uniformly satisfied. | D5.5+ |
| M-4 | No structured startup logging | No STARTUP log phase with `app_version`, `git_sha`, `env`, `db_backend`, `feature_flags`. Logs begin mid-request. | D5.9 |
| M-5 | Frontend types have no PDPA enforcement | `@/types/analytics.ts` exposes `pdpa_level` strings but does not prevent callers from rendering `restricted`-level fields at component level. | D5.5 + D5.7 |
| M-6 | docker-compose.yml hardcoded weakest-credential defaults | `POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-change-me}` — ships as runtime default. No startup check warns when `ENV=production` with default credentials. | D5.9 |
| M-7 | SQLite WAL has no cleanup | `backend/database.py` configures WAL mode for dev SQLite. No documented or enforced WAL cleanup policy. | D5.9 |
| M-8 | `api.ts` has no retry/timeout defaults | `get()` wrapper has no timeout, no retry, no abort controller. Slow API calls block the React tree indefinitely. | D5.6 |

---

## 4. LOW

| ID | Item | D5 slice |
|----|------|---------|
| L-1 | `analytics.service.ts` does not cover `/api/analytics/metrics/values` if backend adds it | D5.x future |
| L-2 | 27 `<GuardedPage>` invocations — slight DRY debt | D5.x future |
| L-3 | `SESSION_COOKIE_DOMAIN = ""` — cookie never sent cross-domain | Documentation only |

---

## 5. DEFERRED

| ID | Item | Reason |
|----|------|--------|
| D-1 | Managed secrets infrastructure (Vault/AWS Secrets Manager) | Requires infra provisioning; env-var baseline is correct |
| D-2 | ML-powered optimization candidates | BYO solver still under active development |
| D-3 | Real SIS/LMS/HR real-time adapters | Contract modeling complete (D4.8); real adapters require IT/sign-off |
| D-4 | `scheduler.py` internal cron mutation audit logging | Gate owner approval required |
| D-5 | Router extraction in `optimize_workflow.py` (58K) and `schedule.py` (66K) | Progressive extraction continues; no breakage risk by continuing in-place |

---

## 6. D5 slice dependency graph

```
D5.0  Audit doc — no dependencies
D5.1  Governance cockpit      ← backend services existing
D5.2  Trace explorer          ← D2 trace engine existing
D5.3  Config admin            ← D3 export/import services existing
D5.4  Op health dashboard     ← health endpoint existing
D5.5  System states           ← needs ErrorBoundary review
D5.6  Performance hardening   ← build measurement first → lazy loading → timeout
D5.7  PDPA guard              ← audit D5.0 C-1, runs after Audit doc
D5.8  Audit explorer          ← thin proxy endpoints append-only to analytics router
D5.9  Deployment hardening    ← Docker/nginx/runbook files
D5.10 CI/CD foundation        ← reads existing workflows
D5.11 Exec reporting          ← reads all prior D5 docs
D5.12 Stabilization           ← must run last; fixes any slice regressions
```

---

## 7. D5 final targets

| Dimension | Target |
|---|---|
| Architecture maturity | 99+/100 |
| DRY maturity | 97–99/100 |
| Governance | 98–99/100 |
| Optimization | 95–98/100 |
| Analytics | 92–96/100 |
| Deployment readiness | 92–97/100 |
| PDPA maturity | 94–97/100 |
| Observability | 85–90/100 |
| Overall | 99.7+/100 |
