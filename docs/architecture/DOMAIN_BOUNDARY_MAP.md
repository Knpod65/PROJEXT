# Domain Boundary Map
## EMS — Bounded Contexts, Ownership Rules, and Cross-Boundary Violations

> **Audience:** Engineers adding features, architects deciding where logic belongs
> **Scope:** Domain inventory, dependency rules, current violations, shared kernel, anti-corruption layer rules
> **NOT a data model doc** — see `docs/DATA_MODEL.md` for that

---

## 1. Domain Inventory

Nine bounded contexts, each with a clear ownership mandate.

### Domain 1 — Identity & Auth
**Owns:** User accounts, roles, authentication tokens, impersonation, SSO integration
**Files:** `backend/auth_utils.py`, `backend/permissions.py`, `backend/security.py`, `backend/cmu_sso.py`, `backend/routers/auth.py`, `backend/routers/users.py`
**Tables:** `users`, `revoked_tokens`
**Invariants:**
- Only this domain creates/modifies `User` records
- JWT tokens are created and revoked exclusively here
- Role capability sets (`VIEW_ALL_ROLES`, `WRITE_ROLES`, `SIGNER_ROLES`) are defined once in `permissions.py`

---

### Domain 2 — Term Lifecycle
**Owns:** Academic periods, lifecycle transitions (draft → active → archived → locked), settings
**Files:** `backend/term_lifecycle.py`, `backend/routers/period.py`, `backend/routers/settings.py`, `backend/config/retention_policy.py`
**Tables:** `exam_periods`, `system_settings`
**Invariants:**
- A locked period is immutable — no domain may write to data scoped to a locked period
- Only this domain calls `mark_period_active()`, `mark_period_archived()`, `mark_period_locked()`
- All other domains must call `ensure_period_record_editable()` before mutating period-scoped data

---

### Domain 3 — Academic Data
**Owns:** Course catalog, section enrollment, import sessions, lecturer name maps
**Files:** `backend/routers/courses.py`, `backend/routers/imports_v2.py`, `backend/routers/imports.py`, `backend/import_v2/` (all), `backend/academic_groups.py`
**Tables:** `courses`, `sections`, `students`, `enrollments`, `enrollment_records`, `import_sessions`, `import_row_logs`, `lecturer_name_maps`
**Invariants:**
- Section creation/modification must go through this domain
- Import sessions are the only authoritative source for bulk data mutations
- `academic_groups.py` classification rules (`GOV/PA/IR/STB`) belong here; they must NOT leak into other domains

---

### Domain 4 — Exam Scheduling
**Owns:** Exam date/time/room assignments, co-exam groups, external exams
**Files:** `backend/routers/schedule.py`, `backend/routers/co_exam.py`, `backend/routers/external_exams.py`, `backend/time_ranges.py`
**Tables:** `exam_schedules`, `co_exam_groups`, `co_exam_members`, `external_exams`, `external_supervisions`
**Invariants:**
- Room capacity must be ≥ student count before an `ExamSchedule` record is confirmed
- Co-exam groups are resolved before optimizer runs
- External exams have their own staffing path independent of the optimizer

---

### Domain 5 — Submission & Approval
**Owns:** Teacher exam file submission, version history, PDF access tokens, exam ownership
**Files:** `backend/routers/submissions.py`, `backend/routers/exam_manager.py`, `backend/routers/documents.py`, `backend/routers/pdf.py`, `backend/exam_ownership.py`, `backend/exam_pdf_processor.py`
**Tables:** `exam_submissions`, `exam_submission_versions`, `exam_material_requests`, `section_exam_managers`, `exam_access_tokens`, `exam_access_logs`, `pdf_tokens`, `exam_messages`
**Invariants:**
- A teacher may only access submissions for sections they own
- Submission status transitions follow a strict state machine (see `WORKFLOW_STATE_MACHINE.md`)
- PDF access requires a time-bounded `ExamAccessToken` — direct file access is forbidden

---

### Domain 6 — Staff Operations
**Owns:** Optimizer sessions, invigilator assignments, staff workloads, swaps, check-ins, QR pickup
**Files:** `backend/routers/optimize_workflow.py`, `backend/routers/swaps_v2.py`, `backend/routers/checkins.py`, `backend/routers/dashboard.py`, `backend/staff_workloads.py`, `backend/exam_pickup.py`
**Tables:** `supervisions`, `optimize_sessions`, `swap_requests`, `checkin_events`, `exam_pickup_qr_tokens`, `exam_pickup_checkins`, `staff_unavailability`, `room_unavailability`, `paper_distribution_assignments`, `supervision_baselines`
**Invariants:**
- Optimizer may only run when the period is in `active` status
- Only 1 valid swap per time slot is permitted; conflicting swaps are auto-cancelled
- QR tokens have a defined lifecycle: `issued → scanned → confirmed/expired`

---

### Domain 7 — Print Queue
**Owns:** Print job tracking, copy counts, dispatch
**Files:** `backend/routers/printing.py`
**Tables:** `print_queue_jobs`, `printshop_users`
**Invariants:**
- Print jobs are created from approved submissions only
- Copy counts are not accessible to `staff` role (PDPA)
- Print shop users have a dedicated role (`print_shop`) separate from staff

---

### Domain 8 — Export Center
**Owns:** PDF/Excel generation, workload summary, compensation calculation
**Files:** `backend/routers/exports.py`, `backend/routers/exports_excel.py`, `backend/gen_docs.py`, `backend/operational_documents.py`
**Tables:** (no owned tables — reads from other domains)
**Invariants:**
- Every export involving PII must be logged in `audit_logs`
- Period resolution follows the canonical `_resolve_period()` pattern (see `IMPORT_EXPORT_GOVERNANCE.md`)
- Export availability depends on upstream data completeness (no submissions → no submission export)

---

### Domain 9 — Historical Archive
**Owns:** Permanent snapshots of optimization results and schedule history
**Files:** `backend/routers/historical_schedules.py`, `backend/historical_schedule_import.py`
**Tables:** `historical_schedule_batches`, `historical_schedule_entries`, `historical_schedule_invigilators`, `historical_distribution_slots`
**Invariants:**
- Historical records are write-once; no update or delete allowed
- Retention policy: `permanent` (never purged — institutional record)
- Historical data is always visible regardless of period lock status

---

## 2. Domain Dependency Graph

Arrows mean "may call into / query from". No circular dependencies are allowed.

```
┌─────────────────────────────────────────────────────────┐
│                   Shared Kernel                         │
│  ExamPeriod lifecycle (term_lifecycle.py)               │
│  UserRole enum (models.py)                              │
│  Role capability sets (permissions.py)                  │
│  AuditLog writing (auth_utils.log_action)               │
└────────────────────────┬────────────────────────────────┘
                         │  (all domains may read from shared kernel)
     ┌───────────────────┼───────────────────────────────┐
     │                   │                               │
     ▼                   ▼                               ▼
Identity & Auth    Term Lifecycle              Academic Data
     │                   │                               │
     │                   │ (period status check)         │ (sections/enrollments)
     │                   ▼                               ▼
     │             Exam Scheduling ◄─────────────────────┘
     │                   │
     │                   │ (schedule assignments)
     │                   ▼
     │          Submission & Approval
     │                   │
     │                   │ (approved submissions → print jobs)
     │                   ▼
     │              Print Queue
     │
     │         Staff Operations ◄──── Exam Scheduling (schedule ids)
     │                   │
     │                   │ (approved workflow state → export eligibility)
     │                   ▼
     │            Export Center ◄──── Submission & Approval
     │                   │
     │                   ▼
     │          Historical Archive (snapshot on period lock)
     │
     └──────► (Identity: user lookups only — all domains)
```

**Rule:** An arrow going "upward" (e.g., Term Lifecycle calling Submission) is a violation.
Lower-tier domains must not import from higher-tier domains.

---

## 3. Current Cross-Boundary Violations

These are concrete violations found in the codebase that must be addressed in Phase 3.

### Violation 1 — `submissions.py` Contains Print Priority Logic
**File:** `backend/routers/submissions.py`, function `_get_print_priority()` (lines ~121–134)
**What it does:** Computes print queue priority based on student count thresholds: 120→high, 70→medium, 15→normal, else→low
**Where it belongs:** Domain 7 (Print Queue), specifically in `backend/services/print_service.py`
**Risk:** Print thresholds are hardcoded in the wrong layer; changing them requires searching submissions.py

### Violation 2 — `schedule.py` Contains Dept Filtering Logic
**File:** `backend/routers/schedule.py`, function `_build_schedule_query()` (lines ~69–96)
**What it does:** Applies `dept_code` filtering based on role — duplicating logic from `permissions.get_dept_filter()`
**Where it belongs:** Domain 1 (Identity & Auth), via `permissions.get_dept_filter()` which already exists
**Risk:** Two inconsistent dept-filtering implementations; fixing one misses the other

### Violation 3 — `optimize_workflow.py` Contains User CRUD
**File:** `backend/routers/optimize_workflow.py` (lines ~87–147)
**What it does:** Full `User` create/update operations — username uniqueness checks, role coercion, password hashing
**Where it belongs:** Domain 1 (Identity & Auth), specifically `backend/routers/users.py`
**Risk:** User management logic is split across two routers; authorization rules differ

### Violation 4 — `exports.py` and `pdf.py` Both Contain `_resolve_period()`
**Files:** `backend/routers/exports.py` (lines ~17–29), `backend/routers/pdf.py`
**What it does:** Resolves an `ExamPeriod` from `(semester, academic_year, exam_type)` with fallback to active
**Where it belongs:** Domain 2 (Term Lifecycle), as `term_lifecycle.resolve_export_period()`
**Risk:** Period resolution rules diverge silently; a bug fix in one file misses the other

### Violation 5 — `staff_workloads.py` Contains Person-Specific Exclusions
**File:** `backend/staff_workloads.py` (lines 14–16)
**What it does:** `PAPER_DISTRIBUTION_EXCLUDED_USERNAMES = {"araya.fa", "sapanyu.wong"}` — named individuals excluded from paper distribution
**Where it belongs:** A database-backed `StaffExclusionRule` table with `faculty_id` scope
**Risk:** Personnel changes require code changes; violates separation of config from logic

### Violation 6 — `auth_utils.py` Owns `SIGN_ORDER_USERNAMES`
**File:** `backend/auth_utils.py` (line 473)
**What it does:** `["atikant.s", "mathawee.m", "napaporn.ph", "paweena.t"]` — workflow signing order for Domain 6
**Where it belongs:** Domain 6 (Staff Operations) business rule, stored in a `WorkflowSignerConfig` table
**Risk:** Adding a new signer requires a code deployment; signer order is faculty-specific (multi-faculty blocker)

---

## 4. Shared Kernel

These objects legitimately cross domain boundaries. Domains may use them freely.

| Object | Location | Used by all domains for |
|--------|----------|------------------------|
| `ExamPeriod` model | `models.py` | Period-scoping all data |
| `UserRole` enum | `models.py` | Role-based decisions everywhere |
| `VIEW_ALL_ROLES`, `WRITE_ROLES`, `SIGNER_ROLES` | `permissions.py` | Role capability checks |
| `term_lifecycle.get_period_status()` | `term_lifecycle.py` | Read period state safely |
| `term_lifecycle.ensure_period_record_editable()` | `term_lifecycle.py` | Guard before any mutation |
| `permissions.get_effective_role()` | `permissions.py` | Resolve admin impersonation |
| `permissions.get_dept_filter()` | `permissions.py` | Dept-scoped query filtering |
| `auth_utils.log_action()` | `auth_utils.py` | Audit logging |
| `models.AuditLog` | `models.py` | Audit record storage |

---

## 5. Anti-Corruption Layer Rules

Enforced rules for what route handlers are **NOT** allowed to contain:

| Forbidden in route handlers | Reason | Correct location |
|----------------------------|--------|------------------|
| Numeric threshold constants (`120`, `70`) | Business rule leakage | `config/settings.py` or service |
| Person-specific username lists | Config-as-code | Database-backed config table |
| Magic role strings (`"distributor"`, `"chief"`) | Enum bypass | `models.SupervisionRole` enum |
| `try: models.UserRole(value) except ValueError:` | Validation leakage | `permissions.coerce_user_role()` |
| Inline dept_code filtering (`if user.role == teacher and user.dept_code`) | Permission logic in handler | `permissions.get_dept_filter()` |
| Direct `db.query(User)` for ownership checks | Ownership logic in handler | `permissions.assert_submission_access()` or service |
| `db.commit()` inside a service function | Transaction boundary violation | Router layer only |
| `HTTPException` raised inside a service function | HTTP concern in business layer | Raise domain exception; router translates |
| Bilingual error strings in service logic | Localization in wrong layer | i18n keys, resolved at HTTP boundary |

---

## 6. Invariant Enforcement Checklist

When adding a new feature, verify:

- [ ] Does it write to period-scoped data? → Call `ensure_period_record_editable()` first
- [ ] Does it filter by role? → Use `permissions.get_dept_filter()` and `permissions.get_effective_role()`
- [ ] Does it access a submission? → Use `permissions.assert_submission_access()`
- [ ] Does it create/modify a User? → Route through Identity domain only
- [ ] Does it expose PII? → Log via `auth_utils.log_action()` before returning response
- [ ] Does it belong to a domain that doesn't own the table it's querying? → It belongs in a different domain or the shared kernel
