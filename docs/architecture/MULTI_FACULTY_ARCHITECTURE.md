# Multi-Faculty Architecture
## EMS — Removing Single-Faculty Hardcoding and Preparing for Multi-Tenant Deployment

> **Audience:** University IT management, senior architects planning next EMS generation
> **Scope:** Current single-faculty assumptions, multi-tenant data model, RBAC extension, signer configuration, migration path, feature flag strategy
> **Reference files:** `backend/staff_workloads.py`, `backend/auth_utils.py`, `backend/academic_groups.py`, `backend/models.py`

---

## 1. Current Single-Faculty Hardcoding

The EMS system is currently deployed for one faculty: คณะรัฐศาสตร์และรัฐประศาสนศาสตร์ มช.
The following are concrete hardcoded assumptions that must change for multi-faculty support.
Each entry includes the file location, current value, and the reason it is a multi-faculty blocker.

### 1a. Staff Distribution Division
**File:** `backend/staff_workloads.py` line 14
```python
PAPER_DISTRIBUTION_DIVISION = "Education_Student_Quality"
```
**Problem:** Hard-wired to one faculty's org structure. Another faculty will have a different
division name for paper distribution staff.
**Fix:** Database-backed `StaffExclusionRule` table with `faculty_id` scope, OR a
`FacultyConfig` setting.

### 1b. Named Individual Exclusions from Distribution
**File:** `backend/staff_workloads.py` lines 15–16
```python
PAPER_DISTRIBUTION_EXCLUDED_USERNAMES = {"araya.fa", "sapanyu.wong"}
PAPER_DISTRIBUTION_EXCLUDED_NAME_SNIPPETS = ("อารยา", "สัพพัญญู")
```
**Problem:** Person-specific exclusions hardcoded in source code. Adding or removing a person
requires a code deployment. Completely unusable for any other faculty.
**Fix:** `StaffExclusionRule` table (see Section 5).

### 1c. Workflow Signer Order
**File:** `backend/auth_utils.py` line 473
```python
SIGN_ORDER_USERNAMES = ["atikant.s", "mathawee.m", "napaporn.ph", "paweena.t"]
```
**Problem:** Hard-wired signing sequence for one faculty. Another faculty has different signers
and may have a different number of signing rounds. Moving to another faculty requires a code
change and redeployment.
**Fix:** `WorkflowSignerConfig` table (see Section 4).

### 1d. Department Code Classification
**File:** `backend/academic_groups.py` (entire file)
**Current:** Department codes `GOV`, `PA`, `IR`, `STB` are hardcoded with their Thai/English labels.
**Problem:** Another faculty will have different department codes. The mapping is compiled into
the `academic_groups.py` module and imported by `models.py`, coupling the data layer to a
single faculty's org structure.
**Fix:** `Department` table seeded from configuration (see Section 5).

### 1e. Single `ExamPeriod` Active at a Time (System-Wide)
**File:** `backend/term_lifecycle.py`, `get_active_period()` function
**Problem:** There is one `active` period for the entire system. If two faculties use EMS
simultaneously, they cannot each have their own active period.
**Fix:** Add `faculty_id` to `ExamPeriod` so periods are faculty-scoped.

### 1f. Room Pool is System-Wide
**Problem:** All `Room` records are shared across the whole system. A second faculty would
need its own room definitions, but currently rooms are not scoped to a faculty.
**Fix:** Add nullable `faculty_id` to `Room`; shared rooms get `faculty_id = NULL`.

### 1g. User Records Are Faculty-Agnostic
**Problem:** `User.dept_code` uses the single-faculty department codes. Staff from another
faculty cannot be cleanly distinguished.
**Fix:** Add `faculty_id` to `User`; `dept_code` becomes faculty-scoped.

---

## 2. Multi-Tenant Data Model

### New Table: `Faculty`
```python
class Faculty(Base):
    __tablename__ = "faculties"
    id           = Column(Integer, primary_key=True)
    code         = Column(String(20), unique=True, nullable=False)  # e.g., "POLISCI"
    name_th      = Column(String(200), nullable=False)
    name_en      = Column(String(200), nullable=False)
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
```

### Column Additions (via migration)

| Table | Column to Add | Type | Default | Notes |
|-------|--------------|------|---------|-------|
| `users` | `faculty_id` | `Integer FK → faculties.id`, nullable | Seed: 1 | Nullable for system admin users |
| `exam_periods` | `faculty_id` | `Integer FK → faculties.id`, nullable | Seed: 1 | Nullable for backwards compat |
| `rooms` | `faculty_id` | `Integer FK → faculties.id`, nullable | NULL | NULL = shared across faculties |
| `sections` | `faculty_id` | `Integer FK → faculties.id`, nullable | Seed: 1 | Through period association |
| `staff_unavailability` | `faculty_id` | `Integer FK → faculties.id`, nullable | Seed: 1 | Scope unavailability per faculty |

All `faculty_id` additions use `nullable=True` so existing rows are not broken. A migration
script seeds the default faculty and populates `faculty_id = 1` on all existing rows.

---

## 3. RBAC Extension for Multi-Faculty

### Current Role Scope
Today, all roles are system-wide. `dept_supervisor` can see all sections from their `dept_code`,
but `dept_code` is a string that implicitly belongs to the single faculty.

### Target Role Scope
When `MULTI_FACULTY_ENABLED = True`:

| Role | Scope | Change |
|------|-------|--------|
| `admin` | System-wide (all faculties) | No change |
| `esq_head` | Faculty-scoped (own faculty) | NEW: `esq_head.faculty_id` enforced |
| `secretary` | Faculty-scoped (own faculty) | NEW: `secretary.faculty_id` enforced |
| `dept_supervisor` | Dept-scoped within own faculty | `dept_code` + `faculty_id` both checked |
| `teacher` | Own sections within own faculty | `faculty_id` scope check added |
| `staff` | Invigilation assignments within own faculty | `faculty_id` scope check added |
| `print_shop` | All print jobs (system-wide) | No change |
| `student` | Own schedule lookup | No change |

### Implementation
The `permissions.get_dept_filter()` function will need a `faculty_filter` equivalent:
```python
def get_faculty_filter(user: models.User) -> int | None:
    """Returns faculty_id restriction, or None = all faculties (admin)."""
    if user.role == UserRole.admin:
        return None
    return getattr(user, "faculty_id", None)
```

All domain queries must add `faculty_id = get_faculty_filter(user)` when not None.

---

## 4. WorkflowSignerConfig Table

Replace `SIGN_ORDER_USERNAMES` with a database table:

```python
class WorkflowSignerConfig(Base):
    __tablename__ = "workflow_signer_configs"
    id           = Column(Integer, primary_key=True)
    faculty_id   = Column(Integer, ForeignKey("faculties.id"), nullable=False)
    round        = Column(Integer, nullable=False)     # 1 or 2
    order_index  = Column(Integer, nullable=False)     # position in signing order
    username     = Column(String(100), nullable=False) # must match users.username
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("faculty_id", "round", "order_index"),
    )
```

**Seeding for the current faculty:**
```sql
INSERT INTO workflow_signer_configs (faculty_id, round, order_index, username) VALUES
(1, 1, 1, 'atikant.s'),
(1, 1, 2, 'mathawee.m'),
(1, 1, 3, 'napaporn.ph'),
(1, 1, 4, 'paweena.t'),
(1, 2, 1, 'atikant.s'),  -- Round 2 signers (may differ)
(1, 2, 2, 'mathawee.m'),
(1, 2, 3, 'napaporn.ph'),
(1, 2, 4, 'paweena.t');
```

**Usage in `optimize_workflow.py`:**
```python
# Replace: if username in SIGN_ORDER_USERNAMES
# With:
signers = db.query(WorkflowSignerConfig).filter(
    WorkflowSignerConfig.faculty_id == session.faculty_id,
    WorkflowSignerConfig.round == current_round,
    WorkflowSignerConfig.is_active == True,
).order_by(WorkflowSignerConfig.order_index).all()
```

---

## 5. Staff Exclusion Rules Table

Replace `PAPER_DISTRIBUTION_EXCLUDED_USERNAMES` with a database table:

```python
class StaffExclusionRule(Base):
    __tablename__ = "staff_exclusion_rules"
    id           = Column(Integer, primary_key=True)
    faculty_id   = Column(Integer, ForeignKey("faculties.id"), nullable=False)
    rule_type    = Column(String(50), nullable=False)  # "paper_distribution"
    match_type   = Column(String(20), nullable=False)  # "username" | "name_snippet" | "division" | "special_role"
    match_value  = Column(String(200), nullable=False)
    reason       = Column(String(500))
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
```

**Seeding for the current faculty (paper distribution exclusions):**
```sql
INSERT INTO staff_exclusion_rules (faculty_id, rule_type, match_type, match_value, reason) VALUES
(1, 'paper_distribution', 'username', 'araya.fa', 'ESQ staff — not distribution candidate'),
(1, 'paper_distribution', 'username', 'sapanyu.wong', 'ESQ staff — not distribution candidate'),
(1, 'paper_distribution', 'special_role', 'room_keeper', 'Room keepers open/close rooms, not distribute');
```

**Usage in `staff_workloads.py`:**
```python
def is_paper_distribution_candidate(user: models.User, db: Session) -> bool:
    exclusions = db.query(StaffExclusionRule).filter(
        StaffExclusionRule.faculty_id == user.faculty_id,
        StaffExclusionRule.rule_type == "paper_distribution",
        StaffExclusionRule.is_active == True,
    ).all()
    for rule in exclusions:
        if rule.match_type == "username" and user.username == rule.match_value:
            return False
        if rule.match_type == "name_snippet" and rule.match_value in (user.full_name or ""):
            return False
        if rule.match_type == "special_role" and user.special_role == rule.match_value:
            return False
    return True
```

---

## 6. Department Table

Replace `academic_groups.py` hardcoded `GOV/PA/IR/STB` codes with a database table:

```python
class Department(Base):
    __tablename__ = "departments"
    id           = Column(Integer, primary_key=True)
    faculty_id   = Column(Integer, ForeignKey("faculties.id"), nullable=False)
    code         = Column(String(10), nullable=False)  # "GOV", "PA", "IR", "STB"
    name_th      = Column(String(200))
    name_en      = Column(String(200))
    course_prefix_range = Column(String(100))  # e.g., "126100-126199" for GOV
    is_active    = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("faculty_id", "code"),
    )
```

The `academic_groups.py` module continues to exist but reads from the `Department` table
instead of hardcoded dicts. The `@property academic_group` on `Course` and `Section` models
delegates to this service.

---

## 7. Migration Path

### Step 1 — Add Nullable Columns (zero-risk)
```sql
ALTER TABLE faculties ... CREATE (new table);
ALTER TABLE users ADD COLUMN faculty_id INTEGER REFERENCES faculties(id);
ALTER TABLE exam_periods ADD COLUMN faculty_id INTEGER REFERENCES faculties(id);
ALTER TABLE rooms ADD COLUMN faculty_id INTEGER REFERENCES faculties(id);
ALTER TABLE sections ADD COLUMN faculty_id INTEGER REFERENCES faculties(id);
```
All `faculty_id` columns are nullable. Existing data continues to work unchanged.
`MULTI_FACULTY_ENABLED = False` ensures all multi-faculty code paths are inactive.

### Step 2 — Seed Default Faculty
```sql
INSERT INTO faculties (id, code, name_th, name_en) VALUES
(1, 'POLISCI', 'คณะรัฐศาสตร์และรัฐประศาสนศาสตร์', 'Faculty of Political Science and Public Administration');
```

### Step 3 — Backfill Existing Data
```sql
UPDATE users SET faculty_id = 1 WHERE faculty_id IS NULL;
UPDATE exam_periods SET faculty_id = 1 WHERE faculty_id IS NULL;
UPDATE sections SET faculty_id = 1 WHERE faculty_id IS NULL;
-- rooms with faculty_id = NULL remain shared (intentional)
```

### Step 4 — Seed WorkflowSignerConfig and StaffExclusionRule
Run seeder script (see Section 4 and 5 above for INSERT statements).

### Step 5 — Seed Department Table
```sql
INSERT INTO departments (faculty_id, code, name_th, name_en) VALUES
(1, 'GOV', 'ภาควิชาการปกครอง', 'Department of Government'),
(1, 'PA', 'ภาควิชารัฐประศาสนศาสตร์', 'Department of Public Administration'),
(1, 'IR', 'ภาควิชาความสัมพันธ์ระหว่างประเทศ', 'Department of International Relations'),
(1, 'STB', 'ภาควิชาสังคมวิทยาและมานุษยวิทยา', 'Department of Sociology and Anthropology');
```

### Step 6 — Enable Multi-Faculty (when second faculty onboards)
Set `MULTI_FACULTY_ENABLED = True` in `config/settings.py`.
At this point, `faculty_id` scope checks activate on all role-filtered queries.

---

## 8. Feature Flag

`MULTI_FACULTY_ENABLED` in `backend/config/settings.py` (Phase 2 deliverable):

```python
# config/settings.py
class Settings(BaseSettings):
    ...
    MULTI_FACULTY_ENABLED: bool = False
```

When `False`:
- All faculty_id filtering is skipped (system behaves exactly as today)
- Single active ExamPeriod assumption holds
- WorkflowSignerConfig falls back to `SIGN_ORDER_USERNAMES` from auth_utils (Phase 2 interim)

When `True`:
- `get_faculty_filter()` is applied to all user-scoped queries
- `WorkflowSignerConfig` table is the authoritative source for signing order
- Multiple active ExamPeriods (one per faculty) are supported
- Navigation shows faculty label

**This flag stays `False` until the `WorkflowSignerConfig` table is seeded and verified,
and at least one other faculty is ready for pilot testing.**
