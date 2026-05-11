# Faculty Scoping Map
## Phase 1 Concrete Artifact

Source of truth:
- docs/architecture/MULTI_FACULTY_ARCHITECTURE.md
- docs/architecture/DOMAIN_BOUNDARY_MAP.md

This map identifies where single-faculty assumptions exist and how each area must be scoped.

## Current vs Target Scoping

| Surface | Current Scope | Target Scope | Gap Type | Planned Vehicle |
|---|---|---|---|---|
| Users | Global user table with dept_code assumptions | faculty_id-scoped user context | Data model + auth | users.faculty_id + permission filters |
| Exam periods | Single active period globally | Active period per faculty | Lifecycle model | exam_periods.faculty_id |
| Sections | Implicit single-faculty by data context | Section rows scoped to faculty | Data model | sections.faculty_id |
| Rooms | System-wide room pool | faculty-specific or shared nullable model | Data model | rooms.faculty_id (NULL shared) |
| Staff unavailability | Not explicitly faculty-aware | faculty-scoped unavailability | Data model | staff_unavailability.faculty_id |
| Signer order | Hardcoded usernames in auth_utils | Configured per faculty and round | Config hardcoding | workflow_signer_configs table |
| Distribution exclusions | Hardcoded usernames/snippets | Faculty-owned exclusion rules | Config hardcoding | staff_exclusion_rules table |
| Department taxonomy | Hardcoded GOV/PA/IR/STB codes | Faculty-owned department records | Static mapping | departments table |
| Role scope enforcement | Mostly global role checks | Role + faculty scope checks | Authorization | get_faculty_filter and scoped queries |

## Role Scoping Targets

| Role | Current Behavior | Target Multi-Faculty Behavior |
|---|---|---|
| admin | Global | Global (unchanged) |
| esq_head | Global-ish governance role | Restricted to own faculty unless explicit global grant |
| secretary | Global-ish governance role | Restricted to own faculty unless explicit global grant |
| dept_supervisor | dept_code-only logic | dept_code + faculty_id logic |
| teacher | Section ownership checks | Ownership + faculty scope checks |
| staff | Assignment checks | Assignment + faculty scope checks |
| print_shop | Operational global role | Global (or configurable by faculty policy) |

## Transition Safeguards

1. Keep MULTI_FACULTY_ENABLED default false until seed and backfill are verified.
2. Introduce nullable faculty_id columns first, then progressively enforce constraints.
3. Treat faculty-scope misses as security defects once feature flag is enabled.
