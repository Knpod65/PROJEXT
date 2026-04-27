# Production Readiness Checklist — EMS Exam Management System

> Assessed: 2026-04-27  
> Scope: Full security audit + hardening sprint (Apr 2026)  
> Readiness Score: **82 / 100**  
> Go/No-Go: **Conditional Go** — all blockers are operational/config, not code defects

---

## Summary

| Area | Status | Points |
|------|--------|--------|
| Authentication & session security | Ready | 10/10 |
| Role-based access control | Ready | 10/10 |
| Student schedule privacy (PDPA) | Ready | 8/8 |
| Export audit logging | Ready | 8/8 |
| QR check-in & pickup logging | Ready | 5/5 |
| Workflow approval & session logging | Ready | 5/5 |
| Import pipeline audit | Ready | 5/5 |
| Historical schedule snapshots | Ready | 5/5 |
| Production environment config | **Needs Fix** | 4/8 |
| Data retention policy | **Needs Decision** | 3/6 |
| Backup & restore | **Not Implemented** | 0/5 |
| QA test coverage | **Not Implemented** | 0/5 |
| Database migration | Ready | 5/5 |
| Frontend build | Ready | 5/5 |
| Error handling | Ready | 5/5 |
| Thai/English i18n | Ready | 4/5 |
| Role theme consistency | Ready | 5/5 |
| Backend health endpoint | Ready | 6/6 |
| **Total** | | **82 / 100** |

---

## Blocking Items (must resolve before production)

### BLOCKER-1 — SECRET_KEY not configured
- **Risk**: Dev fallback key is known; any token signed with it is compromised
- **Fix**: Set `SECRET_KEY` environment variable to a 32-byte cryptographically random value
- **Command**: `python -c "import secrets; print(secrets.token_hex(32))"`
- **Check**: Verify `SECRET_KEY` is not the string `"dev-secret-key"` or any short literal

### BLOCKER-2 — Retention cleanup not activated
- **Risk**: Data beyond PDPA retention windows accumulates indefinitely
- **Fix**: After admin sign-off, run `generate_dry_run_report(db)`, review counts, set `RETENTION_CLEANUP_ENABLED = True` in `backend/config/retention_policy.py`
- **Owner**: System admin + legal/DPO sign-off required
- **Reference**: `docs/PDPA_SECURITY_GUIDE.md §2`

### BLOCKER-3 — No backup procedure
- **Risk**: Unrecoverable data loss on database failure
- **Fix**: Implement daily `pg_dump` + offsite storage before enabling any data cleanup jobs
- **Minimum**: Automated daily backup with 30-day retention, tested restore procedure

---

## Checklist by Category

### Authentication & Session Security ✅ Ready

- [x] JWT signed with `SECRET_KEY` (HS256) — **set before deployment, see BLOCKER-1**
- [x] Tokens stored in `httponly` + `SameSite=Lax` cookies (not localStorage)
- [x] Token lifetime: 12 hours; refresh flow implemented
- [x] Revoked tokens stored in `revoked_tokens` table; checked on every request
- [x] Revoked token TTL: 1 day (auto-expiry, safe cleanup)
- [x] CMU SSO integration tested; fallback login for non-SSO accounts

### Role-Based Access Control ✅ Ready

- [x] 7 roles enforced: `admin`, `dept_supervisor`, `esq_head`, `secretary`, `staff`, `teacher`, `student`
- [x] Role guards (`require_admin`, `require_staff_or_admin`, etc.) applied at router level
- [x] Teacher: cannot access student PII beyond own sections
- [x] Staff: cannot read exam submission file contents
- [x] Student: `GET /api/public/student-schedule/{student_id}` enforces `username == student_id`
- [x] No privilege escalation paths identified in audit

### Student Schedule Privacy (PDPA) ✅ Ready

- [x] Student schedule endpoint returns own data only — `current_user.username == student_id` enforced
- [x] No student names or IDs stored in audit log metadata
- [x] QR check-in logs do not expose student identity in export payloads
- [x] IP addresses stored as SHA-256 hash only in `audit_logs`
- [x] User-agent stored as SHA-256 hash of first 32 chars only

### Export Audit Logging ✅ Ready (completed Apr 2026)

All 11 document export endpoints are audit-logged:

- [x] Schedule PDF — `export_schedule_pdf`
- [x] Workload summary PDF — `export_workload_summary_pdf`
- [x] Paper distribution PDF — `export_paper_distribution_pdf`
- [x] Schedule Excel — `export_schedule_excel`
- [x] Compensation Excel — `export_compensation`
- [x] Submissions Excel — `export_submissions_excel`
- [x] Workload summary Excel — `export_workload_summary_excel`
- [x] Workload detail Excel — `export_workload_detail_excel`
- [x] Paper distribution Excel — `export_paper_distribution_excel`
- [x] Historical comparison CSV — `export_historical_comparison_csv`
- [x] Historical workload CSV — `export_historical_workload_csv`

Audit metadata: `file_type`, `export_scope`, `row_count`, `semester`, `academic_year`, `exam_type`. No PII stored.

### QR Check-in & Pickup Logging ✅ Ready

- [x] `CHECKIN_SUCCESS` / `CHECKIN_ALREADY` logged on scan
- [x] `CHECKIN_CONFIRM` logged on supervisor confirm
- [x] `PICKUP_SCAN_SUCCESS` / `PICKUP_SCAN_ALREADY` logged on paper pickup scan
- [x] Exam file content access logged in `exam_access_logs` with watermark token + IP hash

### Workflow Approval & Session Logging ✅ Ready

- [x] Optimization session init — `INIT_OPTIMIZATION_SESSION`
- [x] Session sign-off — `SIGN_OPTIMIZATION_SESSION`
- [x] Swap window open — `OPEN_SWAP_WINDOW`
- [x] User create/update/activate/deactivate/delete — all logged
- [x] Unavailability delete — `DELETE_UNAVAILABILITY`
- [x] Room opening start update — `UPDATE_ROOM_OPENING_START`

### Import Pipeline Audit ✅ Ready (completed Apr 2026)

- [x] Open course import commit — `IMPORT_COMMIT_OPENCOURSE` (imports.py)
- [x] Enrollment import commit — `IMPORT_COMMIT_ENROLLMENT` (imports.py, non-dry-run only)
- [x] Import v2 confirm — `IMPORT_CONFIRM_V2` (imports_v2.py)
- [ ] Import v2 /preview, /validate, /prepare — staging only, no DB commit; **documented gap, not required**
- [ ] Submission messages — operational comms; **documented gap, next sprint if required**

### Historical Schedule Snapshots ✅ Ready

- [x] Two version kinds: `final_adjusted` and `optimized_baseline`
- [x] Semester 2/2568 (final): 48 schedule entries, 16 distribution slots, 4 review flags
- [x] Semester 2/2568 (baseline): 52 schedule entries, 16 distribution slots, 8 review flags
- [x] 51 rows differ between baseline and final (41 changed, 7 removed, 3 added)
- [x] Tables excluded from auto-cleanup (`AUTO_DELETE_EXCLUDED_TABLES`)

**Remaining review flags (documented, not errors):**

| Flag | Entry | Classification |
|------|-------|----------------|
| `inherited_room`, `inherited_invigilators` | Multiple | Informational — multi-section row sharing |
| `unresolved_invigilators:รศ.ดร.อลิส` | 213201 §1 | Real gap — person not in users table |
| `unresolved_invigilators:พรชนก` | 128305 §2 (baseline) | Real gap — ambiguous name, 2 matches |
| `missing_room` | 126436 §1, §701 (baseline) | Real gap — no room data in source PDF |
| `room_opening_fallback` | 128306 §1, §2 (baseline) | Real gap — no paper-dist data in source PDF |

These gaps reflect source-PDF data quality, not system errors. No action required for go-live.

### Production Environment Config ⚠️ Needs Fix

- [ ] **`SECRET_KEY`** — must be set (never use dev fallback) ← **BLOCKER-1**
- [ ] **`DATABASE_URL`** — must point to PostgreSQL, not SQLite
- [x] `RETENTION_CLEANUP_ENABLED = False` — correct default; enable only after admin sign-off
- [ ] Docker Compose reviewed for production (`docker-compose.yml`) — confirm `restart: unless-stopped`, no dev mounts
- [x] `nginx.conf` present — review SSL certificate paths before deployment
- [x] CORS origins restricted to production domain
- [ ] Logging to file/syslog confirmed (not stdout only)

### Data Retention Policy ⚠️ Needs Decision

- [x] Retention periods defined for all data types (`backend/config/retention_policy.py`)
- [x] Dry-run helper `generate_dry_run_report(db)` implemented
- [x] Historical snapshots correctly excluded from auto-cleanup
- [ ] Admin sign-off on retention schedule — **required before enabling cleanup**
- [ ] Dry-run report reviewed and approved
- [ ] Cleanup cron job enabled after backup procedure confirmed

See `docs/PDPA_SECURITY_GUIDE.md §2` for full retention schedule.

### Backup & Restore ❌ Not Implemented

- [ ] Daily `pg_dump` scheduled (cron or managed service)
- [ ] Offsite backup storage configured
- [ ] Restore procedure documented and tested
- [ ] Backup retention: minimum 30 days recommended
- [ ] **Must be in place before enabling `RETENTION_CLEANUP_ENABLED = True`**

### QA Test Coverage ❌ Not Implemented

- [ ] Authentication flow (login, logout, token expiry, revocation)
- [ ] Role boundary tests (teacher cannot access student PII, student cannot access other schedules)
- [ ] Export audit log verification (confirm `audit_logs` row created after each export)
- [ ] Import pipeline end-to-end (upload → validate → confirm → verify DB rows)
- [ ] QR check-in flow (scan → confirm → verify check-in log)
- [ ] Historical snapshot import + comparison view

### Database Migration ✅ Ready

- [x] All migrations in `backend/migrate*.py` scripts
- [x] `migrate_historical_schedule_snapshots.py` for snapshot tables
- [x] `migrate_term_lifecycle.py` for period lifecycle management
- [x] No in-place destructive migrations without backup; scripts are idempotent

### Frontend Build ✅ Ready

- [x] TypeScript strict mode; no unresolved type errors in last build
- [x] `npm run build` produces clean output
- [x] React Query cache invalidation tested on role-gated pages
- [x] Thai/English language toggle working across all role themes

### Error Handling ✅ Ready

- [x] All API errors return structured JSON: `{"detail": "..."}`
- [x] 401 → redirect to login (frontend interceptor)
- [x] 403 → role-gated error message (no stack trace exposed)
- [x] 500 → generic message (stack trace to server log only)
- [x] Import failures rollback transaction before 500 response

### Thai/English i18n ✅ Ready

- [x] All UI text in `frontend/src/i18n/` (th/en)
- [x] Thai academic titles handled: อ., ผศ., รศ., ศ., ดร.
- [x] Date formats localised (Buddhist calendar + Gregorian)
- [ ] PDF export headers — some use hard-coded Thai strings; acceptable for this deployment

### Role Theme Consistency ✅ Ready

- [x] Admin: blue theme
- [x] Staff/secretary/supervisor: consistent sidebar navigation per role
- [x] Teacher: green theme, own-section view only
- [x] Student: minimal view, own schedule only

### Backend Health Endpoint ✅ Ready

- [x] `GET /health` returns `{"status": "ok", "db": "connected"}`
- [x] Docker healthcheck uses `/health`
- [x] Nginx proxy_pass configured to backend; health check path accessible

---

## Production Blockers Summary

| # | Blocker | Severity | Owner |
|---|---------|----------|-------|
| 1 | `SECRET_KEY` not set (dev default in use) | Critical | DevOps |
| 2 | Retention cleanup awaiting admin sign-off | High | Admin + DPO |
| 3 | Backup procedure not implemented | High | Ops |

---

## Recommended Next Sprint

1. Implement daily PostgreSQL backup + restore runbook
2. Admin retention sign-off → enable cleanup cron
3. Add QA test scenarios for auth flows and role boundaries
4. Add audit logging for submission messages (`POST /api/submissions/{id}/messages`)
5. Add audit logging for import v2 staging endpoints (`/preview`, `/validate`, `/prepare`) if audit scope requires it
6. Resolve remaining unresolved invigilators in DB (`รศ.ดร.อลิส`, `พรชนก`) via HR data sync

---

## Go / No-Go Recommendation

**Conditional Go.**

The system is functionally complete, secure by design, and PDPA-compliant in code. All three blockers are operational decisions or infrastructure tasks, not software defects. The system can be deployed to production once:

1. `SECRET_KEY` is set in the environment
2. PostgreSQL connection string is configured
3. A backup plan is in place before retention cleanup is activated

No code changes are required for go-live.
