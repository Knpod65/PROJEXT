# EMS Humanization Documentation Hub

## Purpose

This hub turns EMS from a deeply layered institutional platform into a set of human-readable operating guides.

The goal is not to restate architecture for its own sake. The goal is to help people answer three questions quickly:

1. What am I looking at?
2. What should I do next?
3. When do I escalate?

## What This Hub Contains

- [System Cognitive Map](system-cognitive-map.md)
- [Humanization Strategy](humanization-strategy.md)
- Role manuals for major user groups
- Dashboard interpretation guides
- Screenshot atlases and visual journeys
- Operational playbooks and troubleshooting guides

## Design Rules

- Explain workflow before architecture.
- Explain impact before metrics.
- Explain role boundaries before permissions.
- Explain alerts before technical traces.
- Explain escalation before remediation detail.

## Starting Scope

The first documentation slice focuses on the highest-traffic surfaces:

- Dashboard and oversight pages
- Operations and workflow pages
- Governance and audit pages
- Analytics and workload pages
- Optimization and readiness pages

The screenshot atlas starts with those pages only. Broader coverage can follow after the core guides are stable.

## Source Anchors

- [frontend/src/App.tsx](../../frontend/src/App.tsx)
- [frontend/src/config/navigation.ts](../../frontend/src/config/navigation.ts)
- [frontend/src/pages/](../../frontend/src/pages)
- [backend/services/](../../backend/services)
- [docs/architecture/EMS_ARCHITECTURE_MAP.md](../architecture/EMS_ARCHITECTURE_MAP.md)
- [docs/architecture/DOMAIN_BOUNDARY_MAP.md](../architecture/DOMAIN_BOUNDARY_MAP.md)
- [docs/architecture/SERVICE_LAYER_PLAN.md](../architecture/SERVICE_LAYER_PLAN.md)
- [docs/training/DASHBOARD_METRIC_INTERPRETATION_GUIDE.md](../../docs/training/DASHBOARD_METRIC_INTERPRETATION_GUIDE.md)
- [stitch_role_based_exam_platform/](../../stitch_role_based_exam_platform)

## Next Files To Add

- `role-manuals/admin.md`
- `role-manuals/teacher.md`
- `role-manuals/staff.md`
- `dashboard-guides/`
- `journeys/`
- `troubleshooting/`
- `playbooks/`
