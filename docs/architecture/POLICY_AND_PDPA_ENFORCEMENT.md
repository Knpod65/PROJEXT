# Policy and PDPA Enforcement
## EMS — How Data Protection is Enforced in Code

> **Audience:** Security reviewers, compliance officers, engineers adding new endpoints
> **Scope:** Enforcement mechanics, gap analysis, permission matrix, sensitive data flows, PDPA checklist
> **EXTENDS** `docs/PDPA_SECURITY_GUIDE.md` — do NOT duplicate data classification tables or cookie mechanics from there
> **Reference files:** `backend/config/retention_policy.py`, `backend/auth_utils.py` (log_action), `backend/models.py` (AuditLog), `backend/security.py`

---

## 1. Current Enforcement Status

| PDPA Control | Status | Location | Gap |
|-------------|--------|----------|-----|
| HttpOnly cookie for auth | ✅ Implemented | `security.py:set_auth_cookie()` | None |
| JWT token blacklist | ✅ Implemented | `auth_utils.revoke_token()` + `RevokedToken` table | None |
| Input sanitization | ✅ Implemented | `security.py:sanitize_text()` | Usage inconsistent in older routes |
| IP anonymization in audit logs | ✅ Implemented | `security.py:hash_ip()` → stored as SHA-256 hash | Raw IP never stored |
| Role-based access guards | ✅ Implemented | `auth_utils.require_admin()` + route dependencies | See Permission Matrix |
| Object-level access (submissions) | ✅ Implemented | `permissions.assert_submission_access()` | Not used for checkins/swaps |
| Object-level access (schedules) | ✅ Implemented | `permissions.assert_schedule_supervisor()` | Not used for co-exam groups |
| Audit logging of mutations | ⚠️ Partial | `auth_utils.log_action()` | ~30 mutation endpoints missing calls |
| Student data masking (copy count) | ✅ Implemented | `CopyPage` role-gates copy count column | Staff cannot see counts |
| Export audit logging | ✅ Implemented | Noted in PDPA_SECURITY_GUIDE.md §Export Logging | 11 export types logged |
| QR token lifecycle | ✅ Implemented | `exam_pickup.py` + `ExamPickupQrToken` | None |
| Data retention config | ⚠️ Partial | `config/retention_policy.py` | `RETENTION_CLEANUP_ENABLED = False` |
| Retention cleanup execution | ❌ Not activated | `retention_policy.py:run_cleanup()` | Dry-run only; admin sign-off required |
| SECRET_KEY validation | ✅ Implemented | `security.py:validate_production_secrets()` | Dev fallback warns but continues |
| CSP header | ✅ Implemented | `nginx.conf` (active HTTP block) | Not on FastAPI layer directly |
| PII in error messages | ✅ Implemented | Generic error messages; no PII in 500 responses | None |
| Session fixation prevention | ✅ Implemented | New token issued on login; old revoked on logout | None |

---

## 2. Specific Gaps Found

### Gap 1: Incomplete Audit Logging (CRITICAL for compliance)

`auth_utils.log_action()` exists and is called in many places, but the coverage is not complete.
Mutation endpoints confirmed to be **missing** audit log calls (found by cross-referencing
router files):

| Router | Missing Audit Events |
|--------|---------------------|
| `schedule.py` | Room assignment updates, schedule deletion |
| `co_exam.py` | Co-exam group creation, member addition |
| `external_exams.py` | External exam deletion, staff assignment removal |
| `swaps.py` (legacy) | Swap rejection |
| `period.py` | Period creation, period archival |
| `settings.py` | Settings update (retention config change) |
| `users.py` | User deactivation |

**Fix:** Use `audit_service.record()` (Phase 3) with an `ACTION_REGISTRY` to ensure every
mutation endpoint is logged. Add an automated test that enumerates all `PUT/POST/DELETE`
routes and asserts `audit_logs` grows by ≥1 row after each call.

---

### Gap 2: Retention Cleanup Disabled

`backend/config/retention_policy.py` defines `RETENTION_CLEANUP_ENABLED = False`.
The cleanup functions (`purge_old_student_schedules()`, `purge_revoked_tokens()`, etc.) are
fully implemented and include a `generate_dry_run_report()` function. They are safe to run.
The flag is `False` because admin sign-off on the retention periods has not been confirmed.

**Activation procedure** (see Section 7 of this document).

---

### Gap 3: Object-Level Authorization Not Applied to Check-ins and Swaps

`permissions.py` has `assert_submission_access()` and `assert_schedule_supervisor()` but there
are no equivalent assertions for:
- `CheckinEvent` — any `staff` can access any check-in event
- `SwapRequest` — any `staff` can view any swap (even others')
- `ExternalExam` staff assignment — no ownership check

**Fix (Phase 4):** Add `assert_checkin_access()` and `assert_swap_request_access()` to
`permissions.py` following the same pattern as existing assert functions.

---

### Gap 4: User ID Not Propagated to Middleware Logs

`RequestLoggingMiddleware` in `main.py` logs HTTP requests to the structured logger but does
not include `user_id` in the log line (the `_user_id_var` context variable is declared in
`logging_config.py` but never set during request processing).

**Fix (Phase 4):** After `get_current_user()` resolves in `RequestLoggingMiddleware`,
call `_user_id_var.set(user.id)` so all log lines for that request carry the actor ID.

---

## 3. Permission Enforcement Matrix

For each role: what data they can read (R) and write (W), and which layer enforces it.

Legend: ✅ Enforced | ⚠️ Partial | ❌ Not enforced | `-` Not applicable

| Data Type | admin | esq_head | secretary | dept_supervisor | staff | teacher | print_shop | Enforcement Layer |
|-----------|-------|----------|-----------|-----------------|-------|---------|------------|-------------------|
| All `User` records | R/W | R | R | - | - | - | - | Route dep (`require_admin`) |
| Own `User` record | R | R | R | R | R | R | R | JWT claims |
| All `Section` records | R/W | R | R | R (own dept) | R | R (own) | - | Query filter (`get_dept_filter`) |
| `ExamSubmission` (list) | R/W | R | R | R | - | R (own) | - | `assert_submission_access` |
| `ExamSubmission` (approve) | W | - | - | - | - | - | - | Route dep (`require_admin`) |
| `ExamSchedule` (view) | R | R | R | R | R | R | - | Route dep + dept filter |
| `ExamSchedule` (create/update) | W | - | - | - | - | - | - | Route dep (`require_admin`) |
| `Supervision` assignments | R/W | R | R | R | R | R | - | Object-level assertion ⚠️ |
| `SwapRequest` (own) | R/W | R | R | R | R/W | - | - | ⚠️ Partial |
| `PrintQueueJob` | R/W | R | R | - | - | - | R/W | Route dep (`require_print_shop`) |
| Copy count (# of copies) | R | R | R | - | ❌ Hidden in UI | - | UI-layer only ⚠️ |
| `AuditLog` (read) | R | - | - | - | - | - | - | Route dep (`require_admin`) |
| `enrollment_records` (PII) | R/W | - | - | - | - | - | - | Route dep (`require_admin`) |
| `HistoricalSchedule*` | R | R | R | R | R | - | - | Route dep |
| `ExamAccessToken` | R/W | - | - | - | - | - | - | Route dep + token validation |

**Critical note on copy count:** The restriction is enforced only at the UI layer (role-gated column in `CopyPage`).
The backend API for copy counts does not enforce this. A staff user with API access could retrieve copy counts.
Phase 4 fix: add backend enforcement via route dependency.

---

## 4. Sensitive Data Flows

Data flows that touch PII-High (student names, IDs, enrollment records):

### Flow: Enrollment Import → `enrollment_records` Table
```
Admin uploads enrollment CSV
  → POST /api/import/v2/validate     [admin only]  ← PII enters system
  → POST /api/import/v2/commit       [admin only]  ← PII written to DB
  → ImportSession.audit_log created  [logged]
  → enrollment_records table:
      student_id (VARCHAR) — PII-High
      full_name  (VARCHAR) — PII-High
```
**Guards:** admin-only route dep; `ImportRowLog` audit; row-level selection prevents bulk over-import.

### Flow: Export → Workload PDF / Excel
```
Admin/staff requests workload export
  → GET /api/exports/workload-summary-pdf  [admin + staff]
  → Contains: full_name, division, assignment_count
  → audit_log: "EXPORT_WORKLOAD_PDF" logged with actor_id
```
**Guards:** Route dep; audit log on every export call.

### Flow: Student Schedule Lookup (Public API)
```
Student (unauthenticated) searches by student ID
  → GET /api/public/schedule?student_id=...  [no auth required]
  → Returns: exam dates, rooms, times
  → Does NOT return: full_name, other students in the room
```
**Guards:** Public endpoint intentionally exposes only own schedule; no cross-student data.

### Flow: PDF Access Token
```
Teacher uploads exam PDF
  → POST /api/submissions/{id}/upload
  → File stored at backend/uploads/exam_files/{filename}
  → ExamAccessToken created (time-bounded)

Print shop accesses PDF
  → POST /api/pdf/token/{sid}       [print_shop role]
  → GET  /api/pdf/download/{token}  [token validation]
  → ExamAccessLog created (actor_id, timestamp, token)
```
**Guards:** Time-bounded token; ExamAccessLog audit trail; no direct file path access.

---

## 5. Audit Coverage Requirement

Every mutation on these sensitive tables MUST produce an `AuditLog` record:

| Table | Required audit fields |
|-------|----------------------|
| `users` | `actor_id`, `action` (CREATE_USER/UPDATE_USER/DEACTIVATE_USER), `record_id`, `new_values` |
| `exam_submissions` | `actor_id`, `action`, `record_id`, `old_values.status`, `new_values.status` |
| `exam_submission_versions` | `actor_id`, `action`, `record_id` |
| `supervisions` | `actor_id`, `action` (ASSIGN_SUPERVISOR), `record_id` |
| `optimize_sessions` | `actor_id`, `action` (SIGN_WORKFLOW/UNLOCK_SWAP_WINDOW), `record_id` |
| `exam_access_logs` | Already has dedicated table — verify foreign key to `audit_logs` |
| `import_sessions` | `actor_id`, `action` (IMPORT_COMMIT), `record_id`, row count |
| `exam_periods` | `actor_id`, `action` (LOCK_PERIOD/ARCHIVE_PERIOD), `record_id` |
| `system_settings` | `actor_id`, `action` (UPDATE_SETTINGS), `old_values`, `new_values` |

---

## 6. PDPA Checklist for New Features

Run through this checklist before any new endpoint goes to code review:

**Data Access:**
- [ ] Does this endpoint return student names or IDs? If yes: add to sensitive data flow map
- [ ] Does it return PII in error messages? If yes: fix to use generic errors
- [ ] Does it expose data from `enrollment_records`? → admin-only route dep required

**Audit Logging:**
- [ ] Is this a POST/PUT/DELETE endpoint? → `audit_service.record()` call required after success
- [ ] Does it return a file (PDF/Excel)? → export audit log required
- [ ] Does it change a user's role or active status? → `CREATE_USER` or `UPDATE_USER` audit required

**Access Control:**
- [ ] Is the route protected by `require_admin` or similar? Verify the correct dependency
- [ ] Is object-level ownership checked? If the endpoint accesses a record by ID, is access verified?
- [ ] Does it use `get_dept_filter()` for dept-scoped data? Staff/teacher must see only their scope

**Retention:**
- [ ] Is new PII data being stored? → Specify retention period in `config/retention_policy.py`
- [ ] Is a new table with personal data being created? → Add it to the RETENTION_POLICY dict

**Frontend:**
- [ ] Is sensitive data (copy counts, full names) hidden for lower-privilege roles?
- [ ] Is this enforced at backend level, not just UI level?

---

## 7. Retention Activation Procedure

The cleanup system in `config/retention_policy.py` is fully implemented but gated behind
`RETENTION_CLEANUP_ENABLED = False`.

**Steps to activate:**
1. Run the dry-run report in staging: call `generate_dry_run_report(db)` — this returns
   a summary of rows that would be deleted, grouped by table, with date ranges
2. Review the report with admin and compliance officer — verify counts are expected
3. Get written sign-off from admin that the retention periods are appropriate
4. Set `RETENTION_CLEANUP_ENABLED = True` in production `.env`
5. The retention cleanup runs on the scheduler (see `routers/scheduler.py`)
6. Monitor: after first run, verify `audit_logs` shows `RETENTION_CLEANUP_EXECUTED` action

**Current retention periods (from `config/retention_policy.py`):**
| Data type | Retention | Trigger |
|-----------|-----------|---------|
| Student schedules + attendance | 365 days | exam_period_end |
| QR check-in logs | 365 days | exam_period_end |
| Audit logs | 730 days | log_date |
| Revoked tokens | 1 day | created_at |
| Submission versions | 730 days | exam_period_end |
| Exam access logs | 730 days | timestamp |
| Swap requests | 180 days | exam_period_end |
| Historical schedules | **Permanent** | never |
