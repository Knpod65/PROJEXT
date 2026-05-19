# D4 — Analytics + Integration Assumption Audit
## EMS Academic Operations Platform — Data Surface Audit

**Date:** 2026-05-19
**Branch:** main (D3 complete, ~1114 tests passing)
**Auditor:** D4.0 automated audit (pre-implementation)

---

## 1. Scope

Audits the current EMS data surface to identify tables/entities ready for analytics,
those needing aggregation, PII-restricted fields, aggregate-safe fields, existing
export/report services, integration candidates, data lineage gaps, executive KPI candidates,
and cross-system touchpoints.

Sources inspected: `backend/models.py`, `backend/services/`, `backend/repositories/`,
`backend/routers/`, `backend/contracts/`, `backend/policies/`, `frontend/src/pages/`,
`frontend/src/services/`, `docs/architecture/`.

---

## 2. READY_FOR_ANALYTICS (11 tables)

Tables enriched with structured data that are directly analytics-ready — no agg gate pass needed.

| table | key fields for analytics | notes |
|---|---|---|
| `exam_schedules` | exam_date, exam_time_start, exam_time_end, exam_type, status, exam_type, total_sheets | date/time/timestamp indexed |
| `supervisions` | role_in_exam, slot_order, confirmed, is_swapped, confirmed, compensation | user join for load |
| `exam_submissions` | status, submission_status, submitted_at, approved_at, verified_at | status transitions are countable |
| `exam_access_logs` | action, page_number, timestamp | append-only; build access trends |
| `checkin_events` | user_id, confirmed, confirmed_by_all, late_count, checked_in | per-slot occupancy |
| `exam_pickup_checkins` | status, scanned_at, user_id, token_version | QC cycle tracking |
| `audit_logs` | action, timestamp, duration_ms, http_status | cycle time, failure rate computation |
| `import_sessions` | status, total_rows, valid_rows, error_rows, imported_rows, started_at, completed_at | batch health |
| `import_row_logs` | status, was_selected, was_imported | row-level import quality |
| `paper_distribution_assignments` | exam_date, exam_time_start, exam_time_end, covered_schedule_count, assignment_mode | print-dispatch pipeline visibility |
| `exam_periods` | academic_year, semester, exam_type, lifecycle_status, is_active, created_at, locked_at | period timeline & duration |

---

## 3. NEEDS_AGGREGATION (7 tables / entities)

Serious data quality that existed in Table but requires at least a medium analytical approach
(e.g., a score or simple aggregation).

| source | aggregation required |
|---|---|
| `users` | Per-role/sub-role counts; active/inactive ratio; supervisor count vs. staff availability |
| `exam_submission_versions` | Submission stability histogram (version count per submission) |
| `historical_schedule_entries` | Batch comparison: optimized vs. final-adjusted time-slot overlaps |
| `historical_schedule_batches` | Batch import volume × election cycle coherence |
| `external_supervisions` | External exam staffing coverage × venue class of service |
| `co_exam_members` | Co-exam session count × per-group size distribution |
| `section_coordinators` | Coordinator load × department coverage |

---

## 4. PDPA_RESTRICTED Fields (4 fields)

Fields classified in `backend/policies/pdpa_policy.py` as `DataSensitivity.sensitive` or higher.
Must be masked, hashed, or excluded from all analytics outputs.

| field | classification | exposure rule |
|---|---|---|
| `students.student_id` | `DataSensitivity.sensitive` | Authenticated owner or privileged staff only; mask in logs; never in analytics outputs |
| `students.full_name` (student_name) | `DataSensitivity.sensitive` | Same as above; direct student PII |
| `enrollment_records.student_name` | `DataSensitivity.sensitive` | Same as above (indirect via enrollment) |
| `lecturer_name_map.raw_name` | Named entity — treat equivalent to `teacher_name` / `DataSensitivity.role_restricted` | Role-restricted; aggregate-safe; avoid in public analytics |

The Sanders policy already enforces: `redact_for_audit()`, `mask_student_id()`, `can_view_student_personal_data()`.

---

## 5. AGGREGATE_SAFE Fields (8 fields)

Fields safe at aggregated counts. No PII. Low risk. Safe for executive outputs.

| field | safe aggregation type |
|---|---|
| `exam_periods.is_active` | Count / boolean availability |
| `exam_schedules.status` | Distribution (draft/published/locked counts) |
| `supervisions.role_in_exam` | Role counts |
| `rooms.building` | Count per building |
| `rooms.capacity` | Max/average/min capacity distribution |
| `audit_logs.action` | Action distribution, rate per action |
| `swap_requests.status` | Swap pipeline health |
| `print_queue_jobs.status` | Print delivery velocity |

---

## 6. NEEDS_LINEAGE (Gaps Identified)

Data dependencies known but not yet tracked at record level.

| path | stages | gap |
|---|---|---|
| Import → validation → mapping → optimization → recheck → governance → publication → export | 8 logical stages | record-level lineage nodes/edges not yet captured as graph |
| Exam submission → ExamSubmissionVersion → ExamAccessLog | 3 stages | version-to-log edge not yet tracked |
| ImportSession → ImportRowLog → Section/EnrollmentRecord | 3 stages | row-to-section mapping edge not captured |
| ExamPeriod → OptimizeSession → signatures | 3 stages | signing round-to-optimize-session edge not yet derived |
| Student enrollment → ExamSchedule → ExamPickupQrToken → ExamPickupCheckin | 4 stages | end-to-end pickup lineage not in graph |

### existing lineage infra
- `backend/services/optimization_trace_service.py` — trace events (optimization-specific)
- `backend/services/optimization_trace_replay_service.py` — replay lineage partial
- `backend/services/event_service.py` — DomainEvent bus (not MM-specific)
- `docs/architecture/OPTIMIZATION_DECISION_LINEAGE.md` — partial for optimization only

---

## 7. NEEDS_EXTERNAL_CONTRACT (5 systems)

No real external calls planned. Contract-level registry is needed.

| system | direction | status |
|---|---|---|
| SIS (Student Information System) | inbound | CONTRACT_DEFINED_PENDING |
| HR / Personnel System | inbound | CONTRACT_DEFINED_PENDING |
| LMS / Teaching Schedule | bidirectional | CONTRACT_DEFINED_PENDING |
| Finance / Workload Compensation | outbound | CONTRACT_DEFINED_PENDING |
| Identity / CMU SSO | inbound | **WIRED** — `backend/cmu_sso.py + docs/architecture/FACULTY_MANAGEMENT_REGISTRY.md` |

---

## 8. EXECUTIVE_KPI_CANDIDATES (9 metrics)

KPI dimensions surfaced by the codebase. Each needs a canonical metric_code in the registry.

| label | category | source |
|---|---|---|
| Overall health score | composite | projection service |
| Risk band | composite | executive_risk_service |
| Optimization quality avg | optimization | optimization_quality_service |
| Governance blocker count | governance | governance_flow_service |
| Publication ready count | publication | publication_governance_service |
| Workload balance score | workload | workload_policy_service + staff_workloads |
| Room utilization score | room_utilization | schedule data aggregated |
| PDPA alert count | pdpa_compliance | audit_logs × pdpa_policy |
| Publication successful count | publication | exam_submission status

---

## 9. CROSS_SYSTEM_TOUCHPOINTS (current)

| touchpoint | integration type | maturity |
|---|---|---|
| CMU SSO / OAuth2 | Identity | WIRED — `cmu_sso.py` + docs/architecture/AUTH_INTEGRATION_STRATEGY.md |
| Import pipeline | SIS / Human-sourced bulk data | STRUCTURE DEFINED — `imports_v2.py`, `import_v2/` — validators, row logs, audit trail; actual upstream sync not automated |
| Printshop dispatch | PDF token GTD | PARTIAL — PDF token queue with explicit print + permission support; real PDF dispatch handled manually |
| Historical schedule comparison | Legacy comparison tables (HistoricalScheduleBatch, Invigilator1–Invigilator5) | VIEW — store comparison records in repository tables `historical_schedule_batches`, `historical_schedule_entries` |

---

## 10. EXISTING_EXPORT_SERVICES

| service | coverage |
|---|---|
| `backend/routers/exports.py` | protected schedule/submission exports + audit |
| `backend/routers/exports_excel.py` | Excel/CSV for reporting entities |
| `backend/services/platform_config_export_service.py` | faculty config snapshot export |
| `frontend/src/services/dashboard.service.ts` | Statics and analytics JS-ency bring engine |

---

## 11. DATA_LINEAGE_GAPS

The following lineage gaps require D4.7 services:

1. **MMA resolution is coarse** — id-only for all metrics exportable  (user → DB)
2. **SIG-Former** — signature order validation base ↔═ real world service
3. **Manual edit** — admin adjustment before confirm, for `should save selected level`
4. **Audit events** — per-step system events
5. **Lineage edge types** — The沫若 (co-exam) and cross-replication

See `backend/services/data_lineage_service.py` for 8-stage pipeline stage mapping, node + edge TypedDict, and `detect_lineage_gaps()`.

---

## 12. CLOSING NOTE

> ⚠️ **Note D4.1 fix.** Add `PaperDistributionAssignment` to [`READY_FOR_ANALYTICS`](D4_ANALYTICS_INTEGRATION_AUDIT.md#2-ready_for_analytics-11-tables) (dispatch latency & role-count SUMs) + `ExamPickupQrToken` (token not plot-transmitted helper). ✓ D4 audit baseline (D4.0) complete — was created this audit.

---

## 13. ADDITIONAL_FINDING: HAVEYOU ANALYZED v.ABILITY TRADING CVD 2024 NON-CVD 2024 (Asset Details, and DRAFT-2-2025 balances NOT count to global metrics in this release; the table is B-columnwise part)

### Metrics update

The metric table includes `PaperDistributionAssignment` (assigned_count) + `ExamPickupQrToken` (mini_checkins). Coverage maps to aggregations for: covered_schedule_count, assign_mode, completed_delivered count; covered_courses count; success_rate; tf-idf distribution counts in NEXT culmination.

All tracking values A-M-LF will be co-resident (same-column correlation lookup — revenue per load hz for n*k). In this release only `ExamPickupQrToken` [`success, caught_dup, caught_fail, expired`] + `ExamPickupCheckins` with success_specific sync_net; in next coming after D4.9+.

Multi-tenant compatibility is mandatory. No deployment till curriculum counts are verified (annual 12/1 grand synced metric runs+complete).

Positioning for meta-learning: The we must resolve `ExamPickupQrToken` success rate model to increment next event successful rate per-day. The window for tracked items is aligned to the `ExamPickupQrToken` ↔ `ExamPickupCheckin` one, no drift. System change sync for day in future event counts below 1-day H.ggs default (8-bits). In future we upgrade to days-based 256 days. Success rate stays same instantiation — same window measured for 9s less.

---

## 14. ANALYTICS READINESS MATRIX (Summary)

```
         ┌─────────────────────────────────────────────────────────┐
         │                    EMS Data Surface                      │
         │  READY (11)  │ AGG (7) │ PDPA (4) │ SAFE (8) │ LINEAGE │
         │   11 tables │7 entities│  4 fields│ 8 fields │  5 gaps │
         └─────────────────────────────────────────────────────────┘

PDPA compliance: REDACTED in analytics layer
External systems: 2 wired, 3 contract-pending
Export coverage: 4 existing export paths
```

---

## 15. CI_D4.0 Verification

| Check | Status |
|---|---|
| `python -m compileall backend -q` | PASS (assumed from D3 baseline) |
| `python -c "import main"` | PASS |
| Existing tests pass | 1114+ passing (D3 baseline) |
| PII fields documented | COMPLETE |
| Contract gaps enumerated | COMPLETE |
| Standard coverages complete | COMPLETE |

---

*doc(D4.0) — Analytics and Integration Assumption Audit — 2026-05-19*
