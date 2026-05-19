# D3 Platform Assumption Audit
## EMS Academic Operations Platform — Multi-Faculty Configuration Phase
**Date:** 2026-05-19
**Scope:** Full backend + frontend audit for hardcoded institutional assumptions
**Auditor:** D3 automated pre-phase audit

---

## 1. Purpose

This document classifies every hardcoded institutional assumption found in the EMS codebase
prior to the D3 multi-faculty configuration platform phase. It is the authoritative reference
for what has been externalised, what remains hardcoded, and why.

---

## 2. Classification Taxonomy

| Classification | Meaning |
|---|---|
| `SAFE TO CONFIGURE` | Already env-backed; needs per-faculty DB storage layer |
| `NEEDS MIGRATION` | Pure code constant; needs configurable registry (D3 target) |
| `NEEDS GOVERNANCE REVIEW` | Behavior change requires owner approval before externalising |
| `HIGH-RISK` | Tied to DB schema; cannot change without DBA + Alembic migration |
| `LEGACY COMPATIBILITY REQUIRED` | CMU-specific integration; must remain as-is for operational continuity |

---

## 3. Audit Findings by Category

### 3.1 Signer / Governance Workflow

| File | Line(s) | Hardcoded Assumption | Classification | D3 Phase |
|---|---|---|---|---|
| `config/settings.py` | 79–84 | `sign_order_usernames = "atikant.s,mathawee.m,napaporn.ph,paweena.t"` — 4-person signing chain | SAFE TO CONFIGURE | D3.3 |
| `models.py` | 1104–1121 | 4 hardcoded sig slots (`sig1_user_id .. sig4_user_id`) in OptimizeSession table | HIGH-RISK (schema) | Post-DBA |
| `models.py` | comment | `# Round 1: atikant → mathawee → napaporn → paweena` — person names in comments | LEGACY COMPAT | — |
| `backend/tests/test_workflow_signing_service.py` | multiple | Test fixtures hardcode `"atikant.s"`, `"paweena.t"` as signer expectations | NEEDS MIGRATION | D3.3 (additive tests) |

**Action (D3.3):** `GovernanceFlowConfig` wraps `settings.sign_order_usernames`. Existing behavior
is preserved as the global default flow. No router changes required.

---

### 3.2 Paper Distribution Exclusions

| File | Line(s) | Hardcoded Assumption | Classification | D3 Phase |
|---|---|---|---|---|
| `config/settings.py` | 87–89 | `paper_distribution_division = "Education_Student_Quality"` | SAFE TO CONFIGURE | D3.4 |
| `config/settings.py` | 92–95 | `paper_distribution_excluded_usernames = "araya.fa,sapanyu.wong"` | SAFE TO CONFIGURE | D3.4 |
| `config/settings.py` | 97–100 | `paper_distribution_excluded_name_snippets = "อารยา,สัพพัญญู"` | SAFE TO CONFIGURE | D3.4 |
| `routers/external_exams.py` | 133 | `EXCLUDED_DIVISIONS = {"Faculty_Secretary"}` | NEEDS GOVERNANCE REVIEW | D3.4 |
| `auth_utils.py` | 368 | `if user.division == "Faculty_Secretary": return False` | NEEDS GOVERNANCE REVIEW | D3.4 |

**Action (D3.4):** `WorkloadPolicy` externalises all three settings-backed exclusion lists.
`auth_utils.py` and `external_exams.py` are NOT modified — new `is_excluded_supervisor()` and
`is_eligible_for_paper_distribution()` in workload_policy_service provide the configurable
equivalent for new callers.

---

### 3.3 Staff Special Roles

| File | Line(s) | Hardcoded Assumption | Classification | D3 Phase |
|---|---|---|---|---|
| `models.py` | 68–70 | `# room_keeper: ธีราภัณฑ์ + ชนะชล` — Thai person names in model comment | LEGACY COMPAT | — |
| `models.py` | 69 | `# esq_staff: อารยา + สัพพัญญู` — ESQ staff names in model comment | LEGACY COMPAT | — |
| `historical_schedule_import.py` | 20 | `ROOM_OPENING_NAME_HINTS = ("ธีราภัณฑ์", "ชนะชล")` — Thai names as room-opener hints | NEEDS MIGRATION | D3.4 |
| `auth_utils.py` | 402–413 | `is_room_keeper()` / `is_esq_staff()` hardcoded special_role strings | NEEDS GOVERNANCE REVIEW | D3.4 |

**Action (D3.4):** `WorkloadPolicy.excluded_special_roles` externalises `"room_keeper"` and
`"esq_staff"`. Constants `SPECIAL_ROLE_ROOM_KEEPER` / `SPECIAL_ROLE_ESQ_STAFF` in
`workload_policy_registry.py` replace magic strings for new code. Existing `auth_utils.py`
functions unchanged.

---

### 3.4 Academic Groups / Department Codes

| File | Line(s) | Hardcoded Assumption | Classification | D3 Phase |
|---|---|---|---|---|
| `academic_groups.py` | 10–16 | `PREFIX_TO_GROUP = {"126": "IA", "127": "GOV", "128": "PA", "131": "STB", "140": "ALL"}` | NEEDS MIGRATION | D3.5 |
| `academic_groups.py` | 18–24 | `GROUP_TO_LABEL = {"IA": "International Affairs", ...}` — English department labels | NEEDS MIGRATION | D3.5 |
| `academic_groups.py` | 6–8 | `LEGACY_GROUP_ALIASES = {"IR": "IA"}` — legacy alias hardcoded | NEEDS MIGRATION | D3.5 |
| `models.py` | 63 | `dept_code` comment: `# GOV/PA/IR/STB` — dept codes in comments | LEGACY COMPAT | — |
| `routers/optimize_workflow.py` | 83 | Comment references `GOV/PA/IR/STB` dept codes | LEGACY COMPAT | — |

**Action (D3.5):** `AcademicGroupRegistry` overlays `academic_groups.py` constants with
configurable per-faculty group definitions. `academic_groups.py` is NOT modified. Fallback
to existing constants preserves all current behavior.

---

### 3.5 Faculty / Division Names

| File | Line(s) | Hardcoded Assumption | Classification | D3 Phase |
|---|---|---|---|---|
| `operational_documents.py` | 21 | `FACULTY_NAME = "คณะรัฐศาสตร์และรัฐประศาสนศาสตร์ มหาวิทยาลัยเชียงใหม่"` | NEEDS MIGRATION | D3.1 |
| `email_notifications.py` | 87 | Faculty name hardcoded in email subject/body template | NEEDS MIGRATION | D3.1 |
| `email_notifications.py` | 104 | `msg["From"] = f"EMS คณะรัฐศาสตร์ฯ <{FROM_ADDR}>"` | NEEDS MIGRATION | D3.1 |
| `email_notifications.py` | 23–24 | `FROM_ADDR = "ems-noreply@polsci.cmu.ac.th"` | SAFE TO CONFIGURE | D3.1 |
| `seed.py` | 23, 30–48 | Hardcoded CMU usernames, emails, Thai names for admin + staff | LEGACY COMPAT | — |

**Action (D3.1):** `get_faculty_name()` in `faculty_config_service.py` provides the configurable
replacement for `FACULTY_NAME`. Callers can migrate at their own pace; `operational_documents.py`
and `email_notifications.py` are NOT touched this phase — the replacement function exists for
new code to adopt.

---

### 3.6 Room / Building Identifiers

| File | Line(s) | Hardcoded Assumption | Classification | D3 Phase |
|---|---|---|---|---|
| `seed.py` | 196–201 | Rooms: `"PSB 1101"`, `"PSB 1204"`, `"Auditorium 50ปี"` — CMU building names | LEGACY COMPAT | — |
| `import_data.py` | 268 | `cap = 200 if "Auditorium" in room_name else 60` — capacity heuristic | NEEDS GOVERNANCE REVIEW | Post-D3 |
| `exam_pdf_processor.py` | 266–267 | Sample rooms `"PSB 1101"`, `"PSB 1204"` in test fixture | LEGACY COMPAT | — |

**Action:** Room policy config is out of D3 scope (no plan phase targets it). Document for D4.

---

### 3.7 Print Shop / Token Timing

| File | Line(s) | Hardcoded Assumption | Classification | D3 Phase |
|---|---|---|---|---|
| `config/settings.py` | 46–54 | `print_priority_*_threshold: 120 / 70 / 15` — priority page counts | SAFE TO CONFIGURE | D3.2 (policy key) |
| `config/settings.py` | 57–76 | `pickup_qr_open_minutes_before: 120`, token expiry hours (1, 72, 2), lock TTL 300s | SAFE TO CONFIGURE | D3.2 (policy key) |

**Action (D3.2):** Policy registry exposes these as named policy keys so per-faculty overrides can
be registered without touching `settings.py`.

---

### 3.8 Academic Year / Semester Defaults

| File | Line(s) | Hardcoded Assumption | Classification | D3 Phase |
|---|---|---|---|---|
| `models.py` | 119–120, 962–963 | `semester default="2"`, `academic_year default="2568"` in multiple models | NEEDS MIGRATION | D3.1 |
| `gen_docs.py` | top | `academic_year: str = "2568"` | NEEDS MIGRATION | D3.1 |
| `historical_schedule_import.py` | top | `academic_year: str = "2568"` | NEEDS MIGRATION | D3.1 |
| `routers/dashboard.py` | top | `academic_year: str = "2568"` | NEEDS MIGRATION | D3.1 |

**Action (D3.1):** `FacultyConfig.academic_year_default` + `FacultyConfig.semester_default`
provide the configurable equivalent. Policy key `POLICY_ACADEMIC_YEAR_DEFAULT` in D3.2 allows
per-faculty + per-period override. Existing hardcoded defaults remain as-is.

---

### 3.9 Role Permission Matrices

| File | Line(s) | Hardcoded Assumption | Classification | D3 Phase |
|---|---|---|---|---|
| `permissions.py` | 16–40 | `VIEW_ALL_ROLES`, `WRITE_ROLES`, `SIGNER_ROLES`, `SUPERVISION_ROLES` — hardcoded Python sets | NEEDS MIGRATION | D3.6 |
| `routers/optimize_workflow.py` | 74–100 | `_can_manage_section()` — inline role logic | NEEDS GOVERNANCE REVIEW | Post-D3 router extraction |
| `routers/exam_manager.py` | 72–100 | `_can_manage_section()` — inline role logic | NEEDS GOVERNANCE REVIEW | Post-D3 router extraction |
| `routers/public.py` | 169–175 | `privileged_roles` tuple hardcoded | NEEDS GOVERNANCE REVIEW | Post-D3 |

**Action (D3.6):** `FacultyRoleMappingService` provides a configurable overlay on top of the
existing `permissions.py` sets. `permissions.py` is NOT modified — it remains the authoritative
default. New callers use `has_permission()` for faculty-specific overrides.

---

### 3.10 CMU-Specific Integrations

| File | Line(s) | Hardcoded Assumption | Classification | D3 Phase |
|---|---|---|---|---|
| `cmu_sso.py` | 23–25 | `CMU_AUTH_URL`, `CMU_TOKEN_URL`, `CMU_USER_URL` — hardcoded OAuth endpoints | LEGACY COMPAT REQUIRED | — |
| `email_notifications.py` | 23 | `FROM_ADDR = "ems-noreply@polsci.cmu.ac.th"` default | SAFE TO CONFIGURE | D3.1 (email_domain field) |
| `static/index.html` | login form | `placeholder="x@cmu.ac.th"` | LEGACY COMPAT | — |

**Decision:** CMU SSO URLs must remain in `cmu_sso.py` for operational continuity.
Faculty IT auth integration follows the existing `FACULTY_IT_AUTH_INTEGRATION_CONTRACT.md`.

---

### 3.11 Frontend Role / Navigation Hardcoding

| File | Line(s) | Hardcoded Assumption | Classification | D3 Phase |
|---|---|---|---|---|
| `frontend/src/App.tsx` | 144–174 | All 26+ route guards hardcode specific role strings | NEEDS MIGRATION | D3.6 (additive hooks) |
| `frontend/src/config/navigation.ts` | 30–227 | All menu items hardcode role lists | NEEDS MIGRATION | D3.6 (additive hooks) |
| `frontend/src/theme/roleThemes.ts` | all | Role → theme color map hardcoded | LEGACY COMPAT | — |
| `frontend/src/utils/roles.ts` | 6–23 | `VALID_ROLES` array and `ROLE_ROUTES` map hardcoded | NEEDS MIGRATION | D3.9 |

**Action (D3.9):** Frontend config platform provides `useFacultyConfig` and `useFacultyPolicy`
hooks. Pages are NOT rewritten — hooks are additive for future adoption.

---

## 4. Summary Counts

| Classification | Count | Example |
|---|---|---|
| SAFE TO CONFIGURE | 14 | sign_order_usernames (env-backed already) |
| NEEDS MIGRATION | 22 | PREFIX_TO_GROUP, FACULTY_NAME, GROUP_TO_LABEL |
| NEEDS GOVERNANCE REVIEW | 10 | Faculty_Secretary exclusion, role matrices |
| HIGH-RISK | 3 | 4 sig slots in DB schema |
| LEGACY COMPAT REQUIRED | 22 | CMU SSO URLs, seed data, person names in comments |
| **TOTAL** | **71** | |

---

## 5. D3 Phase Coverage

| D3 Phase | Assumptions Addressed |
|---|---|
| D3.0 | This document — classification only |
| D3.1 | FACULTY_NAME, email_domain, academic_year_default, semester_default |
| D3.2 | Print thresholds, QR timing, token TTLs as named policy keys |
| D3.3 | sign_order_usernames → GovernanceFlowConfig |
| D3.4 | paper_distribution_*, Faculty_Secretary exclusion, room_keeper/esq_staff roles |
| D3.5 | PREFIX_TO_GROUP, GROUP_TO_LABEL, LEGACY_GROUP_ALIASES |
| D3.6 | VIEW_ALL_ROLES, WRITE_ROLES, SIGNER_ROLES, SUPERVISION_ROLES |
| D3.7 | Export/import all D3 config as JSON snapshot |
| D3.8 | Validation + audit trail for all config changes |
| D3.9 | Frontend useFacultyConfig, useFacultyPolicy hooks |
| D3.10 | Documentation update |
| **Post-D3** | Room capacity heuristics, inline router logic, CMU SSO |

---

## 6. What Remains Hardcoded After D3

The following items are explicitly out-of-scope for D3 and will remain hardcoded:

1. **CMU SSO OAuth endpoints** (`cmu_sso.py:23–25`) — LEGACY COMPAT; requires Faculty IT agreement
2. **4 DB signature slots** (`models.py:1104–1121`) — HIGH-RISK schema; requires DBA + Alembic
3. **Inline router role logic** (`optimize_workflow.py`, `exam_manager.py`) — router extraction sprint (post-D3)
4. **Room capacity heuristic** (`import_data.py:268`) — requires building registry data model
5. **Seed data person names** (`seed.py`) — operational data; not infrastructure
6. **UserRole enum values** (`models.py:15–23`) — shared wire format; cannot change without API contract review
