# Admin Dashboard Visual Redesign Source Review

**Date**: 2026-06-15  
**Route**: `/admin-intelligence-dashboard`  
**API**: `GET /api/dashboard/admin-intelligence`  
**Scope**: frontend presentation only

## Authoritative Sources

- `frontend/src/hooks/domain/useAdminIntelligenceDashboard.ts` remains the dashboard query entry point.
- `frontend/src/types/dashboardMetrics.ts` remains the response contract.
- `backend/services/admin_dashboard_intelligence_service.py` remains the source of metric groups, values, source severity, PDPA level, and recommended-action metadata.
- `backend/services/dashboard_metric_service.py` remains the shared backend severity classifier.
- Active-period shell context is read from the existing period store; API query selection is unchanged.

No backend contract, calculation, route, permission, readiness score, workload route, payment workflow, review gate, settings logic, or export behavior was changed.

## Frontend Display Policy

`frontend/src/utils/presenters/adminDashboardPresenter.ts` is a dedicated admin-dashboard presenter. It converts existing response fields into display-only states:

- `healthy`
- `informational`
- `warning`
- `critical`
- `notMeasured`
- `unavailable`

The presenter preserves raw metric values and groups while localizing values, units, states, actions, and restricted-data labels. It does not write data or change shared role-dashboard presentation.

Higher-is-better display handling is explicit for:

- `api_uptime_pct`
- `optimization_quality_avg`
- `submission_rate`
- `room_utilization_score`

Higher-is-worse display handling is explicit for:

- `unscheduled_sections`
- `blocker_count`
- `pdpa_alert_count_24h`
- `staff_imbalance_score`
- `storage_usage_pct`

`print_queue_size` and `qr_redeems_24h` are known placeholders in the backend service. Their zero values are displayed as `not measured`, not healthy zero. `db_ok` is displayed as localized connected/disconnected text; a healthy connected database has no recovery action.

## Recorded Backend Contradiction

`DashboardMetricService.classify_metric_severity` classifies larger values as progressively worse by comparing `value >= critical`, then `warning`, then `info`. The admin intelligence service also calls that classifier for higher-is-better metrics using thresholds such as quality `80/60/40/20`, room utilization, submission rate, and API uptime.

As a result, live `100%` API uptime can arrive with source severity `critical`. This pass intentionally does not change that shared backend logic. The dedicated presenter applies a dashboard-only display-state correction while preserving the API response and backend scoring.

## Invariants

- Public API and response fields are unchanged.
- Overall readiness value is displayed exactly as received.
- Priority actions contain at most five actionable degraded metrics.
- Actions appear only for warning, critical, or unavailable display states.
- No by-date, by-slot, or personnel-distribution data is invented.
- `internal`, `public`, raw status tokens, and raw boolean units are not rendered.
- Restricted-data badges appear only for `restricted` or `confidential` metrics.
- Shared authorization helpers remain in use.

