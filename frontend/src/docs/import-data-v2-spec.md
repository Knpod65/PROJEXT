# Import Data V2 — Implementation Handoff Spec

**System:** EMS (Exam Management System) — Faculty of Political Science & Public Administration, CMU  
**Scope:** Preview-first, admin-confirmed import pipeline for all four source files  
**Target term:** Semester 2 / 2568 (data verified from actual files)  
**Status:** Codex-ready implementation spec — do NOT modify existing app code unless explicitly listed

---

## 1. File Schema Report

All schemas are derived from reading actual bytes. Do not infer from filenames.

---

### 1.1 `Book1.xls` — Student Enrollment

**Sheet:** `regist_student_faculty`  
**Engine required:** `xlrd` (binary .xls format)  
**Rows:** 7,628 | **Columns:** 16

| Column | Type | Nullable | Notes |
|---|---|---|---|
| `ID` | int64 (9-digit) | No | Student ID. Format: YYFFFNNNN. PK candidate |
| `NAME` | string | No | First name. Thai or English |
| `SNAME` | string | **165 nulls** | Surname. Null = international student or missing entry |
| `COURSENO` | int64 | No | Course code. FK → opencourse.COURESNO (after typo fix) |
| `SECLEC` | int64 | No | Section number. 1–15 = regular; 700-series = intl; 800-series = weekend/grad |
| `SECLAB` | int64 | No | Lab section. 0 = no lab |
| `CRELEC` | int64 | No | Lecture credits |
| `CRELAB` | int64 | No | Lab credits |
| `GRADE` | string | **7,491 nulls** | Null = not yet graded. "W" = withdrawn (137 rows). No other values present |
| `TYPE_REGIST` | string | No | K/P/I/S/A/O/L/C. Meaning undocumented — see §10 |
| `TRM` | int64 | No | Term number. All rows = 268 |
| `SEMESTER` | int64 | No | All rows = 2 |
| `YEAR` | int64 | No | All rows = 2568 |
| `MAJOR` | string | **4 nulls** | Student's major. 96 unique values |
| `FAC_ID` | int64 | No | Faculty ID. 20 unique values. No master table exists in DB |
| `FAC_NAME` | string | No | Faculty name text |

**Key findings:**
- 5,008 unique students; 87 unique course codes
- No duplicate rows on `(ID, COURSENO, SECLEC, SEMESTER, YEAR)` — enrollment data is clean
- `COURSENO=127798` appears in 0 rows of opencourse — orphan enrollment, must be blocked
- GRADE=W rows (137) should be excluded from exam list generation
- Section distribution: 700-series = 957 enrollments, 800-series = 807 enrollments

---

### 1.2 `Employee190226.csv` — Staff + Exam Roles

**Engine:** CSV, encoding `utf-8-sig`  
**Rows:** 37 | **Columns:** 11

| Column | Type | Nullable | Notes |
|---|---|---|---|
| `employee_id` | int64 | No | Sequential 1–37. PK |
| `title` | string | No | Thai honorific title |
| `name` | string | No | First name (Thai) |
| `surname` | string | No | Surname (Thai) |
| `role` | string | No | `Secretary`(1) / `Head_of_Unit`(4) / `Staff`(32) |
| `department` | string | **29 nulls** | Exam-role tag: ESQ/GOV/IA/PA/STB/ADMIN/Secretary. NOT an org unit |
| `division` | string | No | Org division. 6 values: General_Administration(13), Education_Student_Quality(11), Strategic_Planning(5), Research_Academic_Services(4), Political_Innovation_Center(3), Faculty_Secretary(1) |
| `unit` | string | **4 nulls** | Sub-unit (Political_Innovation_Center staff have no unit) |
| `ext` | string | No | Phone extension |
| `mobile` | string | No | Mobile. All 37 unique |
| `cmu_mail` | string | No | CMU email. All 37 unique. **Primary join key** |

**Key findings:**
- `department` column = exam-role tag, not org structure. Only 8/37 have it
- This file is **identical** to `Personnel_120226.xlsx → staff sheet`, except this CSV has the `department` column and the xlsx does not
- Import this file as the authoritative staff source (it has the extra column)
- In models: `department` maps to `User.dept_code`, `division` maps to `User.division`, `role` maps to... see §8

---

### 1.3 `opencourse.xls` — Course Sections + Lecturer + Exam Dates

**Format:** HTML exported as .xls (NOT binary Excel). Engine: `pd.read_html()`  
**Rows:** 165 | **Columns:** 20

| Column | Type | Nullable | Notes |
|---|---|---|---|
| `COURESNO` | int64 | No | **TYPO** — should be COURSENO. FK join key. Must be renamed on parse |
| `TITLE` | string | No | Course title in English |
| `SECLEC` | int64 | No | Section number. Composite PK with COURESNO |
| `SECLAB` | int64 | No | Lab section |
| `CRELEC` | float | No | Lecture credits |
| `CRELAB` | float | No | Lab credits |
| `DAY` | string | No | Day pattern: MTh/TuF/We/Sa/Su/TBA/Tu/Mo/Th/Fr |
| `BTIME` | string | No | Begin time HHMM string. "TBA" or "0000" = unscheduled |
| `FTIME` | string | No | End time HHMM string |
| `ROOM` | string | No | Room code. **Inconsistent spacing**: "PSB 1309" vs "PSB1309". Normalize on parse |
| `LECTURER` | string | No | Full name string (Thai or English). **No teacher_id**. 44 unique values |
| `MAX` | int64 | No | Enrollment cap |
| `REGIST` | int64 | No | Current enrollment count |
| `MID_DAY` | string | **117 nulls** | Midterm date string: "29 JAN 2026" format |
| `MID_TIME` | string | **117 nulls** | Midterm time: "15:30-18:30" format |
| `FIN_DAY` | string | **129 nulls** | Final exam date string |
| `FIN_TIME` | string | **129 nulls** | Final exam time string |
| `SEMESTER` | int64 | No | All = 2 |
| `YEAR` | int64 | No | All = 2568 |
| `LEVEL` | string | No | `Undergraduate`(139) / `Graduate`(26) |

**Key findings:**
- Composite PK: `(COURESNO, SECLEC, SECLAB, SEMESTER, YEAR)` — all 165 rows distinct
- Section 7xx = international/exchange student sections
- Section 8xx = weekend/evening graduate sections
- **4 sections with REGIST=0**: course 127492 sec 1, 128351 sec 1, 128799 sec 0, 140105 sec 0 — likely cancelled
- **4 sections over-enrolled** (REGIST > MAX): 126440/sec1 (+3), 126449/sec1 (+1), 128305/sec2 (+3), 128310/sec3 (+1)
- `LECTURER` = `"��Ҩ����"` (garbled Thai for "advisor") in thesis rows — not a real teacher; treat as placeholder
- `DAY=TBA` applies to 37 rows (22%) — thesis/cooperative education sections
- ROOM free-text inconsistency: strip all spaces before the room number digit during normalization

---

### 1.4 `Personnel_120226.xlsx` — Teacher + Staff Master

**Sheets:** `teacher` (44 rows × 10 cols) + `staff` (37 rows × 10 cols)

#### Sheet: `teacher`

| Column | Type | Nullable | Notes |
|---|---|---|---|
| `teacher_id` | int64 | No | Sequential 1–44. No duplicates. PK |
| `title` | string | No | Academic title (Thai) |
| `name` | string | No | First name |
| `surname` | string | No | Surname |
| `department` | string | No | `GOV`(15) / `PA`(15) / `IR`(13) / `STB`(1) |
| `ext` | string | No | Extension. Some include room suffix: `42989#128` |
| `mobile` | string | No | All present |
| `cmu_mail` | string | No | **0 nulls. Unique. Primary join key** |
| `email` | string | **3 nulls** | Personal email |
| `remark` | string | **40 nulls** | Free-text. 4 rows = `"��� 3"` (room annotation) |

**Department → course code prefix mapping:**

| dept | course prefix | description |
|---|---|---|
| GOV | 127xxx | Political Science / Government |
| PA | 128xxx | Public Administration |
| IR | 126xxx | International Relations |
| STB | 131xxx | Sustainability (1 teacher only) |
| Cross-dept | 140xxx | General education (multiple teachers) |

#### Sheet: `staff`

Identical rows to `Employee190226.csv` but **missing the `department` exam-role column**. Use `Employee190226.csv` as authoritative source. Do not import this sheet separately.

---

## 2. Relationship Mapping

### 2.1 Strong Joins (automatable)

| Relationship | Keys | Notes |
|---|---|---|
| `opencourse` section → `enrollment` rows | `COURESNO=COURSENO` + `SECLEC` + `SEMESTER` + `YEAR` | Rename COURESNO first |
| `Employee CSV` ↔ `Personnel staff sheet` | `cmu_mail` | Exact 1:1; no gaps |
| Teacher lookup: `opencourse.LECTURER` → `User.cmu_mail` | Via pre-built name→email map | 39/44 resolve automatically |
| Section in existing DB ↔ new enrollment rows | `course_id` + `section_no` + `semester` + `academic_year` | Standard FK |

### 2.2 Weak Joins (require admin confirmation)

| Relationship | Problem | Resolution |
|---|---|---|
| `opencourse.LECTURER` → `users` (5 unresolved) | Thai encoding corruption breaks exact string match | Show mapping UI; admin selects from teacher dropdown |
| `FAC_ID` → faculty master | No faculty master table in DB; FAC_ID values present but unresolved | Derive from `(FAC_ID, FAC_NAME)` pairs; create lookup at import time |
| `Employee.department` exam-role → system permissions | Codes ESQ/GOV/IA/PA/STB/ADMIN are undocumented | Admin must confirm meaning before permission assignment |

### 2.3 Unresolved Lecturer Name Map

The following 5 lecturers appear in `opencourse.LECTURER` but cannot be auto-matched to personnel due to encoding corruption. Matching is done via `cmu_mail` out-of-band:

| opencourse LECTURER value (garbled) | Likely match (cmu_mail) | teacher_id | Confidence | Action |
|---|---|---|---|---|
| `[garbled pichaarpa variant]` | pichaarpa.p@cmu.ac.th | 38 | Medium | Admin must confirm |
| `MATTHEW ROBSON` | matthew.r@cmu.ac.th | 39 | **High** | Auto-map (English name, safe) |
| `[garbled malinee variant]` | malinee.k@cmu.ac.th | 4 | Medium | Admin must confirm |
| `��Ҩ����` | N/A — thesis advisor placeholder | None | N/A | Mark section as `thesis_type=true`; skip teacher FK |
| `[garbled kraiwuth variant]` | kraiwuth.j@cmu.ac.th | 24 | Medium | Admin must confirm |

### 2.4 Missing Links

| Gap | Impact | Required action |
|---|---|---|
| `teacher_id` absent from opencourse | Cannot create `section.teacher_id` automatically for 5 rows | Mapping UI required |
| `COURSENO=127798` in enrollment, absent from opencourse | 0 enrollment rows can be linked | Admin must decide: skip or backfill |
| `department` exam-role meaning undocumented | Cannot assign permissions to ESQ/ADMIN/etc. staff | Admin confirmation before import commit |
| No `ExamPeriod.id` FK in opencourse | Must be selected by admin during import, not derived from file | Include `period_id` in import form |
| ROOM value is free-text | Rooms created on first seen; capacity not known from opencourse | Admin must set capacity in room master post-import |

---

## 3. Import Flow Specification

### 3.1 Import Order (strict dependency chain)

```
1. ExamPeriod must exist and be active   ← prerequisite; blocks all other imports
2. Personnel teachers    (Personnel_120226.xlsx → teacher sheet)
3. Staff/employees       (Employee190226.csv)
4. Course sections       (opencourse.xls)        ← depends on teachers (step 2)
5. Student enrollment    (Book1.xls)              ← depends on sections (step 4)
```

Personnel and staff (steps 2–3) are **global master data** — import once per system setup, not per term.  
Course sections and enrollment (steps 4–5) are **per-term** — repeat each semester.

---

### 3.2 Step 2: Personnel Teachers

**Source:** `Personnel_120226.xlsx`, sheet `teacher`  
**Target table:** `users` (role=`teacher`)

**Pre-import parse steps:**
1. Read with `openpyxl` engine, sheet `teacher`, header row 0
2. Strip whitespace from all string fields
3. Normalize `cmu_mail` to lowercase

**Validations:**
| Check | Severity | Block? |
|---|---|---|
| `cmu_mail` non-null and matches `*@cmu.ac.th` | Error | Yes |
| `cmu_mail` unique within file | Error | Yes |
| `department` in (`GOV`,`PA`,`IR`,`STB`) | Error | Yes |
| `name` or `surname` non-null | Error | Yes |
| `cmu_mail` already exists in `users` table → treat as UPDATE, not insert | Info | No |

**Insert/update logic:**
- If `users.email = cmu_mail` exists → update fields, keep `id`
- If not exists → insert with `role=teacher`, `password_hash=hash("cmu2025!")`
- Set `User.dept_code = department`
- Set `User.title`, `User.mobile`, `User.ext` from file

---

### 3.3 Step 3: Staff / Employees

**Source:** `Employee190226.csv`  
**Target table:** `users` (role=`staff` or `admin`)

**Pre-import parse steps:**
1. Read CSV with `encoding=utf-8-sig`
2. Detect admin email from config (`ADMIN_EMAIL = atikant.s@cmu.ac.th`)

**Validations:**
| Check | Severity | Block? |
|---|---|---|
| `cmu_mail` non-null | Error | Yes |
| `cmu_mail` unique within file | Error | Yes |
| `role` in (`Secretary`,`Head_of_Unit`,`Staff`) | Error | Yes |
| `division` non-null | Error | Yes |
| `department` exam-role tag (if present) in known set | Warning | No |
| `cmu_mail` already in `users` → UPDATE | Info | No |

**Insert/update logic:**
- `users.role = admin` if email matches `ADMIN_EMAIL`, else `staff`
- `users.dept_code = department` (exam-role tag, nullable)
- `users.division = division`
- `users.unit = unit` (nullable)

---

### 3.4 Step 4: Course Sections (opencourse.xls)

**Source:** `opencourse.xls`  
**Target tables:** `courses`, `sections`, `rooms`, `exam_schedules`

**Pre-import parse steps:**
1. Read with `pd.read_html(content, encoding="utf-8")[0]`
2. Rename column `COURESNO` → `COURSENO` — flag this rename in preview
3. Normalize ROOM: `re.sub(r'\s+(\d)', r'\1', room_str)` → "PSB 1309" → "PSB1309"
4. Parse `MID_DAY`/`FIN_DAY` strings: `"29 JAN 2026"` → `"2026-01-29"` (existing `parse_thai_date()` function works)
5. Resolve `LECTURER` → `teacher_id` via name→email map (see §2.3)

**Validations:**
| Check | Severity | Block? |
|---|---|---|
| `COURSENO` non-null and numeric | Error | Yes (row) |
| `SECLEC` non-null | Error | Yes (row) |
| `(COURSENO, SECLEC, SEMESTER, YEAR)` unique in file | Error | Yes (row) |
| `LECTURER` resolves to a `users.id` | Error | Yes (row) — unless thesis placeholder |
| `REGIST > MAX` | Warning | No — import proceeds, flag for admin |
| `REGIST == 0` | Warning | No — import proceeds, admin may deselect |
| `MID_DAY` / `FIN_DAY` both null | Warning | No — section created without exam schedule |
| `DAY == "TBA"` or `BTIME in ("TBA","0","0000","000")` | Warning | No |
| `LEVEL` not in (`Undergraduate`,`Graduate`) | Warning | No — default to Undergraduate |
| Exam date + room collision (same date+time+room for two sections) | Error | Yes — both rows flagged |
| Teacher assigned to two sections with identical exam date+time | Error | Yes — both rows flagged |

**Thesis / placeholder handling:**
- If `LECTURER` = thesis-advisor placeholder → set `section.teacher_id = null`, set `section.is_thesis = true` (new field)
- If `SECLEC = 0` and `SECLAB > 0` → lab-only / thesis section, no lecture room needed

**Insert/update logic:**
- `courses`: upsert on `course_id`
- `sections`: upsert on `(course_id, section_no, semester, academic_year)`
- `rooms`: upsert on `room_name` (normalized); capacity defaults to `MAX` if room is new
- `exam_schedules`: upsert on `(section_id, exam_type)`; only created if exam date is non-null

---

### 3.5 Step 5: Student Enrollment (Book1.xls)

**Source:** `Book1.xls`, sheet `regist_student_faculty`  
**Target tables:** `enrollment_records`, `sections.num_students`

**Pre-import parse steps:**
1. Read with `xlrd` engine, sheet name `regist_student_faculty`
2. Filter rows where `GRADE == "W"` → flag as withdrawn, exclude from exam list
3. Filter rows where `SEMESTER` matches target semester and `YEAR` matches target year

**Validations:**
| Check | Severity | Block? |
|---|---|---|
| `ID` non-null and 9 digits | Error | Yes (row) |
| `COURSENO` + `SECLEC` combination exists in `sections` table | Error | Yes (row) |
| `COURSENO=127798` (known orphan) | Error | Yes (row) — specific message |
| `GRADE == "W"` | Warning | No — skipped from exam list, still logged |
| `SNAME` null | Warning | No — international student record |
| `MAJOR` null | Warning | No — informational only |
| `TYPE_REGIST` not in (`K`,`P`,`I`,`S`,`A`,`O`,`L`,`C`) | Warning | No |
| Duplicate `(ID, COURSENO, SECLEC, SEMESTER, YEAR)` | Error | Yes (row) — de-duplicate |

**Insert logic:**
- Delete existing `enrollment_records` for this `import_session_id` before inserting
- Bulk insert all valid, non-withdrawn rows
- After insert, recount `sections.num_students` per section from actual enrollment_records
- Update `exam_schedules.total_sheets = num_students × num_pages` for affected sections

---

## 4. Validation Rule Engine

### 4.1 Complete Rule Table

Each rule has: id, target file, field, condition, severity, block_import, allow_override, message_template.

```
RULE-001  opencourse  COURESNO        Column named COURESNO (not COURSENO)     error    no   yes  "Column renamed COURESNO→COURSENO automatically"
RULE-002  opencourse  COURSENO        null or non-numeric                       error    yes  no   "Row {n}: COURSENO is missing or invalid"
RULE-003  opencourse  SECLEC          null                                      error    yes  no   "Row {n}: SECLEC is missing"
RULE-004  opencourse  (composite)     duplicate (COURSENO+SECLEC) in file       error    yes  no   "Row {n}: duplicate section {course}/{sec}"
RULE-005  opencourse  LECTURER        name cannot resolve to users.id           error    yes  yes  "Row {n}: lecturer '{name}' not found — map manually"
RULE-006  opencourse  LECTURER        thesis placeholder detected               info     no   n/a  "Row {n}: thesis advisor placeholder — teacher FK will be null"
RULE-007  opencourse  REGIST          REGIST > MAX                              warning  no   yes  "Row {n}: section {course}/{sec} over capacity by {diff}"
RULE-008  opencourse  REGIST          REGIST == 0                               warning  no   yes  "Row {n}: section {course}/{sec} has no enrolled students"
RULE-009  opencourse  MID_DAY/FIN_DAY both null for exam_type=midterm/final     warning  no   yes  "Row {n}: no exam date for {course}/{sec}"
RULE-010  opencourse  DAY/BTIME       DAY='TBA' or BTIME in (TBA,0,0000,000)   warning  no   yes  "Row {n}: {course}/{sec} has no scheduled time"
RULE-011  opencourse  (cross-row)     two sections: same date+time+room         error    yes  yes  "Rows {a},{b}: room conflict on {date} {time} in {room}"
RULE-012  opencourse  (cross-row)     same teacher: two sections same date+time error    yes  yes  "Rows {a},{b}: teacher {name} has exam schedule conflict"
RULE-013  enrollment  ID              null or not 9 digits                      error    yes  no   "Row {n}: student ID missing or invalid"
RULE-014  enrollment  COURSENO+SECLEC not found in sections table               error    yes  yes  "Row {n}: section {course}/{sec} not imported yet"
RULE-015  enrollment  COURSENO        COURSENO=127798 specifically              error    yes  no   "Row {n}: course 127798 has no matching section — must resolve manually"
RULE-016  enrollment  GRADE           'W' (withdrawn)                           warning  no   yes  "Row {n}: student {id} withdrawn from {course} — excluded from exam"
RULE-017  enrollment  SNAME           null                                      warning  no   no   "Row {n}: student {id} has no surname"
RULE-018  enrollment  (composite)     duplicate (ID+COURSENO+SECLEC)            error    yes  no   "Row {n}: duplicate enrollment for student {id}"
RULE-019  enrollment  MAJOR           null                                      warning  no   no   "Row {n}: student {id} has no major"
RULE-020  personnel   cmu_mail        null or not *@cmu.ac.th                   error    yes  no   "Row {n}: invalid or missing cmu_mail"
RULE-021  personnel   cmu_mail        duplicate within file                     error    yes  no   "Row {n}: duplicate cmu_mail {mail}"
RULE-022  personnel   department      not in (GOV,PA,IR,STB)                   error    yes  no   "Row {n}: unknown department '{dept}'"
RULE-023  employee    cmu_mail        null                                      error    yes  no   "Row {n}: missing cmu_mail"
RULE-024  employee    role            not in (Secretary,Head_of_Unit,Staff)     error    yes  no   "Row {n}: unknown role '{role}'"
RULE-025  employee    department      exam-role tag not in known set (nullable) warning  no   yes  "Row {n}: exam-role tag '{tag}' is unrecognized — will be ignored"
```

### 4.2 Override Behavior

Rules with `allow_override=yes` can be bypassed by admin. When admin overrides a warning or error:
- Reason must be entered in a text field (min 10 chars)
- Override is stored in `import_row_logs.override_reason`
- Override actor and timestamp stored in `import_row_logs`
- Overridden errors still appear in audit log but do not block the row

Rules with `allow_override=no` are hard blocks — the row cannot be selected for import until the underlying data is fixed or the row is deselected entirely.

---

## 5. UX / UI Structure

### 5.1 Overall Flow

```
[1] Upload  →  [2] Parse Preview  →  [3] Validation Summary  
→  [4] Row Table  →  [5] Conflict Map  →  [6] Final Summary  →  [7] Confirm
```

Admin can go back to any step. No data is written until Step 7 confirms.

---

### 5.2 Step 1 — Upload

**Component:** `ImportUploadStep`

- File picker + drag-and-drop zone
- Accept: `.xls, .xlsx, .csv`
- Form fields:
  - Import type selector: `opencourse` | `enrollment` | `personnel` | `employee`
  - Academic year text input (pre-filled from active ExamPeriod)
  - Semester selector: `1` | `2`
  - Exam type selector: `midterm` | `final` (only shown for opencourse)
- After file selected: show filename, size, detected format
- "Parse File" button → calls `POST /api/import/v2/preview`

---

### 5.3 Step 2 — Parse Preview

**Component:** `ImportParsePreview`

- Show first 20 parsed rows in a raw table — no validation applied yet
- Show detected column names. If `COURESNO` found → display banner:
  > "Column COURESNO detected and will be renamed to COURSENO automatically. Please confirm."
  > [Confirm rename] button — required before proceeding
- Show file stats: total rows parsed, detected encoding, detected format
- If Thai text columns detected → show encoding notice
- "Run Validation" button → calls `POST /api/import/v2/validate`

---

### 5.4 Step 3 — Validation Summary

**Component:** `ImportValidationSummary`

```
┌─────────────────────────────────────────────────────────────┐
│  File: opencourse.xls   |   165 rows parsed                 │
├─────────────────────────────────────────────────────────────┤
│  ✅  Valid:     148 rows    (89.7%)                         │
│  ⚠️   Warning:   12 rows    (7.3%)   — will import unless   │
│                                        deselected           │
│  ❌  Error:       5 rows    (3.0%)   — BLOCKED              │
├─────────────────────────────────────────────────────────────┤
│  Blocking issues (must resolve before confirm):             │
│  • 5 lecturer names unresolved → open mapping panel         │
│                                                             │
│  Non-blocking issues (review recommended):                  │
│  • 4 over-enrolled sections                                 │
│  • 4 sections with no students                              │
│  • 117 sections missing exam date                           │
│  • 37 sections with TBA schedule                            │
└─────────────────────────────────────────────────────────────┘
```

- "View Row Table" button → Step 4
- "Resolve Lecturer Mapping" button (shown when unresolved lecturers exist) → opens Mapping Panel

---

### 5.5 Lecturer Mapping Panel

**Component:** `LecturerMappingPanel`

Shown as a slide-over panel when unresolved lecturers exist. One card per unresolved name:

```
┌──────────────────────────────────────────────────────────────┐
│  Unresolved: "[garbled Thai string]"                         │
│  Appears in: 126452 sec 1,  126441 sec 1                     │
│                                                              │
│  Suggested match:  pichaarpa.p@cmu.ac.th (dept: IR)          │
│  [Confirm match]  [Search other teacher ▼]  [Skip this row]  │
│                                                              │
│  Search: [ type name or email...              ]              │
│  Results: dropdown of teachers filtered by input             │
│                                                              │
│  ☑ Apply this mapping to all sections with the same name     │
└──────────────────────────────────────────────────────────────┘
```

- Auto-suggest: backend returns top-3 fuzzy matches by surname token
- "Skip this row" = deselect all rows containing this lecturer name; they will not be imported
- Panel completion: all unresolved lecturers must be either mapped or skipped

---

### 5.6 Step 4 — Row-Level Table

**Component:** `ImportRowTable`

| Col | Type | Description |
|---|---|---|
| ☑ | Checkbox | Select/deselect this row. Error rows deselected by default |
| `#` | int | Row number in source file |
| Status | badge | ✅ Valid / ⚠️ Warning / ❌ Error |
| Error reason | string | Plain text; empty if valid |
| Mapping | badge | "Lecturer resolved" / "Lecturer unresolved" |
| Data columns | string | All parsed values inline |
| Action | button | "Override warning" button (for warning rows) / "Fix" (for error rows with fixable data) |

**Table behaviors:**
- Error rows: checkbox disabled (cannot select) until overridden or underlying data fixed inline
- Warning rows: checkbox checked by default; admin can uncheck
- Valid rows: checkbox checked by default
- Batch controls: "Select all valid", "Deselect all errors", "Deselect all warnings"
- Filter: dropdown — All / Valid only / Warnings only / Errors only
- Sort: by any column header

**Inline fix for selected error types:**
- RULE-005 (unresolved lecturer): dropdown appears inline to select teacher
- RULE-007/008 (over-enrolled / empty): override button opens override reason dialog

---

### 5.7 Step 5 — Conflict Map (opencourse only)

**Component:** `ImportConflictMap`

Shown only when importing opencourse and exam dates are present.

- Matrix view: rows = exam dates, columns = time slots, cells = sections scheduled
- Red cells = conflicts (two sections in same room+time)
- Click cell → show section details + conflicting section
- Admin can deselect conflicting section from this view

---

### 5.8 Step 6 — Final Summary

**Component:** `ImportFinalSummary`

```
┌─────────────────────────────────────────────────────────────┐
│  Import Summary — Ready to confirm                          │
├──────────────────┬──────────────────────────────────────────┤
│  Total rows:     │  165                                     │
│  Will create:    │  148 sections, 82 courses, 30 rooms      │
│  Will update:    │  17 existing sections                    │
│  Will skip:      │  5 rows (deselected or error)            │
│  Blocking issues │  0    ← must be 0 to enable confirm      │
├──────────────────┴──────────────────────────────────────────┤
│  Overrides applied: 2                                       │
│  • Row 27: over-enrolled — "confirmed by registrar"         │
│  • Row 33: over-enrolled — "waitlist approved"              │
└─────────────────────────────────────────────────────────────┘

[← Back to Row Table]          [Confirm Import  →]
```

- "Confirm Import" button is **disabled** if any blocking issues remain
- If re-importing (session exists): show diff — created/updated/skipped counts

---

### 5.9 Step 7 — Confirm Import

- Confirmation modal:
  > "This will write 148 records for Semester 2/2568. All overrides will be logged. This action can be reviewed in the audit log but cannot be automatically undone."
  > [Cancel]  [Confirm Import]
- After confirm: progress bar → redirects to session summary page
- Session summary shows final stats + link to audit log

---

### 5.10 Audit Log Behavior

Every import action writes to `import_row_logs`:
- One row per source file row (valid, warning, error, skipped)
- Includes: `session_id`, `row_number`, `raw_data` (JSONB), `status`, `error_code`, `error_message`, `was_selected`, `was_imported`, `override_reason`, `override_by`, `override_at`
- Audit log is **append-only** — no deletes
- Accessible from Import History page: click session → see all rows + statuses

---

## 6. API Contract

All new endpoints are under `/api/import/v2/`. Existing v1 endpoints at `/api/import/` are untouched.

---

### 6.1 `POST /api/import/v2/preview`

**Purpose:** Parse file, return raw rows + detected schema. No validation, no DB write.  
**Auth:** admin required  
**Content-Type:** `multipart/form-data`

**Request:**
```
file:          UploadFile   — the source file
import_type:   string       — "opencourse" | "enrollment" | "personnel" | "employee"
academic_year: string       — e.g. "2568"
semester:      string       — "1" | "2"
exam_type?:    string       — "midterm" | "final" (required if import_type=opencourse)
```

**Response 200:**
```json
{
  "import_type": "opencourse",
  "file_name": "opencourse.xls",
  "file_format": "html_xls",
  "encoding": "utf-8",
  "total_rows": 165,
  "columns_detected": ["COURESNO","TITLE","SECLEC",...],
  "column_warnings": [
    {"original": "COURESNO", "rename_to": "COURSENO", "reason": "known typo in source"}
  ],
  "preview_rows": [
    {"_row": 0, "COURSENO": "126101", "TITLE": "Introduction to...", "SECLEC": 1, ...},
    ...
  ]
}
```

**Response 400:** `{"detail": "Cannot read file — unsupported format or corrupted"}`

---

### 6.2 `POST /api/import/v2/validate`

**Purpose:** Run all validation rules against parsed data. No DB write.  
**Auth:** admin required  
**Content-Type:** `multipart/form-data`

**Request:** same fields as preview, plus:
```
column_renames: JSON string  — e.g. '[{"from":"COURESNO","to":"COURSENO"}]'
```

**Response 200:**
```json
{
  "summary": {
    "total_rows": 165,
    "valid": 148,
    "warning": 12,
    "error": 5,
    "blocking_count": 5
  },
  "rows": [
    {
      "_row": 0,
      "status": "valid",
      "error_code": null,
      "error_message": null,
      "mapping_status": "resolved",
      "data": { "COURSENO": "126101", "SECLEC": 1, ... }
    },
    {
      "_row": 4,
      "status": "error",
      "error_code": "RULE-005",
      "error_message": "Lecturer '[garbled]' not found — map manually",
      "mapping_status": "unresolved",
      "suggested_matches": [
        {"teacher_id": 38, "full_name": "...", "cmu_mail": "pichaarpa.p@cmu.ac.th", "department": "IR"}
      ],
      "data": { "COURSENO": "126452", "SECLEC": 1, ... }
    }
  ],
  "lecturer_unresolved": [
    {
      "raw_name": "[garbled]",
      "appears_in_rows": [4, 35],
      "suggested_matches": [...]
    }
  ],
  "conflict_map": [
    {
      "type": "room_conflict",
      "rows": [27, 33],
      "date": "2026-01-29",
      "time": "15:30-18:30",
      "room": "PSB1309"
    }
  ]
}
```

---

### 6.3 `POST /api/import/v2/confirm`

**Purpose:** Execute the import. Write to DB. Create audit log.  
**Auth:** admin required  
**Content-Type:** `application/json`

**Request body:**
```json
{
  "import_type": "opencourse",
  "academic_year": "2568",
  "semester": "2",
  "exam_type": "final",
  "selected_rows": [0, 1, 2, 3, 5, 6],
  "lecturer_mappings": [
    {"raw_name": "[garbled]", "teacher_id": 38},
    {"raw_name": "MATTHEW ROBSON", "teacher_id": 39}
  ],
  "overrides": [
    {
      "row": 27,
      "rule_code": "RULE-007",
      "reason": "Over-enrollment confirmed by registrar office"
    }
  ],
  "file_token": "abc123def456"
}
```

> `file_token` is a temporary token issued by the `/validate` endpoint that references the server-cached parsed data, avoiding re-upload.

**Response 200:**
```json
{
  "status": "ok",
  "session_id": 42,
  "stats": {
    "courses_created": 82,
    "courses_updated": 8,
    "sections_created": 148,
    "sections_updated": 17,
    "rooms_created": 30,
    "exam_schedules_created": 48,
    "rows_imported": 148,
    "rows_skipped": 5,
    "overrides_applied": 2
  }
}
```

**Response 400:** `{"detail": "Blocking issues remain — confirm rejected"}` (if client sends rows with unresolved errors that were not deselected)

**Response 409:** `{"detail": "Import locked — exam period is confirmed. Contact administrator."}` (if OptimizeSession is locked)

---

### 6.4 `GET /api/import/v2/teachers/search`

**Purpose:** Teacher lookup for lecturer mapping panel.  
**Auth:** admin required

**Query params:**
- `q`: string — search by name token or email fragment (min 2 chars)
- `department?`: string — filter by GOV/PA/IR/STB

**Response 200:**
```json
[
  {
    "teacher_id": 38,
    "full_name": "...",
    "cmu_mail": "pichaarpa.p@cmu.ac.th",
    "department": "IR",
    "title": "..."
  }
]
```

---

### 6.5 `GET /api/import/sessions` (existing — no change)

Returns list of `ImportSession` objects. Schema unchanged.

---

### 6.6 `GET /api/import/sessions/{id}/logs`

**Purpose:** Return row-level audit log for a session.  
**Auth:** admin required

**Response 200:**
```json
{
  "session_id": 42,
  "rows": [
    {
      "id": 1001,
      "row_number": 0,
      "status": "imported",
      "error_code": null,
      "was_selected": true,
      "was_imported": true,
      "override_reason": null,
      "raw_data": { "COURSENO": "126101", ... }
    }
  ]
}
```

---

## 7. State Management Plan

### 7.1 Backend State (persisted in DB)

| State | Where stored | Lifetime |
|---|---|---|
| Parsed file data (during preview) | Server-side temp cache (in-memory dict keyed by `file_token`, TTL 30 min) | Temporary — purged after confirm or timeout |
| `ImportSession` | `import_sessions` table | Permanent — one per (year, semester, exam_type) |
| `import_row_logs` | `import_row_logs` table | Permanent — append-only audit |
| Imported courses/sections/enrollments | `courses`, `sections`, `enrollment_records` | Permanent |

### 7.2 Frontend State (React component state + context)

The import wizard is a **multi-step form** with shared state across steps. Use a single `useImportWizard` hook with `useReducer`.

**Import wizard state shape:**
```typescript
interface ImportWizardState {
  // Step 1 — Upload
  step: 1 | 2 | 3 | 4 | 5 | 6 | 7;
  importType: "opencourse" | "enrollment" | "personnel" | "employee" | null;
  academicYear: string;
  semester: string;
  examType: "midterm" | "final" | null;
  file: File | null;

  // Step 2 — Parse Preview
  previewResult: PreviewResult | null;
  columnRenames: ColumnRename[];

  // Step 3/4 — Validation
  validationResult: ValidationResult | null;
  fileToken: string | null;

  // Step 4 — Row Selection
  selectedRows: Set<number>;     // row indices selected for import
  overrides: RowOverride[];      // { row, rule_code, reason }

  // Lecturer mapping
  lecturerMappings: LecturerMapping[];  // { raw_name, teacher_id }

  // Step 6 — Final
  finalStats: ImportFinalStats | null;

  // Loading flags
  loading: boolean;
  error: string | null;
}
```

**Actions:**
```typescript
type ImportWizardAction =
  | { type: "SET_STEP"; payload: number }
  | { type: "SET_FILE_META"; payload: { file; importType; academicYear; semester; examType } }
  | { type: "SET_PREVIEW"; payload: PreviewResult }
  | { type: "CONFIRM_RENAME"; payload: ColumnRename[] }
  | { type: "SET_VALIDATION"; payload: { result: ValidationResult; fileToken: string } }
  | { type: "TOGGLE_ROW"; payload: number }
  | { type: "SELECT_ALL_VALID" }
  | { type: "DESELECT_ALL_ERRORS" }
  | { type: "SET_LECTURER_MAPPING"; payload: LecturerMapping }
  | { type: "SET_OVERRIDE"; payload: RowOverride }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_ERROR"; payload: string | null }
  | { type: "RESET" };
```

### 7.3 What Is Purely UI State (not persisted)

- Which step is active
- Filter/sort state of the row table
- Whether the lecturer mapping panel is open
- Whether the conflict map is expanded
- Override reason dialog open/close
- Row selection checkboxes

These live in component local state (`useState`) inside the step components and are not part of the wizard reducer.

---

## 8. Data Model / Tables

### 8.1 Existing Tables (no schema changes required)

| Table | Use in import | Notes |
|---|---|---|
| `users` | Teachers and staff are users | `role` = `teacher` or `staff` or `admin` |
| `courses` | Created from opencourse | `course_id` = string course code |
| `sections` | Created from opencourse | `section_no` = string e.g. "1", "701", "801" |
| `rooms` | Created from opencourse ROOM column | |
| `exam_schedules` | Created from MID_DAY/FIN_DAY in opencourse | |
| `import_sessions` | One per (year, semester, exam_type) | |
| `enrollment_records` | One per student per section | |

### 8.2 Schema Changes Required

#### Add to `sections` table

```sql
ALTER TABLE sections ADD COLUMN is_thesis BOOLEAN DEFAULT FALSE;
```

Used to flag sections where LECTURER is a thesis advisor placeholder. Prevents FK constraint error for null `teacher_id`.

#### New table: `import_row_logs`

```sql
CREATE TABLE import_row_logs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id       INTEGER NOT NULL REFERENCES import_sessions(id),
    row_number       INTEGER NOT NULL,
    raw_data         JSON NOT NULL,
    status           TEXT NOT NULL,      -- 'valid' | 'warning' | 'error' | 'skipped' | 'imported'
    error_code       TEXT,               -- e.g. 'RULE-005'
    error_message    TEXT,
    was_selected     BOOLEAN,
    was_imported     BOOLEAN,
    override_reason  TEXT,
    override_by      INTEGER REFERENCES users(id),
    override_at      DATETIME,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_import_row_logs_session ON import_row_logs(session_id);
```

#### New table: `lecturer_name_map`

```sql
CREATE TABLE lecturer_name_map (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_name      TEXT NOT NULL,      -- garbled string from opencourse file
    teacher_id    INTEGER NOT NULL REFERENCES users(id),
    confirmed_by  INTEGER REFERENCES users(id),
    confirmed_at  DATETIME,
    UNIQUE(raw_name)
);
```

This table persists lecturer name resolutions across import sessions. Once an admin maps a garbled name to a teacher_id, future imports auto-resolve it.

### 8.3 Master vs Transactional Classification

| Table | Type | Re-imported each term? |
|---|---|---|
| `users` (teachers + staff) | Global master | No — upsert only; add new hires |
| `courses` | Global master | No — upsert only |
| `rooms` | Global master | No — upsert only |
| `lecturer_name_map` | Global master | No — persistent lookup |
| `exam_periods` | Term master | Yes — one per semester |
| `sections` | Per-term transactional | Yes — new rows each semester |
| `exam_schedules` | Per-term transactional | Yes |
| `enrollment_records` | Per-term transactional | Yes — deleted and rebuilt per session |
| `import_sessions` | Per-term audit | Yes |
| `import_row_logs` | Per-term audit | Yes — append-only |

---

## 9. Implementation Plan for Codex

### 9.1 Backend — Files to Create

```
backend/routers/imports_v2.py
```
New router. Does NOT modify `imports.py`. Register at `/api/import/v2`.

Contains:
- `POST /preview` → `import_v2_preview()`
- `POST /validate` → `import_v2_validate()`
- `POST /confirm` → `import_v2_confirm()`
- `GET /teachers/search` → `search_teachers()`
- `GET /sessions/{id}/logs` → `get_session_logs()`

Internal helper modules (can be in same file or separate):

```
backend/import_v2/
    __init__.py
    parsers.py        — read_file_by_type(), normalize_cols(), parse_thai_date()
    validators.py     — run_validation(df, import_type, db) → List[RowResult]
    teacher_resolver.py — resolve_lecturer_name(name, db) → teacher_id | None
    importer.py       — execute_import(validated_rows, mappings, overrides, session, db)
    file_cache.py     — store_parsed_df(token, df), retrieve_parsed_df(token) → df
```

```
backend/migrate_v2_import.py
```
Migration script to:
1. Add `sections.is_thesis` column
2. Create `import_row_logs` table
3. Create `lecturer_name_map` table

### 9.2 Backend — Files to Register

In `main.py`, add:
```python
from routers import imports_v2
app.include_router(imports_v2.router, prefix="/api/import/v2", tags=["import-v2"])
```

No changes to any existing router.

### 9.3 Backend — models.py Changes

Add `ImportRowLog` model:
```python
class ImportRowLog(Base):
    __tablename__ = "import_row_logs"
    id              = Column(Integer, primary_key=True)
    session_id      = Column(Integer, ForeignKey("import_sessions.id"), nullable=False)
    row_number      = Column(Integer, nullable=False)
    raw_data        = Column(JSON, nullable=False)
    status          = Column(String(20), nullable=False)
    error_code      = Column(String(20))
    error_message   = Column(Text)
    was_selected    = Column(Boolean)
    was_imported    = Column(Boolean)
    override_reason = Column(Text)
    override_by     = Column(Integer, ForeignKey("users.id"))
    override_at     = Column(DateTime(timezone=True))
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
```

Add `LecturerNameMap` model:
```python
class LecturerNameMap(Base):
    __tablename__ = "lecturer_name_map"
    id           = Column(Integer, primary_key=True)
    raw_name     = Column(String(300), unique=True, nullable=False)
    teacher_id   = Column(Integer, ForeignKey("users.id"), nullable=False)
    confirmed_by = Column(Integer, ForeignKey("users.id"))
    confirmed_at = Column(DateTime(timezone=True))
```

Add `is_thesis` to `Section`:
```python
is_thesis = Column(Boolean, default=False)
```

### 9.4 Frontend — Files to Create

```
src/pages/ImportV2.tsx                   — wizard page container; renders active step
src/hooks/useImportWizard.ts             — useReducer hook; full wizard state + actions
src/services/import-v2.service.ts        — API calls: previewImport(), validateImport(), confirmImport(), searchTeachers()
src/types/import-v2.types.ts             — TypeScript interfaces: ImportWizardState, PreviewResult, ValidationResult, RowResult, etc.
src/components/import/
    ImportUploadStep.tsx                 — Step 1
    ImportParsePreview.tsx               — Step 2
    ImportValidationSummary.tsx          — Step 3
    LecturerMappingPanel.tsx             — slide-over panel for lecturer resolution
    ImportRowTable.tsx                   — Step 4 — row-level table with checkboxes
    ImportConflictMap.tsx                — Step 5 — exam date/room conflict matrix
    ImportFinalSummary.tsx               — Step 6
    ImportOverrideDialog.tsx             — modal for override reason input
```

### 9.5 Frontend — Files to Update

```
src/App.tsx (or router config)           — add route for /import-v2
src/components/ui/Sidebar.tsx            — add nav link "นำเข้าข้อมูล v2" (or replace existing Import link)
src/services/import.service.ts           — add getSessionLogs(sessionId)
src/types/api.ts                         — add ImportRowLog, LecturerNameMap interfaces
```

### 9.6 Frontend — Component Responsibilities

| Component | Props | Emits |
|---|---|---|
| `ImportV2.tsx` | none | — |
| `useImportWizard` | — | dispatch, state |
| `ImportUploadStep` | `onNext(meta)` | file selected + meta |
| `ImportParsePreview` | `previewResult`, `onConfirmRenames`, `onNext` | column renames confirmed |
| `ImportValidationSummary` | `validationResult`, `onOpenMapping`, `onNext` | |
| `LecturerMappingPanel` | `unresolvedLecturers`, `onMap(raw_name, teacher_id)`, `onSkip(raw_name)` | mapping decisions |
| `ImportRowTable` | `rows`, `selectedRows`, `onToggle`, `onOverride`, `onBatchSelect` | row selections, overrides |
| `ImportConflictMap` | `conflicts`, `selectedRows`, `onDeselect(row)` | row deselections |
| `ImportFinalSummary` | `state`, `onConfirm`, `onBack` | confirm action |
| `ImportOverrideDialog` | `row`, `ruleCode`, `onConfirm(reason)`, `onCancel` | override with reason |

### 9.7 Migration Requirements

Run before any V2 import is attempted:

```bash
python backend/migrate_v2_import.py
```

The script must be idempotent — check if columns/tables exist before adding.

### 9.8 Testing Requirements

Backend (pytest):
- `test_preview_opencourse_html_xls` — verify COURESNO rename detected
- `test_validate_unresolved_lecturer` — RULE-005 fires for 5 garbled names
- `test_validate_orphan_courseno` — RULE-015 fires for 127798
- `test_validate_withdrawal` — RULE-016 fires for GRADE=W rows
- `test_confirm_import_blocked_when_errors_remain`
- `test_confirm_import_writes_row_logs`
- `test_lecturer_name_map_persists_across_sessions`

Frontend (Vitest + Testing Library):
- `ImportRowTable` — deselected error rows cannot be submitted
- `LecturerMappingPanel` — apply-to-all applies mapping to all rows with same name
- `useImportWizard` — state transitions between steps

---

## 10. Risks and Ambiguities

### 10.1 Known Data Problems Requiring Admin Decision

| Issue | Description | Required action before import |
|---|---|---|
| `COURSENO=127798` in enrollment | Appears in Book1.xls but has no matching entry in opencourse. Unknown if course was cancelled or erroneously included | Admin must decide: skip all enrollment rows for this course, or manually create a section record |
| 4 zero-enrollment sections | Courses 127492, 128351, 128799, 140105 have REGIST=0. May be cancelled or newly opened | Admin must confirm: import as inactive sections, or skip |
| 4 over-enrolled sections | 126440, 126449, 128305, 128310 have REGIST > MAX | Admin must confirm each. If imported, override reason required |
| `department` exam-role codes in Employee CSV | ESQ/GOV/IA/PA/STB/ADMIN are present on 8/37 staff rows but meaning is undocumented | Admin must document: what system permissions/visibility does each code grant? Until confirmed, store as `dept_code` but do not use for access control |
| Section 7xx / 8xx semantics | 1,764 enrollment rows in 700-series and 800-series sections. Whether these require different exam room assignment (separate venue, different timing, different invigilators) is not documented | Admin must confirm before exam room assignment workflow |
| `SNAME` null on 165 student rows | Mostly international students with English-only names and some encoding gaps | Admin must confirm: do these students need special handling on ID cards or exam lists? |
| Missing MID_DAY/FIN_DAY on 117 opencourse sections | 71% of sections have no exam date in the source file | Admin must confirm: are these sections exempt from centralized exam scheduling, or will dates be entered manually in the EMS after import? |

### 10.2 Thai Encoding

The source files were exported from a Thai university system. Thai column values in `LECTURER` are corrupted when read by Python in some environments because the HTML export uses `TIS-620` internally but claims `UTF-8`. **Never join on Thai name strings.** Use `cmu_mail` as the sole join key. The `lecturer_name_map` table stores the corrupted string as-is (raw bytes → stored as opaque key) and maps it to a `teacher_id`.

### 10.3 File Format Fragility

`opencourse.xls` and `Book1.xls` are not real Excel files. They are HTML tables with `.xls` extension. The correct parser is `pd.read_html()`. If the registrar's office changes their export format, the parser will break silently (may try `xlrd` first and fail). The `read_uploaded_file()` function must try engines in this order: `openpyxl` → `xlrd` → `read_html`. Currently this is already implemented in `imports.py` but must be verified for the v2 path.

### 10.4 `file_token` Cache Implementation

The `/validate` endpoint caches the parsed DataFrame server-side and issues a token. The `/confirm` endpoint uses this token to avoid re-parsing. Implementation options:
- **Simple (recommended):** Python `dict` in module scope, keyed by UUID, value = `(df, metadata, expiry_timestamp)`. Background task or on-access cleanup for expired entries.
- **Robust:** Redis if available. Not currently in the stack.
- **Fallback:** If token expires or is missing, `/confirm` returns `400` asking client to re-upload.

### 10.5 Assumptions That Need Confirmation

1. `TYPE_REGIST` codes K/P/I/S/A/O/L/C — are any of these codes exam-ineligible? If so, they need filtering rules.
2. Whether `FAC_ID` values in enrollment map to a faculty master that needs to be maintained in the EMS, or whether `FAC_NAME` string is sufficient for display.
3. Whether the `remark = "��� 3"` on 4 teacher rows means "assigned to exam room 3" and whether this should affect room assignment logic.
4. Whether graduate-level sections (LEVEL=Graduate) require a separate invigilator assignment workflow from undergraduate sections.
5. Whether re-importing opencourse for the same (year, semester, exam_type) should overwrite existing exam schedules (current behavior in v1) or reject unless previous session is explicitly marked complete.

---

*Spec version: 2.0 | Generated: 2026-04-21 | Based on real file analysis of Semester 2/2568 data*
