# Faculty Policy Registry

**Phase:** D3.2
**File:** `backend/services/policy_registry_service.py`
**Constants:** `backend/policies/faculty_policy_registry.py`

---

## Overview

The policy registry provides a three-tier key/value store for platform
configuration values. It overlays `settings.py` without modifying it.

---

## Resolution Algorithm

```
get_policy_value(key, faculty_id=F, period_id=P)

1. If F + P provided and (F, P)[key] exists → return period override
2. If F provided and F[key] exists          → return faculty override
3. If key in _global                        → return global default
4. If fallback arg provided                 → return fallback
5. Raise KeyError
```

The sentinel `_SENTINEL = object()` distinguishes "no fallback" from `fallback=None`.

---

## Standard Policy Keys

| Constant | String key | Source default |
|---|---|---|
| `POLICY_PAPER_DISTRIBUTION_DIVISION` | `paper_distribution_division` | `settings.paper_distribution_division` |
| `POLICY_PAPER_EXCLUDED_USERNAMES` | `paper_distribution_excluded_usernames` | `settings.paper_distribution_excluded_usernames` |
| `POLICY_PAPER_EXCLUDED_SNIPPETS` | `paper_distribution_excluded_snippets` | `settings.paper_distribution_excluded_name_snippets` |
| `POLICY_SIGN_ORDER_USERNAMES` | `sign_order_usernames` | `settings.sign_order_usernames` |
| `POLICY_APPROVAL_QUORUM` | `approval_quorum` | derived from signer count |
| `POLICY_MAX_SUPERVISION_SESSIONS` | `max_supervision_sessions` | 0 (unlimited) |
| `POLICY_ROOM_DEFAULT_CAPACITY` | `room_default_capacity` | — |
| `POLICY_ACADEMIC_YEAR_DEFAULT` | `academic_year_default` | `settings.academic_year` |
| `POLICY_SEMESTER_DEFAULT` | `semester_default` | `settings.semester` |
| `POLICY_FACULTY_NAME_TH` | `faculty_name_th` | `settings` / FacultyConfig.name_th |
| `POLICY_FACULTY_NAME_EN` | `faculty_name_en` | `settings` / FacultyConfig.name_en |
| `POLICY_EMAIL_DOMAIN` | `email_domain` | `settings` / FacultyConfig.email_domain |

---

## API

```python
# Write
set_global_policy(key, value)
set_faculty_policy(faculty_id, key, value)
set_period_policy(faculty_id, period_id, key, value)

# Read (raises KeyError if no match and no fallback)
get_policy_value(key, *, faculty_id=None, period_id=None, fallback=_SENTINEL)

# Convenience re-export
from policies.faculty_policy_registry import get_policy, POLICY_*

# Inspect
list_policy_keys(*, faculty_id=None, period_id=None)   # sorted list
has_faculty_override(faculty_id, key)
has_period_override(faculty_id, period_id, key)

# Clear
clear_faculty_policies(faculty_id)
clear_period_policies(faculty_id, period_id)
clear_all_policies()   # test isolation
```

---

## Example Override

```python
from policies.faculty_policy_registry import POLICY_SIGN_ORDER_USERNAMES
from services.policy_registry_service import set_faculty_policy

# Faculty 2 uses a different signing chain
set_faculty_policy(2, POLICY_SIGN_ORDER_USERNAMES, ["dean.eng", "vice.dean.eng"])
```
