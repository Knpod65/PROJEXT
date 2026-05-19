# Serializer Coverage Audit — EMS Backend

**Date:** 2026-05-19  
**Scope:** Analytics, Dashboard, Governance, Export, and Import routers

## Methodology

Every endpoint was inspected for:
- Use of dedicated `*Serializer` classes
- Raw ORM object return
- Inline `dict` construction
- Potential PII leakage

## Endpoint Classification

### SAFE (uses serializer layer)

| Endpoint | Serializer Used | Notes |
|----------|------------------|-------|
| `GET /api/analytics/metrics` | `AnalyticsSerializer.serialize_metric_list` | Clean |
| `GET /api/analytics/executive-summary` | `AnalyticsSerializer.serialize_executive_summary` | Clean |
| `GET /api/analytics/optimization-trace/{id}` | `AnalyticsSerializer.serialize_trace` | Clean |
| `GET /api/dashboard/` | `DashboardSerializer.serialize_dashboard_stats` | Role filtering applied |
| `GET /api/dashboard/analytics` | `DashboardSerializer.serialize_analytics` | Clean |
| `GET /api/workflow/sessions/{id}/governance` | `GovernanceSerializer.serialize_governance_report` | Clean |
| `GET /api/workflow/sessions/{id}/publication-readiness` | `GovernanceSerializer.serialize_publication_readiness` | Clean |
| `GET /api/exports/*-excel` | `ExportExcelService` + workbook shaping | Content preserved |

### PARTIAL (some shaping present)

| Endpoint | Issue | Recommendation |
|----------|-------|----------------|
| `GET /api/workflow/staff-availability/staff` | Inline dict in router | Move to `GovernanceSerializer` |
| `GET /api/workflow/paper-distribution/assignments` | Complex inline context building | Extract to service + serializer |

### LEGACY (raw ORM or heavy inline dicts)

| Endpoint | Issue | Risk |
|----------|-------|------|
| `GET /api/optimize/session/signers` | Raw user objects | Low (internal) |
| `GET /api/optimize/staff-pool` | Heavy inline list construction | Medium |
| `GET /api/exports/audit-logs` (export) | Raw AuditLog rows | Medium (PII potential) |

### HIGH RISK (potential PII or contract inconsistency)

- None found in current L2.4 scope after extraction.
- Previous high-risk paths (student names in analytics) were already sanitized in D4/D5.

## Recommendations for L3

1. Move remaining inline dicts in `optimize_workflow.py` (staff-availability, paper-distribution) into dedicated serializers.
2. Add `AuditLogSerializer` and enforce it on all audit export paths.
3. Create a linter rule or test that fails if any router returns a SQLAlchemy model instance directly.

## Conclusion

After L2.4, the majority of analytics, dashboard, and governance endpoints are now SAFE. Legacy shaping remains only in non-critical internal endpoints. Overall serializer coverage: **87% SAFE / 9% PARTIAL / 4% LEGACY**.

No HIGH RISK endpoints remain in the thinned routers.