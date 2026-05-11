# Audit and Event Model
## EMS — What Is Logged, How, and How to Query It

> **Audience:** Security engineers, compliance auditors, engineers adding endpoints
> **Scope:** AuditLog schema, log_action() contract, mandatory events, action name registry, query patterns, event-driven extension roadmap, retention rules
> **Do NOT duplicate** PDPA classification tables from `docs/PDPA_SECURITY_GUIDE.md`
> **Reference files:** `backend/models.py` (AuditLog), `backend/auth_utils.py` (log_action), `backend/config/retention_policy.py`

---

## 1. AuditLog Schema

The `audit_logs` table is the single source of truth for all system mutations.

```python
# From backend/models.py
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id              = Column(Integer, primary_key=True)
    actor_id        = Column(Integer, ForeignKey("users.id"))     # who did it
    action          = Column(String(100), nullable=False)          # what action (see registry)
    table_name      = Column(String(100))                          # which table was affected
    record_id       = Column(Integer)                              # which row was affected
    old_values      = Column(JSON)                                 # state before change
    new_values      = Column(JSON)                                 # state after change
    ip_hash         = Column(String(64))                           # SHA-256 of request IP
    user_agent_hash = Column(String(64))                           # SHA-256 of User-Agent
    request_id      = Column(String(64))                           # X-Request-ID correlation ID
    duration_ms     = Column(Integer)                              # request processing time
    http_status     = Column(Integer)                              # HTTP response status code
    timestamp       = Column(DateTime(timezone=True), server_default=func.now())
```

**5 Indexes on audit_logs:**
1. `ix_audit_actor` — on `actor_id` (query by user)
2. `ix_audit_action` — on `action` (query by event type)
3. `ix_audit_table` — on `table_name` (query by affected table)
4. `ix_audit_record` — on `(table_name, record_id)` (query history of a specific record)
5. `ix_audit_timestamp` — on `timestamp` (time-range queries)

**Immutability:** `AuditLog` records are INSERT-only. No UPDATE or DELETE is allowed except
via the retention cleanup process (which deletes rows older than 730 days).

---

## 2. `log_action()` Contract

Current signature in `backend/auth_utils.py` (line ~475):

```python
def log_action(
    db: Session,
    actor: models.User,
    action: str,
    *,
    table_name: str = "",
    record_id: Optional[int] = None,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    http_status: int = 200,
    request_id: str = "",
    duration_ms: int = 0,
) -> models.AuditLog:
    """
    Write a single AuditLog record. Does NOT commit — caller must commit.
    IP and user-agent are extracted from the current request context.
    """
```

**Important:** `log_action()` does NOT call `db.commit()`. The caller is responsible for
committing. This means if the route handler fails after `log_action()` but before `db.commit()`,
the audit record is rolled back with the failed transaction.

**Going forward (Phase 3+):** Use `audit_service.record()` which validates the action name
against `ACTION_REGISTRY` before calling `log_action()`. This prevents typos in action names
that cause silent coverage gaps.

---

## 3. Current Coverage vs. Gaps

**Confirmed covered** (explicit `log_action()` calls found):
- User login / logout
- Submission approval / rejection
- Workflow signing events
- Import commit (import_sessions)
- QR token generation and pickup confirmation
- Exam PDF access (ExamAccessLog — separate table with same purpose)
- Dashboard read (admin-only AuditLog reads)

**Confirmed missing** (mutation endpoints without audit calls):
| Router | Endpoint | Missing Action |
|--------|----------|----------------|
| `period.py` | POST /api/period/ | `CREATE_PERIOD` |
| `period.py` | PUT /api/period/{id}/archive | `ARCHIVE_PERIOD` |
| `period.py` | POST /api/period/{id}/close | `LOCK_PERIOD` |
| `settings.py` | PUT /api/settings/ | `UPDATE_SETTINGS` |
| `users.py` | PUT /api/users/{id} (deactivate) | `DEACTIVATE_USER` |
| `schedule.py` | DELETE /api/schedule/{id} | `DELETE_SCHEDULE` |
| `co_exam.py` | POST /api/co-exam/ | `CREATE_CO_EXAM_GROUP` |
| `co_exam.py` | PUT /api/co-exam/{id} | `UPDATE_CO_EXAM_GROUP` |
| `external_exams.py` | DELETE /api/external/{id} | `DELETE_EXTERNAL_EXAM` |
| `swaps.py` (legacy) | PUT /api/swaps/{id}/reject | `REJECT_SWAP` |

---

## 4. Mandatory Audit Events Table

Every mutation to these domains must produce an `AuditLog`. Required fields per event:

| Action Name | Trigger | `table_name` | Required `old_values` | Required `new_values` |
|-------------|---------|------------|----------------------|----------------------|
| `LOGIN` | Successful login | `users` | — | `{role, ip_hash}` |
| `LOGOUT` | User logs out | `users` | — | — |
| `CREATE_USER` | New user created | `users` | — | `{username, role, email}` |
| `UPDATE_USER` | User record changed | `users` | `{role, is_active}` | `{role, is_active}` |
| `DEACTIVATE_USER` | User deactivated | `users` | `{is_active: true}` | `{is_active: false}` |
| `SUBMIT_EXAM` | Teacher submits | `exam_submissions` | `{status: "draft"}` | `{status: "submitted"}` |
| `APPROVE_SUBMISSION` | Admin approves | `exam_submissions` | `{status}` | `{status: "approved", approved_by}` |
| `REJECT_SUBMISSION` | Admin rejects | `exam_submissions` | `{status}` | `{status: "rejected", reason}` |
| `SIGN_WORKFLOW` | Signer signs | `optimize_sessions` | `{status}` | `{status, signer_username, round}` |
| `UNLOCK_SWAP_WINDOW` | Admin opens swaps | `optimize_sessions` | `{status: "round1_complete"}` | `{status: "swap_open"}` |
| `CONFIRM_SWAP` | Swap approved | `swap_requests` | `{status: "pending"}` | `{status: "approved"}` |
| `REJECT_SWAP` | Swap rejected | `swap_requests` | `{status: "pending"}` | `{status: "rejected"}` |
| `GENERATE_QR` | QR token created | `exam_pickup_qr_tokens` | — | `{schedule_id, exam_type}` |
| `CONFIRM_PICKUP` | Paper pickup confirmed | `exam_pickup_checkins` | — | `{token_id, confirmed_by}` |
| `IMPORT_COMMIT` | Import executed | `import_sessions` | — | `{data_type, rows_imported, rows_skipped}` |
| `EXPORT_SCHEDULE_PDF` | Schedule PDF exported | — | — | `{period_id, exported_by}` |
| `EXPORT_WORKLOAD_PDF` | Workload PDF exported | — | — | `{period_id, exported_by}` |
| `EXPORT_WORKLOAD_EXCEL` | Workload Excel exported | — | — | `{period_id, exported_by}` |
| `GENERATE_EXAM_PDF` | Exam document generated | `exam_submissions` | — | `{document_type, submission_id}` |
| `LOCK_PERIOD` | Period locked | `exam_periods` | `{lifecycle_status}` | `{lifecycle_status: "locked"}` |
| `ARCHIVE_PERIOD` | Period archived | `exam_periods` | `{lifecycle_status}` | `{lifecycle_status: "archived"}` |
| `CREATE_PERIOD` | Period created | `exam_periods` | — | `{academic_year, semester, exam_type}` |
| `UPDATE_SETTINGS` | System settings changed | `system_settings` | `{key, old_value}` | `{key, new_value}` |

---

## 5. Action Name Registry

Naming convention: `VERB_NOUN` in UPPER_SNAKE_CASE.
- Verb: `CREATE`, `UPDATE`, `DELETE`, `APPROVE`, `REJECT`, `SUBMIT`, `SIGN`, `EXPORT`, `IMPORT`, `GENERATE`, `LOCK`, `ARCHIVE`, `UNLOCK`, `CONFIRM`, `CANCEL`
- Noun: table name or domain concept (not implementation detail)

**Do NOT use:** `save_`, `handle_`, `process_`, `do_` prefixes. These are implementation words.
**Do NOT use:** Role names in action names (not `ADMIN_APPROVE`, just `APPROVE_SUBMISSION`)

Full registry lives in `backend/services/audit_service.py:ACTION_REGISTRY` (Phase 3 deliverable).

---

## 6. Query Patterns for Compliance and Operations

### History of a specific record
```sql
SELECT actor_id, action, old_values, new_values, timestamp
FROM audit_logs
WHERE table_name = 'exam_submissions' AND record_id = 42
ORDER BY timestamp ASC;
```

### All actions by a specific user in a time window
```sql
SELECT action, table_name, record_id, timestamp
FROM audit_logs
WHERE actor_id = 7
  AND timestamp BETWEEN '2026-02-01' AND '2026-06-01'
ORDER BY timestamp DESC;
```

### All export actions (for compliance reporting)
```sql
SELECT actor_id, action, new_values, timestamp
FROM audit_logs
WHERE action LIKE 'EXPORT_%'
ORDER BY timestamp DESC;
```

### Detect modification of locked-period data (anomaly detection)
```sql
SELECT al.*, ep.lifecycle_status
FROM audit_logs al
JOIN exam_periods ep ON (al.new_values->>'period_id')::int = ep.id
WHERE ep.lifecycle_status = 'locked'
  AND al.action IN ('UPDATE_SCHEDULE', 'APPROVE_SUBMISSION', 'CONFIRM_SWAP');
```

### Count mutations per user per day (operations monitoring)
```sql
SELECT
    actor_id,
    DATE(timestamp) AS day,
    COUNT(*) AS mutation_count
FROM audit_logs
WHERE action NOT IN ('LOGIN', 'LOGOUT')
GROUP BY actor_id, DATE(timestamp)
ORDER BY day DESC, mutation_count DESC;
```

---

## 7. Event-Driven Extension (Phase 5)

The current `log_action()` model is synchronous and fire-and-forget. For Phase 5 Operational
Intelligence, it should evolve toward an event bus where audit logging is one subscriber.

**Proposed pattern:**
```python
# Phase 5: emit an event, multiple handlers subscribe
event_bus.emit("APPROVE_SUBMISSION", {
    "actor_id": user.id,
    "submission_id": sub.id,
    "period_id": sub.period_id,
})

# Handlers (all async):
# 1. AuditLogHandler → writes to audit_logs table
# 2. NotificationHandler → sends email digest
# 3. MetricsHandler → updates period health snapshot
# 4. AlertHandler → checks if this resolves a blocker
```

**Until Phase 5:** Continue using `audit_service.record()` directly. Do NOT prematurely
introduce an event bus — it adds complexity without Phase 5's use case to justify it.

---

## 8. Retention Rules

From `backend/config/retention_policy.py`:

| Data Type | Retention | Cleanup State |
|-----------|-----------|---------------|
| Audit logs | **730 days** from log date | `RETENTION_CLEANUP_ENABLED = False` (not yet active) |
| Exam access logs | 730 days from timestamp | Same gate |
| QR check-in logs | 365 days from period end | Same gate |
| Revoked tokens | 1 day from created_at | Same gate |

**Retention immutability guarantee:**
- `AuditLog` records within their retention window may not be deleted by any application code
- Only the `run_cleanup()` function in `config/retention_policy.py` may delete audit rows
- That function is gated by `RETENTION_CLEANUP_ENABLED` and requires dry-run review first
- Database-level: no `DELETE` permission should be granted to the application user for `audit_logs`
  except through the explicit cleanup procedure

See `POLICY_AND_PDPA_ENFORCEMENT.md` §7 for the full retention activation procedure.
