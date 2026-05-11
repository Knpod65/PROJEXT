# EMS Architecture Map
## Academic Operations Intelligence Platform — System Topology & Module Registry

> **Audience:** New engineers onboarding, architects making cross-cutting changes, AI coding assistants
> **Scope:** System topology, module registry, data flows, startup sequence, coupling hotspots
> **Do NOT look here for:** Role permission tables (→ `docs/ROLE_SYSTEM.md`), data retention (→ `docs/PDPA_SECURITY_GUIDE.md`)

---

## 1. System Topology

```
┌─────────────────────────────────────────────────────────────────────┐
│  Browser                                                            │
│  React 18 SPA  (Vite build → /static/index.html)                   │
│  React Router v6 │ Context API │ TypeScript │ i18n (TH/EN)         │
└──────────────┬──────────────────────────────────────────────────────┘
               │  HTTPS  (port 443 / 80 → nginx)
┌──────────────▼──────────────────────────────────────────────────────┐
│  Nginx Reverse Proxy  (nginx.conf)                                  │
│  • /app  /static → serve frontend build                            │
│  • /api/* → proxy_pass → FastAPI :8000                             │
│  • CSP header on the active HTTP block                             │
└──────────────┬──────────────────────────────────────────────────────┘
               │  HTTP (internal Docker network)
┌──────────────▼──────────────────────────────────────────────────────┐
│  FastAPI Application  (backend/main.py)                             │
│  Middleware stack (outermost → innermost):                         │
│    1. RequestLoggingMiddleware  (correlation ID, duration_ms)      │
│    2. SecurityHeadersMiddleware (X-Content-Type-Options etc.)      │
│    3. LoginRateLimitMiddleware  (in-memory, per-IP)                │
│    4. CORSMiddleware            (ALLOWED_ORIGINS from env)         │
│                                                                     │
│  26 API Routers  (see Router-to-Domain Map below)                  │
│  CMU SSO sidecar  (/api/auth/sso/*)                                │
└──────────────┬──────────────────────────────────────────────────────┘
               │  SQLAlchemy ORM  (database.py)
┌──────────────▼──────────────────────────────────────────────────────┐
│  Database                                                           │
│  Development:  SQLite  (backend/ems.db)                            │
│  Production:   PostgreSQL  (docker-compose.yml, POSTGRES_* env)    │
│  48 tables, 20+ enum types, UTC timestamps throughout              │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  External Integrations                                              │
│  • CMU SSO   — OAuth2-style SSO via cmu_sso.py                    │
│  • SMTP      — email_notifications.py (digest emails)             │
│  • OR-Tools  — CP-SAT optimizer inside optimize_workflow.py        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Backend Module Registry

All 36 Python modules in `backend/`. **Role** column: router / utility / model / config / pipeline.

| Module | Role | Key Imports / Dependencies | Notes |
|--------|------|---------------------------|-------|
| `main.py` | entry | all routers, security, logging_config | App factory, middleware, lifespan |
| `models.py` | model | sqlalchemy, database, academic_groups | 48 ORM classes, 20+ enums |
| `database.py` | config | sqlalchemy | Engine, Session factory, `get_db()` |
| `auth_utils.py` | utility | models, database, academic_groups | JWT, bcrypt, `get_current_user`, `log_action`, `SIGN_ORDER_USERNAMES` |
| `permissions.py` | utility | models, database, auth_utils (lazy) | RBAC role sets, object-level auth, **`build_dependencies()`** |
| `security.py` | utility | — | Input sanitization, cookie management, IP extraction |
| `cmu_sso.py` | router | fastapi, httpx | CMU SSO OAuth2 integration |
| `logging_config.py` | config | logging, contextvars | Structured JSON logging, `_request_id_var`, `_user_id_var` |
| `term_lifecycle.py` | utility | models | **Reference implementation** — pure state machine, no HTTP concerns |
| `academic_groups.py` | utility | — | `GOV/PA/IR/STB` dept classification, `can_access_academic_group()` |
| `exam_ownership.py` | utility | models, database | Teacher→section ownership queries |
| `staff_workloads.py` | utility | models, auth_utils | Duty allocation, `PAPER_DISTRIBUTION_*` hardcoded constants |
| `exam_pdf_processor.py` | utility | pdf libs | PDF metadata extraction |
| `exam_pickup.py` | utility | models, auth_utils | QR token generation and check-in logic |
| `email_notifications.py` | utility | smtplib | SMTP client, digest emails |
| `operational_documents.py` | utility | docx, jinja2 | Document template handling |
| `gen_docs.py` | utility | operational_documents, reportlab | DOCX/PDF generation |
| `time_ranges.py` | utility | — | Time slot parsing, `ranges_overlap()` |
| `schemas.py` | model | pydantic | Request/response Pydantic models |
| `import_v2/importer.py` | pipeline | models, validators, normalizers | Main import orchestrator |
| `import_v2/validators.py` | pipeline | models | Row-level validation rules (25+ rules) |
| `import_v2/parsers.py` | pipeline | pandas | Excel/CSV parsing |
| `import_v2/normalizers.py` | pipeline | — | Data normalization |
| `import_v2/file_cache.py` | pipeline | — | Import file caching |
| `config/retention_policy.py` | config | — | PDPA retention periods, dry-run cleanup |
| `seed.py` | pipeline | models | Dev data seeding |
| `historical_schedule_import.py` | pipeline | models | Legacy schedule import |
| `migrate_v2.py` | pipeline | sqlalchemy, models | Main schema migration runner |
| `migrate_*.py` (23 files) | pipeline | sqlalchemy | Targeted schema migrations |

---

## 3. Router-to-Domain Map

26 routers grouped into 9 business domains.

### Domain: Identity & Auth
| Router | Prefix | Key Endpoints |
|--------|--------|---------------|
| `auth.py` | `/api/auth` | POST /login, GET /me, POST /view-as, POST /logout |
| `cmu_sso.py` | `/api/auth/sso` | SSO callback, token exchange |
| `users.py` | `/api/users` | CRUD users, GET /teachers |

### Domain: Term Lifecycle
| Router | Prefix | Key Endpoints |
|--------|--------|---------------|
| `period.py` | `/api/period` | GET /all, POST /, PUT /{id}, POST /{id}/close |
| `settings.py` | `/api/settings` | GET /, PUT / (deadlines, flags, retention config) |
| `scheduler.py` | `/api/scheduler` | Internal job triggers |

### Domain: Academic Data
| Router | Prefix | Key Endpoints |
|--------|--------|---------------|
| `courses.py` | `/api/courses` | GET /, GET /sections, POST /sections |
| `imports_v2.py` | `/api/import/v2` | POST /start, POST /validate, POST /commit |
| `imports.py` | `/api/import` | Legacy import endpoints |

### Domain: Exam Scheduling
| Router | Prefix | Key Endpoints |
|--------|--------|---------------|
| `schedule.py` | `/api/schedule` | GET /, POST /, PUT /{id}, POST /optimize, GET /grouped |
| `co_exam.py` | `/api/co-exam` | GET /, POST /, POST /auto-detect |
| `external_exams.py` | `/api/external` | POST /, PUT /{id}, POST /{id}/assign |

### Domain: Submission & Approval
| Router | Prefix | Key Endpoints |
|--------|--------|---------------|
| `submissions.py` | `/api/submissions` | Multi-step wizard (Step1–Step4), approve, reject |
| `exam_manager.py` | `/api/exam-manager` | PUT /section/{id}/ownership, GET /my-sections |
| `documents.py` | `/api/documents` | POST /generate/{sid}, POST /preview-pdf/{sid} |

### Domain: Staff Operations
| Router | Prefix | Key Endpoints |
|--------|--------|---------------|
| `optimize_workflow.py` | `/api/workflow` | POST /session/init, POST /session/sign, GET /staff-workload |
| `swaps_v2.py` | `/api/swaps2` | POST /, GET /, PUT /{id}/confirm |
| `checkins.py` | `/api/checkins` | GET /schedule/{id}, POST /confirm, POST /pickup/scan |
| `dashboard.py` | `/api/dashboard` | GET /, GET /analytics |

### Domain: Print Queue
| Router | Prefix | Key Endpoints |
|--------|--------|---------------|
| `printing.py` | `/api/printing` | POST /queue, GET /queue |

### Domain: Export Center
| Router | Prefix | Key Endpoints |
|--------|--------|---------------|
| `exports.py` | `/api/exports` | GET /schedule, GET /workload-summary-pdf |
| `exports_excel.py` | `/api/exports` | GET /schedule-excel, GET /submissions-excel |
| `pdf.py` | `/api/pdf` | POST /token/{sid}, GET /download/{token} |

### Domain: Public & Historical
| Router | Prefix | Key Endpoints |
|--------|--------|---------------|
| `public.py` | `/api/public` | GET /schedule (no auth, student-facing) |
| `historical_schedules.py` | `/api/historical-schedules` | GET /overview, GET /workload, GET /comparison |

---

## 4. Frontend Module Registry

| Layer | Count | Location | Notes |
|-------|-------|----------|-------|
| Pages | 35+ | `frontend/src/pages/` | Route-level components |
| Components | 60+ | `frontend/src/components/` | `ui/` (generic) and `domain/` (business) |
| Services | 25+ | `frontend/src/services/` | API client wrappers, one per domain |
| Hooks | 11 | `frontend/src/hooks/` | Data-fetching and UI state hooks |
| Stores | 3 | `frontend/src/store/` | auth, ui, period |
| i18n | 2 | `frontend/src/i18n/` | en.ts, th.ts (600+ keys each) |
| Types | 10+ | `frontend/src/types/` | TypeScript interface definitions |
| Utils | 5 | `frontend/src/utils/` | format, roles, gps, cx, academicGroups |
| Theme | 1 | `frontend/src/theme/` | `roleThemes.ts` — role-scoped CSS variables |
| Config | 1 | `frontend/src/config/navigation.ts` | Route → page metadata mapping |

### Page-to-Router Correspondence (key pages)

| Frontend Page | Backend Router | Domain |
|---------------|----------------|--------|
| `Dashboard.tsx` | `dashboard.py` | Staff Operations |
| `Schedule.tsx` | `schedule.py` | Exam Scheduling |
| `Optimizer.tsx` | `optimize_workflow.py` | Staff Operations |
| `Submissions.tsx` | `submissions.py` | Submission & Approval |
| `WorkflowV2.tsx` | `optimize_workflow.py` | Staff Operations |
| `SwapsV2.tsx` | `swaps_v2.py` | Staff Operations |
| `Checkins.tsx` | `checkins.py` | Staff Operations |
| `ImportV2.tsx` | `imports_v2.py` | Academic Data |
| `ExportCenter.tsx` | `exports.py`, `exports_excel.py` | Export Center |
| `ExamManager.tsx` | `exam_manager.py` | Submission & Approval |
| `Period.tsx` | `period.py` | Term Lifecycle |
| `SettingsV2.tsx` | `settings.py` | Term Lifecycle |
| `UsersV2.tsx` | `users.py` | Identity & Auth |

---

## 5. Data Flow Paths

### Flow A — Auth & Session
```
Browser
  → POST /api/auth/login  {username, password}
  → auth.py validates credentials (bcrypt)
  → create_token()  →  JWT (HS256, 12h)
  → set_auth_cookie()  →  HttpOnly "ems_session" cookie
  → Browser stores cookie (no JS access)

Subsequent requests:
  → Cookie extracted by _get_request_token()
  → _resolve_user_from_token() decodes JWT
  → is_token_revoked() checks blacklist
  → User object injected via Depends(get_current_user)

Logout:
  → POST /api/auth/logout
  → revoke_token()  →  RevokedToken row inserted
  → delete_auth_cookie()  →  cookie cleared
```

### Flow B — Import Pipeline (V2)
```
Admin uploads Excel/CSV
  → POST /api/import/v2/start   (upload file, select data type)
  → import_v2/parsers.py        (read file, normalize columns)
  → POST /api/import/v2/validate (row-level validation, 25 rules)
  → import_v2/validators.py     (returns issue list per row)
  → UI shows preview with errors, admin selects rows + overrides
  → POST /api/import/v2/commit  (selected_rows, overrides)
  → import_v2/normalizers.py    (clean data)
  → import_v2/importer.py       (upsert to DB)
  → ImportSession + ImportRowLog written (audit trail)
```

### Flow C — Optimizer → Workflow → Signed
```
Admin initiates optimizer
  → POST /api/workflow/session/init
  → optimize_workflow.py builds CP-SAT problem (OR-Tools)
  → ExamSchedule + Supervision rows generated
  → OptimizeSession record created (status=draft)

Admin reviews, then signs
  → POST /api/workflow/session/sign
  → Checks SIGN_ORDER_USERNAMES (round-based signing)
  → Status progresses: draft → round1 → swap_open → round2 → complete

Swap window
  → POST /api/swaps2/  (staff requests swap)
  → PUT  /api/swaps2/{id}/confirm  (approved/rejected)
  → 1 valid swap per slot enforced, conflicts auto-removed
```

### Flow D — Teacher Submission → Approval → Print
```
Teacher
  → PUT /api/submissions/{id}/step1  (confirm exam date)
  → PUT /api/submissions/{id}/step2  (exam type: online/onsite/no-exam)
  → PUT /api/submissions/{id}/step3  (metadata: duplex, staple, extras)
  → POST /api/submissions/{id}/upload (PDF file)
  → PUT /api/submissions/{id}/submit (finalize)

Admin/ESQ approval
  → PUT /api/submissions/{id}/approve  (ExamSubmissionVersion snapshot created)
  → PUT /api/submissions/{id}/reject   (returns to teacher)

Print queue
  → POST /api/printing/queue  (PrintQueueJob created from submission)
  → print_shop role manages queue via /api/printing/queue
```

---

## 6. Startup Sequence

The `lifespan` function in `main.py` (lines 31–43) runs on startup:

```python
async def lifespan(app: FastAPI):
    # Step 1 — Security validation (crashes on bad SECRET_KEY in production)
    validate_production_secrets()

    # Step 2 — Create DB tables
    Base.metadata.create_all(bind=engine)

    # Step 3 — Seed dev data
    seed_data(db)

    # ⚠️  MISSING STEP — permissions.build_dependencies() is NOT called
    # This means require_admin / require_staff_or_admin / require_view_all
    # in permissions.py remain as NotImplementedError stubs until called.
    # Most routers import from auth_utils.py instead, which has working
    # equivalents — masking the bug. Fix: add this call here.
    # from permissions import build_dependencies; build_dependencies()
    yield
```

**Critical:** `permissions.build_dependencies()` must be added as Step 4. Without it, any router
that imports `require_admin` from `permissions` (not `auth_utils`) will raise `NotImplementedError`
on the first request. This is a latent production defect.

**Middleware ordering** (applied innermost-to-outermost in Starlette):
```
Request  →  CORS  →  LoginRateLimit  →  SecurityHeaders  →  RequestLogging  →  Route Handler
Response ←  CORS  ←  LoginRateLimit  ←  SecurityHeaders  ←  RequestLogging  ←  Route Handler
```

---

## 7. Known Coupling Hotspots

### Hotspot 1: `auth_utils.py` vs `permissions.py` Duplication

Both modules define the same abstractions. Routers import from whichever they were
written against, creating two divergent sources of truth:

| Function | `auth_utils.py` | `permissions.py` |
|----------|-----------------|-----------------|
| `get_effective_role()` | ✅ line 252 | ✅ line 45 |
| `get_dept_filter()` | ✅ line 316 | ✅ line 51 |
| `require_admin()` | ✅ line 264 | ✅ stub (line 69) |
| `require_staff_or_admin()` | ✅ line 269 | ✅ stub (line 73) |
| `require_view_all()` | ✅ line 295 | ✅ stub (line 77) |
| `VIEW_ALL_ROLES` | ❌ inline checks | ✅ line 18 |

**Resolution:** `permissions.py` should be the single source of truth. `auth_utils.py` functions
should be removed after consolidation in Phase 2.

### Hotspot 2: `SIGN_ORDER_USERNAMES` Cross-Domain Reference

`SIGN_ORDER_USERNAMES = ["atikant.s", "mathawee.m", "napaporn.ph", "paweena.t"]` lives in
`auth_utils.py` (line 473) but is a business rule for the workflow domain. It is consumed by
`optimize_workflow.py` router. This creates a dependency from the Workflow domain into the
Identity module. Planned resolution: move to a database-backed `WorkflowSignerConfig` table
(Phase 2 / Phase 6 prerequisite).

### Hotspot 3: `_coerce_user_role()` is Private but Needed System-Wide

`auth_utils.py` line 103 defines `_coerce_user_role()` (private, with underscore prefix).
Multiple routers (`optimize_workflow.py`, `users.py`) independently implement the same
`try: models.UserRole(value) except ValueError:` pattern. Fix: make it public in
`permissions.py` as `coerce_user_role()`.

### Hotspot 4: Route Registration in `main.py` is Manual

28 routers are included by hand (lines 184–211). No auto-discovery. When a new router is
added, `main.py` must be manually updated. Not a bug, but a maintenance risk as the system
grows toward multi-faculty.

### Hotspot 5: `academic_groups.py` is Imported by `models.py`

`models.py` line 12 imports from `academic_groups.py` for `@property` computations. This
creates a startup-time dependency from the data model layer into a business utility. When
`models.py` is imported (at every module load), `academic_groups.py` runs. The department
code hardcoding in `academic_groups.py` (`GOV/PA/IR/STB`) therefore affects the model layer
directly — a risk for multi-faculty migration.
