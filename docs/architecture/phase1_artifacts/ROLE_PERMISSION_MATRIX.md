# Role Permission Matrix
## Phase 1 Concrete Artifact

Source of truth:
- docs/architecture/POLICY_AND_PDPA_ENFORCEMENT.md
- docs/architecture/EMS_ARCHITECTURE_MAP.md

Legend:
- R = Read
- W = Write/Mutate
- Limited = constrained by ownership/department/workflow state

| Resource Group | admin | esq_head | secretary | dept_supervisor | staff | teacher | print_shop | Current Enforcement |
|---|---|---|---|---|---|---|---|---|
| Users (all records) | R/W | R | R | - | - | - | - | Route dependency |
| User self profile | R | R | R | R | R | R | R | Token identity claims |
| Sections/Courses | R/W | R | R | R (dept) | R | R (owned) | - | Dept filter + route dependencies |
| Exam submissions list/detail | R/W | R | R | R (dept) | - | R (owned) | - | Object-level helper + route dependencies |
| Submission approval | W | - | - | - | - | - | - | Admin-only dependency |
| Schedules (view) | R | R | R | R | R | R | - | Route + filtering |
| Schedules (create/update/delete) | W | - | - | - | - | - | - | Admin-only dependency |
| Workflow signing | W | W (sign role) | W (sign role) | - | - | - | - | Workflow state + role checks |
| Swap requests | R/W | R | R | R | R/W (limited) | R/W (limited) | - | Partial object-level enforcement |
| Check-ins and pickup | R/W | R | R | R | R/W | R (limited) | - | Partial object-level enforcement |
| Print queue jobs | R/W | R | R | - | - | - | R/W | Role dependency + endpoint constraints |
| Exports | R/W | R (selected exports) | R (selected exports) | - | R/W (ops exports) | - | - | Endpoint-specific role checks |
| PDF token download | R/W | - | - | - | - | - | R/W | Tokenized route with role checks |
| Audit logs | R/W | - | - | - | - | - | - | Admin-only route surface |

## Known Permission Gaps

1. Check-in and swap object-level access is partial and needs dedicated assertions.
2. Copy-count masking is primarily UI-level and needs backend enforcement.
3. Dual permission sources (auth_utils and permissions) remain a drift risk until consolidation.
