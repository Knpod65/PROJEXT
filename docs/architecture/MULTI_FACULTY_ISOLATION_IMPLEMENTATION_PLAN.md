# Multi-Faculty Isolation Implementation Plan

**Status:** Phase 3 skeleton implemented  
**Date:** 2026-05-14  
**Files:** `backend/policies/faculty_scope_policy.py`, `backend/services/faculty_scope_service.py`

---

## Current State (Single Faculty)

EMS currently operates with a single implicit faculty (CMU Political Science).
All data is globally shared within an exam period. The following assumptions
are hardcoded in the current codebase:

1. **Staff division** — hardcoded exclusion lists in `staff_workloads.py`
2. **Signer order** — 4-signature approval order in `workflow_signing_service.py`
3. **Department codes** — GOV / PA / IR / STB in `auth_utils.py`
4. **Single active period** — one global active period at a time
5. **Room pool** — all rooms visible to all users
6. **Audit log** — global (no faculty filter)

---

## Isolation Model (Target State)

When `multi_faculty_enabled = True`:

| Boundary | Scope |
|---|---|
| `Schedule` | faculty_id scoped — no cross-faculty schedule visibility |
| `Export` | faculty_id scoped — exports include only own faculty data |
| `Import` | faculty_id scoped — imports cannot overwrite other faculty data |
| `Audit log` | faculty_id filterable (not exclusive — admin sees all) |
| `Room pool` | faculty_id or building assignment |
| `Staff pool` | faculty_id or division mapping |
| `Period` | faculty_id scoped — each faculty has its own active period |

---

## Migration Sequence (4 Steps)

### Step 1 — DB Migration
Add `faculty_id` column to:
- `User` (FK to a new `Faculty` table)
- `Period`
- `Room`
- `ExamSchedule`

Create `Faculty` table:
```sql
CREATE TABLE faculty (
    id INTEGER PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
ALTER TABLE users ADD COLUMN faculty_id INTEGER REFERENCES faculty(id);
ALTER TABLE periods ADD COLUMN faculty_id INTEGER REFERENCES faculty(id);
ALTER TABLE rooms ADD COLUMN faculty_id INTEGER REFERENCES faculty(id);
ALTER TABLE exam_schedules ADD COLUMN faculty_id INTEGER REFERENCES faculty(id);
```

**Requires IT DBA approval** before execution.

### Step 2 — Backfill
Populate `faculty_id` for all existing records using a one-time migration script.
All existing data belongs to faculty_id = 1 (CMU Political Science).

### Step 3 — Activate Policy
1. Uncomment the filter line in `apply_faculty_scope_to_query()`.
2. Set `OPT_MULTI_FACULTY=true` (or `multi_faculty_enabled=true`) in production settings.
3. Apply `apply_faculty_scope_to_query()` in the 5 key routers:
   - `routers/schedule.py` — schedule listing
   - `routers/optimize_workflow.py` — session + users
   - `routers/imports.py` — import pipeline
   - `routers/exports.py` — export pipeline
   - `routers/dashboard.py` — audit log listing

### Step 4 — Verification
- Verify admin can see all faculties.
- Verify dept_supervisor sees only their faculty's data.
- Verify cross-faculty access returns 403.

---

## Feature Flag Gate

`faculty_scope_policy._multi_faculty_enabled()` reads `settings.multi_faculty_enabled`.

**Default:** `False` — all scope functions are no-ops in current deployment.

```python
# config/settings.py (already present)
multi_faculty_enabled: bool = field(
    default_factory=lambda: os.getenv("OPT_MULTI_FACULTY", "false").lower() == "true"
)
```

---

## Phase 3 Skeleton API

```python
from policies.faculty_scope_policy import (
    is_same_faculty,           # → bool
    assert_faculty_scope_safe, # → None | raises EMSPermissionError
    apply_faculty_scope_to_query,  # → query (unmodified in Phase 3)
    get_faculty_scope_context, # → dict (for audit log)
)

from services.faculty_scope_service import (
    get_active_period_for_faculty, # → Period | None
    get_rooms_for_faculty,         # → list[Room]
    get_staff_for_faculty,         # → list[User]
    get_faculty_audit_boundary,    # → dict
)
```

---

## What Requires Approval Before Step 3

| Approval | Requirement |
|---|---|
| IT/DBA | DB migration (new columns + Faculty table) |
| IT/DBA | Backfill script review + execution |
| Business | Faculty definition — codes, names, department mappings |
| Business | Admin cross-faculty visibility rules |
| DPO/PDPA | Audit log faculty-scoping does not create data blind spots |

---

## Test Coverage

20 tests covering: flag-off pass-through, same/different faculty check,
EMSPermissionError on violation, apply-scope no-op with no faculty_id,
scope context dict, and all edge cases (None faculty_id, None target).
