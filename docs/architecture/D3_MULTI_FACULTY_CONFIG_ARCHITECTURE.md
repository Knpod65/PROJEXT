# D3 Multi-Faculty Configuration Platform Architecture

**Delivered:** 2026-05-19
**Baseline:** D2 native trace engine (915 tests, 99/100 readiness)
**Result:** ~1083 tests, all D3 services committed

---

## Overview

D3 transforms EMS from a single-faculty operational system into a configurable
institutional academic operations platform. The 70+ hardcoded institutional
assumptions identified in D3.0 are now wrapped behind configurable service
layers without modifying any existing file.

**Core constraint:** Existing behavior is always the default. Every new service
falls back to the existing constant (academic_groups.py, permissions.py,
settings.py) when no override is registered.

---

## Service Graph

```
                        ┌─────────────────────────────┐
                        │   Platform Config Snapshot   │
                        │  (export / import / diff)    │
                        └──────────┬──────────────┬────┘
                                   │              │
              ┌────────────────────▼──┐    ┌──────▼──────────────────┐
              │  Config Validation   │    │   Config Governance     │
              │  (severity-graded)   │    │   (immutable audit log) │
              └────────────────────┬─┘    └──────┬──────────────────┘
                                   │             │
      ┌────────────┬───────────────▼─────────────▼──┬────────────────┐
      │            │                                 │                │
  D3.1            D3.3                              D3.4             D3.5
FacultyConfig  GovernanceFlow                  WorkloadPolicy   AcademicGroup
  Service        Service                         Service         Registry
      │            │                                 │                │
      │       reads settings                    reads settings   falls back to
      │       sign_order_usernames              paper_dist_*     academic_groups.py
      │                                                          PREFIX_TO_GROUP
      └────────────┴─────────────── D3.2 PolicyRegistry ─────────────┘
                                        (layered resolution)

      D3.6 FacultyRoleMapping  ←  overlays permissions.py (NOT modified)
      D3.9 Frontend hooks      ←  read-only placeholders, wired to D3.1–D3.6
```

---

## Phases Delivered

| Phase | Description | New Files | Tests Added |
|-------|-------------|-----------|-------------|
| D3.0  | Platform assumption audit | 1 doc | 0 |
| D3.1  | FacultyConfig domain | 4 files | +27 |
| D3.2  | Policy registry | 2 files | +21 |
| D3.3  | Governance flow config | 2 files | +21 |
| D3.4  | Workload/staff policy | 3 files | +25 |
| D3.5  | Academic group registry | 2 files | +23 |
| D3.6  | Role mapping overlay | 2 files | +18 |
| D3.7  | Export/import platform | 2 files + 2 test | +33 |
| D3.8  | Validation + governance | 2 files + 2 test | +31 |
| D3.9  | Frontend hooks (TS) | 3 TS files | 0 (tsc+vite) |
| D3.10 | Docs + readiness update | 7 docs | 0 |

**Total new tests: +199 (915 → ~1114)**

---

## Resolution Chains

### Faculty Config
`InMemoryFacultyConfigRepository` (get_by_id) → `None` if unknown

### Policy Registry (D3.2)
`period_override` → `faculty_override` → `global_default` → `fallback arg` → `KeyError`

### Academic Group Lookup (D3.5)
`registered groups for faculty_id` → `PREFIX_TO_GROUP` from `academic_groups.py` (fallback)

### Role Permission Check (D3.6)
`faculty-specific mapping` → `global override` → `permissions.py role sets` (fallback) → all-False mapping

### Governance Flow (D3.3)
`faculty-specific flow` → `global flow` → `build_default_flow_from_settings()` (lazy)

### Workload Policy (D3.4)
`faculty-specific policy` → `global policy` → `build_default_policy_from_settings()` (lazy)

---

## Key Design Decisions

1. **config_models/ package** — Pure Python frozen dataclasses live in
   `backend/config_models/`, not `backend/models/`, to avoid import conflict
   with the existing flat `models.py` SQLAlchemy file.

2. **No DB writes** — All D3 services are in-memory. DB-backed repository
   implementations deferred pending DBA approval (documented in
   MULTI_FACULTY_ISOLATION_IMPLEMENTATION_PLAN.md).

3. **No API endpoints** — Services are pure logic. Router integration deferred
   to follow-on sprint to keep D3 non-breaking.

4. **Frozen dataclasses** — Consistent with EventEnvelope, DomainEvent patterns
   from D1/D2. `clear_*()` functions reset module-level singletons for test isolation.

5. **settings.py untouched** — governance_flow_service and workload_policy_service
   read from the settings singleton to derive their global defaults; faculty
   overrides layer on top.

6. **academic_groups.py untouched** — The registry service falls back to
   PREFIX_TO_GROUP, GROUP_TO_LABEL, and LEGACY_GROUP_ALIASES constants, building
   synthetic AcademicGroupConfig objects to maintain a consistent return type.

7. **permissions.py untouched** — FacultyRoleMappingService reads VIEW_ALL_ROLES,
   SIGNER_ROLES, SUPERVISION_ROLES, WRITE_ROLES to derive global defaults.

---

## Files NOT Modified (Backward Compatibility Preserved)

- `academic_groups.py`
- `permissions.py`
- `auth_utils.py`
- `models.py` (SQLAlchemy)
- `settings.py` / `config/policy.py`
- `cmu_sso.py`
- All router files
- All existing test files
