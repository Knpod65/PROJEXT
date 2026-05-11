# Import/Export Governance
## EMS — Data Pipeline Rules: What Enters and Leaves the System

> **Audience:** Admin users managing imports, engineers extending the import/export pipeline
> **Scope:** Import pipeline architecture, supported types, guard conditions, idempotency contract, export catalog, data provenance, file storage rules
> **Do NOT duplicate** column-level import mappings → see `frontend/src/docs/import-data-v2-spec.md`
> **Reference files:** `backend/import_v2/` (all), `backend/routers/imports_v2.py`, `backend/routers/exports.py`, `backend/routers/exports_excel.py`, `backend/routers/pdf.py`

---

## 1. Import Pipeline Architecture (V2)

The V2 import pipeline (`backend/import_v2/`) follows a 4-stage linear pipeline with an
explicit guard exception that prevents execution when validation fails.

```
User uploads file
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 1: PARSE  (import_v2/parsers.py)                    │
│  • Read Excel/CSV into DataFrame                           │
│  • Normalize column names (alias resolution)               │
│  • Detect file encoding (UTF-8 / TIS-620 Thai)             │
│  • Output: List[Dict] of raw rows                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 2: VALIDATE  (import_v2/validators.py)              │
│  • 25+ validation rules per row                            │
│  • Required field checks                                   │
│  • Foreign key existence checks (vs DB)                    │
│  • Duplicate detection (within file + vs existing DB)      │
│  • Output: List[ImportRowResult] with issue annotations    │
│  • If critical errors exceed threshold: raise              │
│    ImportExecutionBlocked (blocks Stage 4)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 3: NORMALIZE  (import_v2/normalizers.py)            │
│  • Clean data: strip whitespace, normalize encodings       │
│  • Standardize date formats                                │
│  • Map lecturer name variants via LecturerNameMap table    │
│  • Output: cleaned row dicts ready for DB write            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 4: IMPORT  (import_v2/importer.py)                  │
│  • Blocked if ImportExecutionBlocked was raised            │
│  • Row-level selection: only import selected_rows[]        │
│  • Override mechanism: row-level overrides with reason     │
│  • Upsert strategy: merge on key columns                   │
│  • Write ImportSession + ImportRowLog records              │
│  • Output: ImportSession with row counts                   │
└─────────────────────────────────────────────────────────────┘
```

### API Endpoints (V2)

| Step | Endpoint | What Happens |
|------|----------|-------------|
| Start | `POST /api/import/v2/start` | Upload file, detect type, run Stage 1 (parse) |
| Validate | `POST /api/import/v2/validate` | Run Stage 2 (validate), return issue list per row |
| Preview | UI-only | User reviews rows, selects which to import, adds override reasons |
| Commit | `POST /api/import/v2/commit` | Run Stage 3+4 with `selected_rows` and `overrides` |

### `ImportExecutionBlocked`
If more than a threshold number of rows have critical validation errors, the importer raises
`ImportExecutionBlocked`. This prevents partial imports when the input data is too corrupt.
The threshold is configurable; the default is: if >20% of rows have critical errors, block.

---

## 2. Supported Import Types

| Data Type | Source Format | Key Columns | Conflict Strategy | Tables Written |
|-----------|--------------|-------------|-------------------|----------------|
| OpenCourse (sections) | Excel | `course_id`, `section_no`, `semester`, `academic_year` | Upsert (merge on key) | `courses`, `sections` |
| Enrollment (students) | Excel | `student_id`, `course_id`, `section_no` | Upsert | `enrollment_records`, `sections.num_students` |
| Personnel (staff/teachers) | Excel | `employee_id` or `username` | Upsert | `users` (is_active toggling) |
| Room Capacity | Excel | `room_name` | Upsert | `rooms.capacity` |
| Historical Schedule | Excel (custom format) | `date`, `time`, `room`, `course_id` | Insert (new batch) | `historical_schedule_batches`, `historical_schedule_entries` |

### Column Alias Resolution
Each data type has a set of accepted column name aliases (e.g., for course ID: `COURSE_KEYS = ("course_id", "รหัสวิชา", "courseid")`). The parser tries each alias in order. If none match, a parse error is reported.

For full column alias lists, see `frontend/src/docs/import-data-v2-spec.md`.

---

## 3. Import Guard Conditions

Imports are blocked when:

| Condition | HTTP Response | Reason |
|-----------|--------------|--------|
| Target period is locked | 409 Conflict | `ensure_period_record_editable()` guard |
| File is malformed / unreadable | 400 Bad Request | Parser error from Stage 1 |
| >20% of rows have critical errors | `ImportExecutionBlocked` | Too many errors to safely proceed |
| Import session is from a different period | 400 Bad Request | Session-period mismatch check |
| Admin deselects all rows | 400 Bad Request | Nothing to import |

---

## 4. Import Idempotency Contract

Imports are designed to be re-runnable without data corruption:

| Table | Strategy | Key Columns | What Happens on Re-import |
|-------|----------|-------------|--------------------------|
| `courses` | Upsert | `course_id` | Name/credits updated; existing sections preserved |
| `sections` | Upsert | `course_id + section_no + semester + academic_year` | Metadata updated; existing schedules preserved |
| `users` | Upsert | `username` | Metadata updated; role changes require explicit override |
| `enrollment_records` | Upsert | `student_id + section_id` | Count updated |
| `rooms` | Upsert | `room_name` | Capacity updated |
| `historical_schedule_*` | Insert new batch | `batch_id` | New batch created; old batches preserved (write-once) |

**`import_session_id`**: Every row imported via V2 gets its `import_session_id` set to the
`ImportSession.id` of the current run. This allows tracing every DB record back to the import
that created it.

---

## 5. Export Catalog

All supported export types, their API endpoints, required permissions, and output format.

### Document Exports (Exam Operations)

| Export Type | Endpoint | Roles Allowed | Output Format | Contains PII? | Audit Logged? |
|-------------|----------|---------------|---------------|---------------|---------------|
| Exam schedule PDF | `GET /api/exports/schedule` | admin, staff | PDF | No (room/time only) | Yes |
| Invigilator assignment PDF | `GET /api/exports/schedule` (with staff param) | admin, staff | PDF | Staff names | Yes |
| Workload summary PDF | `GET /api/exports/workload-summary-pdf` | admin, staff | PDF | Staff names, counts | Yes |
| Workload Excel | `GET /api/exports/schedule-excel` | admin, staff | XLSX | Staff names, counts | Yes |
| Paper distribution summary | `GET /api/exports/...` | admin | PDF/XLSX | Staff names | Yes |
| Compensation export | `GET /api/exports/compensation` | admin | XLSX | Staff names, amounts | Yes |
| Submission summary Excel | `GET /api/exports/submissions-excel` | admin, esq_head, secretary | XLSX | Teacher names | Yes |
| Audit log export | `GET /api/exports/audit-logs` | admin | PDF | User IDs, IPs (hashed) | Yes |

### Exam Document Exports (Per Submission)

| Export Type | Endpoint | Roles Allowed | Output |
|-------------|----------|---------------|--------|
| Exam cover sheet PDF | `POST /api/documents/generate/{sid}` | admin, staff | PDF |
| Participant code sheet PDF | `POST /api/documents/generate/{sid}` | admin, staff | PDF |
| Signature sheet PDF | `POST /api/documents/generate/{sid}` | admin, staff | PDF |
| QR pickup code PDF | `POST /api/documents/pickup-qr/{sid}` | admin | PDF |
| Exam file download (print shop) | `GET /api/pdf/download/{token}` | print_shop | PDF |

### Historical Exports

| Export Type | Endpoint | Roles Allowed | Output |
|-------------|----------|---------------|--------|
| Historical workload comparison | `GET /api/historical-schedules/comparison` | admin | JSON/Chart data |
| Historical schedule overview | `GET /api/historical-schedules/overview` | admin | JSON |

---

## 6. Export Period Resolution Problem

`_resolve_period()` is currently duplicated in:
1. `backend/routers/exports.py` (lines ~17–29)
2. `backend/routers/pdf.py`

Both functions resolve an `ExamPeriod` from `(semester, academic_year, exam_type)` with the same
fallback-to-active logic. When called without parameters, they return the active period.

**This duplication must be fixed in Phase 2** by moving the logic into `term_lifecycle.py`:

```python
# backend/term_lifecycle.py (to add)
def resolve_export_period(
    db: Session,
    semester: str | None = None,
    academic_year: str | None = None,
    exam_type: str | None = None,
) -> "models.ExamPeriod":
    """
    Canonical export period resolver.
    If semester+academic_year given: find that specific period.
    If not given: return the currently active period.
    Raises HTTPException(400) if no match found.
    """
    if semester and academic_year:
        period = find_period(db, academic_year, semester, exam_type)
        if period:
            return period
        raise HTTPException(400, "ไม่พบ period ที่ระบุ")
    active = get_active_period(db)
    if active:
        return active
    raise HTTPException(400, "ไม่มี active period")
```

After this, update both `exports.py` and `pdf.py` to call `term_lifecycle.resolve_export_period()`.

---

## 7. Data Provenance

How to trace any piece of data back to its source:

### Section/Course provenance
```sql
SELECT s.*, imp.id AS import_session_id, imp.created_at AS imported_at, imp.import_type
FROM sections s
LEFT JOIN import_sessions imp ON s.import_session_id = imp.id
WHERE s.id = 42;
```

### Import session details
```sql
SELECT
    imp.*,
    COUNT(CASE WHEN irl.status = 'error' THEN 1 END) AS error_rows,
    COUNT(CASE WHEN irl.status = 'ok' THEN 1 END) AS success_rows
FROM import_sessions imp
LEFT JOIN import_row_logs irl ON irl.import_session_id = imp.id
WHERE imp.id = 123
GROUP BY imp.id;
```

### Who imported a specific user record
```sql
SELECT u.username, al.actor_id, al.timestamp, al.new_values
FROM users u
JOIN audit_logs al ON al.table_name = 'users' AND al.record_id = u.id
                   AND al.action = 'CREATE_USER'
WHERE u.username = 'somchai.k';
```

### Tracing an optimizer session back to import data
```sql
-- Optimizer used sections from which import sessions?
SELECT DISTINCT s.import_session_id, imp.import_type, imp.created_at
FROM optimize_sessions os
JOIN exam_schedules es ON es.period_id = os.period_id
JOIN sections s ON es.section_id = s.id
JOIN import_sessions imp ON s.import_session_id = imp.id
WHERE os.id = 5;
```

---

## 8. File Storage Rules

### Uploaded Exam Files (PDF submissions)

**Storage path:** `backend/uploads/exam_files/`
**Filename convention:** `{section_id}_{exam_type}_{timestamp}_{sanitized_original_name}.pdf`
**Naming rule:** `exam_pdf_processor.py` sanitizes original filenames before storage (strips
path components, replaces special characters, limits length)

**Access control:**
- Direct file path is NEVER returned to clients
- Access requires an `ExamAccessToken` with a time-bounded lifetime
- Token endpoint: `POST /api/pdf/token/{submission_id}` → `print_shop` role only
- Download endpoint: `GET /api/pdf/download/{token}` → token validation
- Each download is logged in `exam_access_logs`

**Retention:**
- Files are retained as long as the associated `ExamSubmission` is not purged
- The `exam_access_logs` table retains access records for 730 days
- No automatic file deletion is currently implemented; manual cleanup by admin

### Import Source Files

**Storage:** Temporary file cache during the import session (`import_v2/file_cache.py`)
**Lifetime:** Session-scoped; files are not permanently stored
**Audit:** The `ImportSession` record stores metadata (file size, row count, import type) but
not the file content itself

### Generated Documents (PDFs/DOCX)

**Generated on-demand:** Exam cover sheets, signature sheets, QR codes — generated at request time, not stored
**Exception:** QR code images may be temporarily cached at `backend/static/qr/` for PDF embedding
**Lifetime:** QR cache files are transient; cleared periodically by the scheduler
