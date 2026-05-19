# Cross-System Integration Contracts

## Overview

This document defines the logical contracts for five external systems that exchange data with the EMS platform:
1. SIS (Student Information System)
2. HR/Personnel System
3. LMS/Teaching Schedule System
4. Finance / Workload Compensation System
5. CMU Single Sign-On (SSO)

Each contract specifies the data domain, direction, authentication, sync mode, PDPA level,
ownership, required/optional fields, refresh frequency, and failure handling policy.

Contracts are implemented as `TypedDict` objects in `backend/contracts/integration_contracts.py`
and exposed via a read-only registry service (`backend/services/integration_contract_registry_service.py`).

## Contract Details

### 1. SIS (Student Information System) — Inbound

| Field | Value |
|-------|-------|
| **system_code** | `sis` |
| **system_name** | Student Information System |
| **integration_direction** | inbound |
| **data_domain** | student_registration |
| **auth_method** | api_key |
| **sync_mode** | batch_daily |
| **pdpa_level** | confidential |
| **owner_unit** | Registrar |
| **required_fields** | `student_id`, `full_name`, `department` |
| **optional_fields** | `dept_code`, `major`, `academic_year` |
| **refresh_frequency** | `24h` |
| **failure_policy** | retry_3 |

**Notes:**  
- Student roster flows from SIS → EMS on a nightly batch.
- `student_id` is treated as confidential (PII); never exposed in analytics summaries.
- On failure, EMS retries up to 3 times before alerting operators.

### 2. HR/Personnel System — Inbound

| Field | Value |
|-------|-------|
| **system_code** | `hr` |
| **system_name** | Human Resources / Personnel System |
| **integration_direction** | inbound |
| **data_domain** | personnel |
| **auth_method** | api_key |
| **sync_mode** | batch_hourly |
| **pdpa_level** | confidential |
| **owner_unit** | HR |
| **required_fields** | `employee_id`, `full_name`, `department`, `dept_code` |
| **optional_fields** | `position`, `hire_date`, `supervisor_id` |
| **refresh_frequency** | `1h` |
| **failure_policy** | dead_letter |

**Notes:**  
- Personnel data (employment, assignments) flows hourly from HR → EMS.
- Failed writes go to a dead-letter queue for manual inspection.
- Data is confidential; used for workload planning but not exposed in public analytics.

### 3. LMS/Teaching Schedule System — Bidirectional

| Field | Value |
|-------|-------|
| **system_code** | `lms` |
| **system_name** | Learning Management System / Teaching Schedule |
| **integration_direction** | bidirectional |
| **data_domain** | teaching_schedule |
| **auth_method** | oauth2 |
| **sync_mode** | batch_daily |
| **pdpa_level** | internal |
| **owner_unit** | Academic Affairs |
| **required_fields** | `course_id`, `section_id`, `meeting_time`, `room_id` |
| **optional_fields** | `instructor_id`, `title`, `credits` |
| **refresh_frequency** | `24h` |
| **failure_policy** | retry_3 |

**Notes:**  
- Course sections and teaching assignments flow both ways:
  - LMS → EMS: official course catalog and section metadata.
  - EMS → LMS: finalized exam-day room and timing assignments.
- PDPA level is internal; teaching schedules contain no direct PII but are
  operationally sensitive.
- On failure, retry up to 3 times before alerting.

### 4. Finance / Workload Compensation System — Outbound

| Field | Value |
|-------|-------|
| **system_code** | `finance` |
| **system_name** | Finance / Workload Compensation System |
| **integration_direction** | outbound |
| **data_domain** | payment |
| **auth_method** | jwt_bearer |
| **sync_mode** | batch_monthly |
| **pdpa_level** | internal |
| **owner_unit** | Finance Office |
| **required_fields** | `workload_units`, `rate`, `total_cost` |
| **optional_fields** | `payment_date`, `invoice_number` |
| **refresh_frequency** | `30d` |
| **failure_policy** | alert_only |

**Notes:**  
- Monthly workload compensation summary (hours × rate) is pushed from EMS → Finance.
- Only summary aggregates are transmitted; no individual staff PII.
- On failure, EMS logs an alert but does not block — finance can poll later.
- Internal PDPA level because compensation details are operationally sensitive.

### 5. CMU Single Sign-On (SSO) — Inbound (Already Wired)

| Field | Value |
|-------|-------|
| **system_code** | `cmu_sso` |
| **system_name** | CMU Single Sign-On |
| **integration_direction** | inbound |
| **data_domain** | auth |
| **auth_method** | jwt_bearer |
| **sync_mode** | realtime |
| **pdpa_level** | public |
| **owner_unit** | IT Services |
| **required_fields** | `netid`, `roles`, `groups` |
| **optional_fields** | `employee_id`, `student_id` |
| **refresh_frequency** | `0s` (realtime) |
| **failure_policy** | skip |

**Notes:**  
- This contract describes the existing CMU SSO integration in `backend/auth/cmu_sso.py`.
- EMS consumes roles/groups from SSO to enforce RBAC; `employee_id`/`student_id` are optional
  hints for provenance but not used for access decisions.
- PDPA level is public because roles/groups are not considered sensitive.
- Failure policy is `skip`: if SSO is unreachable, EMS falls back to local auth (dev only)
  or denies access (prod).

## Contract Lifecycle

All contracts follow this lifecycle:
1. **Schema → Registry**: Contract defined as TypedDict and registered in `INTEGRATION_CONTRACTS`.
2. **Registry → Adapter Stub**: A placeholder adapter logs inbound/outbound payloads.
3. **Adapter Stub → Real Adapter**: Real adapter implements actual protocol (HTTP, SFTP, etc.).
4. **Real Adapter → Deprecation**: Contract is versioned when upstream system changes.

## PDPA Boundary Summary

| System | PDPA Level | Data Contained | Exposure Risk |
|--------|------------|----------------|---------------|
| SIS    | confidential | student_id, name, dept | High — must be encrypted in transit/at rest |
| HR     | confidential | employee_id, name, dept | High — same as SIS |
| LMS    | internal     | course, section, time, room | Medium — operational sensitivity |
| Finance| internal     | workload_units, rate, total_cost | Low — aggregates only |
| CMU SSO| public       | netid, roles, groups | None — already public-facing |

## Future: Contract Versioning

To support evolution, contracts may be versioned:
- `IntegrationContractV2` with additional fields (e.g. `encryption_key_id`).
- Registry service gains `list_contracts(version="V2")`.
- Adapters declare which version they speak.

No versioning is implemented in D4; contracts are v1 by default.
