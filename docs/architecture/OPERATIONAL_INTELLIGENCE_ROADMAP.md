# Operational Intelligence Roadmap
## EMS — Metrics, Alerting, and Dashboard Evolution

> **Audience:** Admin/esq_head users needing operational visibility; engineers building analytics features
> **Scope:** Current observability gaps, metrics taxonomy, proposed dashboard APIs, alert conditions, historical trends, Phase 5 roadmap
> **Do NOT duplicate** feature descriptions from `docs/FEATURES.md` or UI component design from `docs/UI_SYSTEM.md`
> **Reference files:** `backend/models.py` (AuditLog), `backend/logging_config.py`, `backend/routers/dashboard.py`, `backend/routers/historical_schedules.py`

---

## 1. Current Observability State

### What exists today:

**Structured Application Logging** (`backend/logging_config.py`)
- JSON log format (configurable via `JSON_LOGS` env var)
- Correlation IDs via `_request_id_var` ContextVar
- `_user_id_var` ContextVar (currently unused — not set during requests)
- Log fields: `method`, `path`, `status_code`, `duration_ms`, `request_id`
- Log levels: INFO for 2xx, WARNING for 4xx+

**AuditLog Table** (`models.AuditLog`)
- 5 indexes for efficient querying
- `duration_ms` field on every audit event (query performance tracking)
- `timestamp` field for time-series analysis
- Coverage: partial (see `AUDIT_AND_EVENT_MODEL.md` §3 for gaps)

**Health Endpoint** (`GET /health`)
- Returns: `{"status": "ok", "db": "connected", "version": "2.0.0"}`
- Database connectivity check (`SELECT 1`)
- Suitable for Docker/load balancer health checks
- Gap: does not reflect application-level health (e.g., locked period, missing data)

**Historical Schedules** (`backend/routers/historical_schedules.py`)
- Comparison between optimization baseline and final schedule
- Workload history per staff member
- These are the most mature analytics endpoints in the system

### What is missing:

- No aggregated period-health metrics API
- No alert thresholds or conditions
- No per-period summary snapshots (point-in-time health)
- No dashboard showing submission completeness %, room assignment %, workflow stage
- No workload fairness trend over time
- `_user_id_var` in logging is declared but never set (user context missing from logs)

---

## 2. Missing Operational Signals

These are questions the operations team needs to answer today but cannot without manual DB queries:

| Question | Data Available? | What's Missing |
|----------|-----------------|----------------|
| What % of sections have submitted their exam? | Data in DB | No aggregation API |
| How many workflow blockers are unresolved today? | Data in DB | No blocker detection query |
| Which rooms are over-assigned vs under-assigned? | Data in DB | No capacity-vs-assignment check |
| Is the print queue backed up? | Data in DB | No queue depth API |
| Which staff have 0 assignments this exam period? | Data in DB | No fairness gap query |
| Has the workflow signing progressed? | Data in DB | No signing progress API |
| What's the QR pickup completion rate? | Data in DB | No rate calculation |
| Has anything changed since yesterday? | Partial (AuditLog) | No change summary API |

---

## 3. Metrics Taxonomy

Four categories of operational metrics, each mapped to existing tables.

### Category A: Submission Health
| Metric | Calculation | Tables |
|--------|-------------|--------|
| Submission rate | `submitted / total_sections` × 100 | `exam_submissions`, `sections` |
| Approval rate | `approved / submitted` × 100 | `exam_submissions` |
| Pending count | `count(status='submitted')` | `exam_submissions` |
| Overdue submissions | `submitted_at > deadline AND status = 'draft'` | `exam_submissions`, `system_settings` |
| Per-dept completion | Breakdown by `sections.academic_group` | `exam_submissions`, `sections`, `courses` |

### Category B: Scheduling Health
| Metric | Calculation | Tables |
|--------|-------------|--------|
| Room assignment rate | `scheduled_sections / total_sections` × 100 | `exam_schedules`, `sections` |
| Capacity violations | Rooms where `section.num_students > room.capacity` | `exam_schedules`, `rooms`, `sections` |
| Unassigned sections | Sections with no `ExamSchedule` for active period | `sections`, `exam_schedules` |
| Double-booking count | Rooms/staff with overlapping slots | `exam_schedules`, `supervisions` |

### Category C: Workflow Health
| Metric | Calculation | Tables |
|--------|-------------|--------|
| Signing progress | `signers_done / total_signers` × 100 | `optimize_sessions` (JSON signing metadata) |
| Workflow stage | Current `OptimizeSession.status` | `optimize_sessions` |
| Swap window status | `is_swap_open` from session status | `optimize_sessions` |
| Open swap requests | `count(status='pending')` during swap window | `swap_requests` |
| Blocking issues | Count of conditions blocking period close | Computed query |

### Category D: Operational Health
| Metric | Calculation | Tables |
|--------|-------------|--------|
| Print queue depth | `count(status='queued')` | `print_queue_jobs` |
| QR pickup rate | `confirmed_pickups / total_qr_tokens` × 100 | `exam_pickup_qr_tokens`, `exam_pickup_checkins` |
| Check-in completion | `sections_with_checkins / exam_sections_today` | `checkin_events`, `exam_schedules` |
| Staff with 0 assignments | Staff in supervision role but 0 active `Supervision` records | `users`, `supervisions` |
| Avg invigilators per room | `count(supervisions) / count(exam_schedules)` | `supervisions`, `exam_schedules` |

---

## 4. Proposed Dashboard API

### `GET /api/dashboard/period-health`

Returns a snapshot of the current period's operational state. Role-filtered.

```json
{
  "period": {
    "id": 3,
    "academic_year": "2568",
    "semester": "2",
    "exam_type": "midterm",
    "lifecycle_status": "active"
  },
  "submission": {
    "total_sections": 84,
    "submitted": 61,
    "approved": 48,
    "pending_approval": 13,
    "not_submitted": 23,
    "rate_pct": 72.6
  },
  "scheduling": {
    "total_sections": 84,
    "assigned_to_room": 79,
    "unassigned": 5,
    "capacity_violations": 2,
    "rate_pct": 94.0
  },
  "workflow": {
    "session_status": "swap_open",
    "signing_round": 1,
    "signers_complete": 2,
    "signers_total": 4,
    "open_swap_requests": 7
  },
  "print_queue": {
    "queued": 12,
    "printing": 3,
    "printed": 35
  },
  "blockers": [
    {"type": "unassigned_sections", "count": 5, "severity": "high"},
    {"type": "capacity_violations", "count": 2, "severity": "medium"}
  ],
  "last_updated": "2026-05-11T10:30:00Z"
}
```

**Roles:** Admin sees all fields. ESQ/Secretary see submission + workflow + blockers. Staff see
scheduling + check-in. Teacher sees only submission status for their own sections.

---

### `GET /api/dashboard/audit-timeline`

Returns the last N significant action events for the active period.

```json
{
  "events": [
    {
      "timestamp": "2026-05-11T09:45:00Z",
      "actor_name": "อธิกันต์ ส.",
      "action": "SIGN_WORKFLOW",
      "description": "ลงนาม Round 1 (2/4)",
      "severity": "info"
    },
    {
      "timestamp": "2026-05-11T08:20:00Z",
      "actor_name": "สมชาย ก.",
      "action": "APPROVE_SUBMISSION",
      "description": "อนุมัติ 126101 ตอน 1",
      "severity": "success"
    }
  ],
  "total_today": 47,
  "next_cursor": "2026-05-11T08:20:00Z"
}
```

---

### `GET /api/dashboard/summary` (existing, to extend)

Extend with blockers count and workflow stage from `/period-health` — currently this endpoint
returns only recent activity and submission stats.

---

## 5. Alert Conditions

Conditions that should trigger a visible warning or notification to the relevant role.

| Condition | Severity | Audience | Trigger Logic |
|-----------|----------|----------|---------------|
| 5+ workflow blockers 48h before earliest exam date | HIGH | esq_head + admin | Query earliest `ExamSchedule.exam_date`; count blocking conditions |
| Print queue has 10+ queued jobs 24h before exam | HIGH | admin + print_shop | `count(status='queued')` vs next exam day |
| >15% sections without room assignment | MEDIUM | admin | Scheduling health rate < 85% |
| 3+ sections with capacity violations | MEDIUM | admin | Room capacity < section.num_students |
| 20+ overdue submissions (past deadline, not submitted) | MEDIUM | admin + dept_supervisor | `submitted_at IS NULL AND deadline_passed` |
| Workflow signing stalled >48h (no new signature) | LOW | esq_head | Last `SIGN_WORKFLOW` event > 48h ago, session still in signing |
| Staff member with 0 invigilator assignments | LOW | admin | Staff user with no Supervision records in active period |

**Implementation note:** These are backend-computed checks, not database triggers.
The `/period-health` endpoint computes them on each request. The frontend renders them as
`blockers[]` with `severity` in the response.

---

## 6. Historical Trend Queries

Using existing `historical_schedule_batches` and `AuditLog` tables for longitudinal analysis.

### Workload Fairness Over Time

```sql
-- Average invigilator assignments per staff member, per exam period batch
SELECT
    batch.batch_name,
    batch.academic_year,
    batch.semester,
    AVG(staff_count.invigilation_count) AS avg_assignments,
    MAX(staff_count.invigilation_count) AS max_assignments,
    MIN(staff_count.invigilation_count) AS min_assignments,
    MAX(staff_count.invigilation_count) - MIN(staff_count.invigilation_count) AS fairness_gap
FROM historical_schedule_batches batch
JOIN (
    SELECT hsi.batch_id, hsi.user_id, COUNT(*) AS invigilation_count
    FROM historical_schedule_invigilators hsi
    GROUP BY hsi.batch_id, hsi.user_id
) staff_count ON staff_count.batch_id = batch.id
GROUP BY batch.id, batch.batch_name, batch.academic_year, batch.semester
ORDER BY batch.academic_year DESC, batch.semester DESC;
```

### Submission Compliance Rate Trend

```sql
-- % of sections that submitted on time, by period (using AuditLog)
SELECT
    ep.academic_year,
    ep.semester,
    ep.exam_type,
    COUNT(DISTINCT es.section_id) AS total_sections,
    COUNT(DISTINCT CASE WHEN es.status != 'draft' THEN es.section_id END) AS submitted,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN es.status != 'draft' THEN es.section_id END) /
        NULLIF(COUNT(DISTINCT es.section_id), 0), 1
    ) AS compliance_pct
FROM exam_periods ep
JOIN exam_schedules esc ON esc.period_id = ep.id
JOIN sections s ON s.id = esc.section_id
LEFT JOIN exam_submissions es ON es.section_id = s.id
    AND es.exam_type = ep.exam_type
GROUP BY ep.id, ep.academic_year, ep.semester, ep.exam_type
ORDER BY ep.academic_year DESC;
```

---

## 7. Phase 5 Implementation Roadmap

### Milestone 1 — Dashboard API (2 weeks)
**Goal:** Implement `/api/dashboard/period-health` and extend existing dashboard

Tasks:
- Create `backend/services/health_service.py` with all metric calculations
- Implement `GET /api/dashboard/period-health` endpoint (role-filtered response)
- Implement `GET /api/dashboard/audit-timeline` endpoint
- Frontend: update `Dashboard.tsx` to consume period health; display blockers list
- Add `_user_id_var.set(user.id)` in `RequestLoggingMiddleware` (fixes missing user context in logs)

Success: `/period-health` returns correct data in <500ms; Dashboard shows blockers

---

### Milestone 2 — Period Health Snapshot (1 week)
**Goal:** Snapshot the health state when a period locks (institutional record)

Tasks:
- Add `PeriodHealthSnapshot` model to `models.py`:
  ```python
  class PeriodHealthSnapshot(Base):
      period_id       = Column(Integer, ForeignKey("exam_periods.id"))
      snapshot_data   = Column(JSON)  # full /period-health response at lock time
      snapshotted_at  = Column(DateTime(timezone=True))
      snapshotted_by  = Column(Integer, ForeignKey("users.id"))
  ```
- Call `health_service.take_snapshot(db, period, actor)` in `period.py` when `POST /api/period/{id}/close` succeeds
- Expose snapshot via `GET /api/period/{id}/health-snapshot`

Success: Every locked period has a `PeriodHealthSnapshot` record

---

### Milestone 3 — Alert Conditions and `useAsyncData` Caching (1 week)
**Goal:** Surface alert conditions in dashboard; reduce redundant API calls in frontend

Tasks:
- Backend: alert conditions computed in `health_service.get_blockers(db, period)` and included in `/period-health.blockers[]`
- Frontend: `useAsyncData` gets optional `cacheKey` + `ttlSeconds` parameter for deduplication
- Frontend: Dashboard renders `blockers[]` as color-coded severity cards
- Email digest: add daily period-health summary to `email_notifications.py` digest

Success: Admins see colored blocker cards on Dashboard; 3 alert conditions detectable via API
