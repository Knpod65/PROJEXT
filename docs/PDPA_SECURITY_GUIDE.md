# PDPA & Security Guide — EMS Exam Management System

> Personal Data Protection Act B.E. 2562 (PDPA) compliance reference for system operators, developers, and auditors.

---

## 1. Data Classification

| Class | Description | Examples | Sensitivity |
|-------|-------------|----------|-------------|
| **PII-High** | Student identity data | Student ID, full name, faculty, enrollment records | High — PDPA Article 26 |
| **PII-Medium** | Staff identity data | Instructor name, staff username, email | Medium |
| **Operational** | Exam scheduling data | Course codes, room assignments, dates/times | Low-Medium |
| **Audit** | System event logs | Action logs, IP hashes, access timestamps | Medium — retention required |
| **Archive** | Historical snapshots | Optimized vs. final schedule comparison | Permanent institutional record |
| **Public** | Reference data | Room names, course titles, building codes | Public |

---

## 2. Retention Periods

Defined in `backend/config/retention_policy.py`. Cleanup is **disabled** pending admin decision — no data is auto-deleted.

| Data Type | Table | Retention | Trigger Event | Rationale |
|-----------|-------|-----------|---------------|-----------|
| Student schedules / enrollments | `enrollment_records`, `exam_schedules` | **1 year** | Exam period end | PDPA minimum + CMU institutional policy |
| QR check-in logs | `exam_pickup_checkins`, `checkin_events` | **1 year** | Exam period end | Incident investigation window |
| Audit logs | `audit_logs` | **2 years** | Log timestamp | PDPA accountability obligation |
| Exam file access logs | `exam_access_logs` | **2 years** | Access timestamp | Security audit trail |
| Submission version history | `exam_submission_versions` | **2 years** | Exam period end | Dispute resolution record |
| Revoked JWT tokens | `revoked_tokens` | **1 day** | Token creation | Token lifetime is 12 h; no regulatory need |
| Swap requests | `swap_requests` | **6 months** | Exam period end | Operational record only |
| Import session records | `import_sessions` | **1 year** | Exam period end | Data provenance trail |
| **Historical schedule snapshots** | `historical_schedule_batches`, `historical_schedule_entries`, `historical_distribution_slots` | **Permanent** | Never | See §5 |

### Enabling cleanup
Set `RETENTION_CLEANUP_ENABLED = True` in `retention_policy.py` only after:
1. Admin sign-off on the retention schedule above
2. A dry-run report is reviewed (`generate_dry_run_report(db)`)
3. A database backup is confirmed

---

## 3. Access Control Principles

### Role hierarchy (highest → lowest privilege)
| Role | DB value | Key permissions |
|------|----------|-----------------|
| `admin` | admin | Full read/write; user management; import; export all; historical schedules |
| `dept_supervisor` | dept_supervisor | View schedules; approve submissions; export own department |
| `esq_head` | esq_head | Exam workflow oversight; view student schedules |
| `secretary` | secretary | View student schedules; support operations |
| `staff` | staff | Check-in; workload views; swap requests |
| `teacher` | teacher | View own sections; submit exam documents |
| `student` | student | View **own schedule only** (authenticated, username == student_id) |

### Principle of least privilege
- **Students** can only access their own schedule via `GET /api/public/student-schedule/{student_id}`. The endpoint enforces `current_user.username == student_id`.
- **Teachers** cannot access student identity data beyond their own sections.
- **Staff** cannot access exam submission file contents (ExamAccessLog is gated by token + role).
- **Admin** actions are audit-logged on every mutating operation.

---

## 4. Export Logging Policy

All document exports are audit-logged via `log_action()` to the `audit_logs` table. No raw student PII is stored in audit metadata.

| Export | Action logged | Metadata captured |
|--------|--------------|-------------------|
| Schedule PDF | `export_schedule_pdf` | file_type, scope, row_count, semester, AY, exam_type |
| Workload summary PDF | `export_workload_summary_pdf` | file_type, scope, row_count, semester, AY, exam_type |
| Paper distribution PDF | `export_paper_distribution_pdf` | file_type, scope, row_count, semester, AY, exam_type |
| Schedule Excel | `export_schedule_excel` | file_type, scope, row_count, semester, AY, exam_type |
| Compensation Excel | `export_compensation` | file_type, scope, row_count, semester, AY, exam_type |
| Submissions Excel | `export_submissions_excel` | file_type, scope, row_count, semester, AY |
| Workload summary Excel | `export_workload_summary_excel` | file_type, scope, row_count, semester, AY, exam_type |
| Workload detail Excel | `export_workload_detail_excel` | file_type, scope, row_count, semester, AY, exam_type |
| Paper distribution Excel | `export_paper_distribution_excel` | file_type, scope, row_count, semester, AY, exam_type |
| Historical comparison CSV | `export_historical_comparison_csv` | file_type, scope, row_count, semester, AY, exam_type |
| Historical workload CSV | `export_historical_workload_csv` | file_type, scope, row_count, version_kind, semester, AY, exam_type |

**Exam file content access** (individual exam PDFs) is additionally logged in the `exam_access_logs` table with watermark tracking and IP hash.

### What is NOT stored in audit metadata
- Student names or IDs
- Raw exam content
- Full IP addresses (SHA-256 hash only)
- Full user-agent strings (first-32-char SHA-256 hash only)
- Passwords or tokens

---

## 5. Historical Schedule Snapshots — Permanent Retention Rationale

Historical schedule snapshots (`HistoricalScheduleBatch`, `HistoricalScheduleEntry`, `HistoricalDistributionSlot`) are retained **permanently** for the following reasons:

1. **Institutional accountability** — The comparison between the optimized baseline (`optimized_original_result`) and the final adjusted schedule (`final_adjusted_result`) documents every room reassignment and timing change made by administrators. This record is required for post-exam audits.

2. **Workload fairness** — The paper-distribution and room-opening workload data forms the basis for staff compensation. Permanent retention enables re-verification if disputes arise after the exam period.

3. **Regulatory compliance** — Thai university regulations require retention of examination administration records for at least 5 years. Permanent retention exceeds this requirement without imposing management overhead.

4. **No personal data risk** — Snapshot data contains staff names (operational roles), not student PII. The retention risk profile is low.

These tables are listed in `AUTO_DELETE_EXCLUDED_TABLES` and will never be touched by automated cleanup jobs.

---

## 6. Import Pipeline Audit

Data import operations (course data, enrollment data) are now audit-logged:

| Action | Endpoint | Trigger |
|--------|----------|---------|
| `IMPORT_COMMIT_OPENCOURSE` | `POST /api/import/opencourse` | After successful DB commit |
| `IMPORT_COMMIT_ENROLLMENT` | `POST /api/import/enrollment` | After successful DB commit (non-dry-run only) |
| `IMPORT_CONFIRM_V2` | `POST /api/import/v2/confirm` | After successful `execute_import()` + commit |

Dry-run enrollment imports do **not** produce an audit entry (no data is written).

---

## 7. Remaining Audit Gaps (Documented)

The following endpoints are not audit-logged. These are either read-only queries or lower-risk staging operations:

| Gap | Endpoint | Risk level | Decision |
|-----|----------|------------|---------|
| Import v2 staging | POST /api/import/v2/preview, /validate, /prepare | Low — no DB commit | Document only; add in next sprint if required |
| Submission messages | POST/GET /api/submissions/{id}/messages | Low — operational comms | Document only; add in next sprint |
| Read-only queries | All GET list/query endpoints | Negligible | Not required per audit policy |

---

## 8. Security Checklist for Operators

Before production deployment:

- [ ] Set `SECRET_KEY` environment variable (never use the dev fallback)
- [ ] Set `DATABASE_URL` to production PostgreSQL connection string
- [ ] Confirm `RETENTION_CLEANUP_ENABLED = False` until retention schedule is approved
- [ ] Run `generate_dry_run_report(db)` to verify row counts before enabling cleanup
- [ ] Confirm daily backup procedure is in place before enabling cleanup
- [ ] Rotate `SECRET_KEY` if the dev default was ever used in a non-isolated environment
- [ ] Review `audit_logs` table weekly for anomalous export activity
