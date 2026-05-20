# System Cognitive Map

## Summary

EMS is organized as a layered operating system for academic administration.

To make it understandable, the platform should be read in five layers:

1. Human role layer
2. Workflow layer
3. Governance layer
4. Intelligence layer
5. Federation and futures layer

The documentation should always translate from the top down: role first, then workflow, then governance, then analytics, then the deeper reasoning systems.

## 1. Frontend Surface Map

### Core Page Families

- Dashboard and oversight: `Dashboard`, `RoleDashboard`, `AdminIntelligenceDashboard`, `ExecutiveAnalytics`, `GovernanceCockpit`, `OperationalHealth`, `AuditExplorer`, `WorkloadDutyAnalytics`, `OptimizationTraceExplorer`, `HistoricalSchedules`, `PlatformConfiguration`
- Operations and workflow: `Schedule`, `Submissions`, `Swaps`, `SwapsV2`, `Checkins`, `RoomAttendance`, `Copy`, `PrintReview`, `PrintQueue`, `External`, `Optimizer`, `StaffAvailability`, `CoExam`, `ExportCenter`
- Exam lifecycle and administration: `Sections`, `MyExam`, `Import`, `ImportV2`, `ImportAudit`, `ExamManager`, `Period`, `Users`, `UsersV2`, `Settings`, `SettingsV2`, `RoomManagementV2`, `VenueManagementV2`, `StudentsV2`
- Entry and public surfaces: `RoleSelection`, `Login`, `StudentSearch`

### Navigation Shape

The current nav groups are:

- dashboard
- operations
- examManagement
- people
- system

This means users are already being asked to move through EMS as a role-based operating environment, not as a flat app menu.

## 2. Backend Service Map

### Core Service Families

- Identity and access control: auth integration, permissions, PDPA guardrails, faculty scope, faculty config
- Governance and audit: config governance, governance flow, governance reasoning, governance trace, governance analytics, publication governance, audit, immutable audit, transaction audit, event outbox, data lineage
- Optimization and scheduling: schedule service, transition service, lifecycle events, optimizer service, optimization governance, optimization simulation, optimization trace, trace replay, optimization quality, optimization recheck, predictive balancing
- Analytics and dashboards: analytics service, projections, metric registry, dashboard service, dashboard alerts, admin dashboard intelligence, executive dashboard projection, executive risk, room utilization, room pressure forecast, staffing forecast, workload analytics, workload duty analytics, workload forecasting
- Federation and futures: federated intelligence, distributed cognition, institutional coordination, institutional state model, institutional trust, institutional registry, national resilience, educational futures
- Workflow and operational support: submission, workflow signing, workflow lock, workflow reporting, import, export, documents, health, unit of work

## 3. Major Complexity Hotspots

### Governance + Audit + Events

This is the densest part of the platform because it combines policy, traceability, immutable records, publication control, and lifecycle tracking.

### Optimization + Trace + Simulation

This cluster is easy to fragment because it has separate paths for quality, simulation, replay, trace capture, explanation, and recheck.

### Workflow + State Machine

Period lifecycle, submission status, signing, swap windows, print queues, and release rules are coupled. Users need to understand state transitions, not just buttons.

### Multi-Faculty Readiness

Any hardcoded faculty assumption can make the platform feel unpredictable. Documentation should call out where scope is global, where it is faculty-specific, and where hidden assumptions still exist.

### Dashboard Overload

Too many metrics in one view create uncertainty. Each dashboard should answer one primary question and at most a few secondary questions.

## 4. Role Confusion Risks

- Admins may see every surface and still not know which page is operational versus informational.
- Staff may receive too many tools without a clear daily sequence.
- Teachers may not know which work belongs to submission, schedule, workload, or check-in.
- Executives may see high-level indicators without enough guidance on what to do next.
- Governance users may confuse review, approval, audit, and publication gates.

## 5. Documentation Anchors

The most useful starting docs are:

- [docs/architecture/EMS_ARCHITECTURE_MAP.md](../architecture/EMS_ARCHITECTURE_MAP.md)
- [docs/architecture/DOMAIN_BOUNDARY_MAP.md](../architecture/DOMAIN_BOUNDARY_MAP.md)
- [docs/architecture/SERVICE_LAYER_PLAN.md](../architecture/SERVICE_LAYER_PLAN.md)
- [docs/architecture/WORKFLOW_STATE_MACHINE.md](../architecture/WORKFLOW_STATE_MACHINE.md)
- [docs/architecture/PUBLICATION_GOVERNANCE_ARCHITECTURE.md](../architecture/PUBLICATION_GOVERNANCE_ARCHITECTURE.md)
- [docs/architecture/OPERATIONAL_INTELLIGENCE_ROADMAP.md](../architecture/OPERATIONAL_INTELLIGENCE_ROADMAP.md)
- [docs/architecture/WORKLOAD_DUTY_ANALYTICS_QA_CHECKLIST.md](../architecture/WORKLOAD_DUTY_ANALYTICS_QA_CHECKLIST.md)

## 6. Preferred Interpretation Order

When documenting any page or service, use this order:

1. What role is this for?
2. What operational job does it support?
3. What is the one thing the user needs to notice first?
4. What should they do next?
5. What is the escalation path if it looks wrong?
