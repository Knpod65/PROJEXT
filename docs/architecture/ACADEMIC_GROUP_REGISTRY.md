# Academic Group Registry

**Phase:** D3.5
**Model:** `backend/config_models/academic_group_config.py`
**Service:** `backend/services/academic_group_registry_service.py`

---

## Overview

The academic group registry provides a configurable overlay on `academic_groups.py`.
It does **not** modify `academic_groups.py` — every lookup falls back to the
existing `PREFIX_TO_GROUP`, `GROUP_TO_LABEL`, and `LEGACY_GROUP_ALIASES` constants
when no registry entry is found.

---

## Overlay Semantics

```
get_group_for_prefix(prefix, faculty_id=F)

1. Registered groups for faculty_id=F → match by course_prefixes
2. Registered groups for all faculties (faculty_id=None) → scan all
3. PREFIX_TO_GROUP from academic_groups.py (fallback)   → synthetic AcademicGroupConfig
4. None
```

All fallback paths return the same `AcademicGroupConfig` type so callers
need no special-case handling.

---

## Default Groups (from academic_groups.py)

| Code | Prefixes | Thai Label |
|------|----------|-----------|
| IA   | 126      | การระหว่างประเทศ |
| GOV  | 127      | รัฐศาสตร์ |
| PA   | 128      | รัฐประศาสนศาสตร์ |
| STB  | 129      | ยุทธศาสตร์การพัฒนา |

---

## API

```python
# Seed from academic_groups.py constants
load_defaults_from_academic_groups(faculty_id)

# Register custom groups
register_academic_groups(faculty_id, [AcademicGroupConfig, ...])

# Lookup (all fall back to academic_groups.py if no registry entry)
get_group_for_code(code, faculty_id=None)       -> AcademicGroupConfig | None
get_group_for_prefix(prefix, faculty_id=None)   -> AcademicGroupConfig | None
get_group_for_course_id(course_id, faculty_id=None) -> AcademicGroupConfig | None
get_group_label(code, faculty_id=None, lang="th")   -> str | None
normalize_group_code(code, faculty_id=None)         -> str | None  # resolves aliases
can_access_group(viewer_code, target_code, faculty_id=None) -> bool

# Manage
list_groups(faculty_id)        # active only
clear_faculty_groups(faculty_id)
clear_all_groups()             # test isolation
```

---

## Legacy Alias Resolution

`normalize_group_code("IR")` → `"IA"` via `LEGACY_GROUP_ALIASES` in `academic_groups.py`.
Registry-registered `legacy_aliases` take priority over the module constant.

---

## Adding a New Faculty's Groups

```python
from config_models.academic_group_config import make_academic_group_config
from services.academic_group_registry_service import register_academic_groups

groups = [
    make_academic_group_config(2, "CS", "วิทยาการคอมพิวเตอร์", "Computer Science", ("204",)),
    make_academic_group_config(2, "EE", "วิศวกรรมไฟฟ้า", "Electrical Engineering", ("205",)),
]
register_academic_groups(faculty_id=2, groups=groups)
```
