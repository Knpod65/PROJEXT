# EMS Original Intent Recenter — Source Review

**Date:** 2026-06-30
**Purpose:** Document the original intended scope of EMS, identify later scope additions, and establish safety boundaries for the de-scoping pass.

---

## Docs Consulted

| Document | Location | Purpose |
|----------|----------|---------|
| EMS_SCOPE_BOUNDARY_EXAM_AND_INVIGILATION_ONLY.md | docs/architecture/ | Authoritative scope boundary (primary source) |
| EMS_CORRECTED_NEXT_PHASE_ROADMAP.md | docs/architecture/ | 9-stage roadmap; gates and blockers |
| EMS_ROADMAP_TO_100_PERCENT.md | docs/architecture/ | Full 10-stage maturity path |
| PROJECT_OVERVIEW.md | docs/ | Target users and intended operational flows |
| DEMO_LIMITATIONS_AND_DISCLOSURE.md | docs/ | What the demo proves vs. does not prove |
| FEATURES.md | docs/ | Full feature checklist |
| FINAL_PLATFORM_READINESS_REPORT.md | docs/ | Demo/pilot/production readiness scores |
| OPERATIONAL_INTELLIGENCE_ROADMAP.md | docs/architecture/ | Metrics taxonomy (added features) |
| EMS_FULL_ROUTE_VISUAL_ACCEPTANCE_MATRIX.md | docs/architecture/ | 47-route visual certification evidence |
| UX_UI_HUMANIZATION_AUDIT.md | docs/architecture/ | Cognitive load and UX assessment |
| EMS_ARCHITECTURE_MAP.md | docs/architecture/ | System topology and module registry |
| DOMAIN_BOUNDARY_MAP.md | docs/architecture/ | 9 bounded domains + domain violations |

---

## Original Intended Product Scope

The following 10 capabilities represent the original intended scope of EMS, as documented in the authoritative scope boundary file and the project overview:

1. **Exam period and term lifecycle management**
   Manage academic terms, exam windows, and period configuration that all other modules depend on.

2. **Academic data import**
   Bulk import of course, section, and enrollment data from university source systems.

3. **Exam schedule creation, room allocation, and timetable**
   Build and publish the master exam timetable with room-by-room allocation.

4. **Staff availability + invigilator assignment + optimization**
   Collect staff availability constraints, run optimization, assign invigilators to rooms.

5. **Exam submission workflow**
   Multi-step teacher → department → approval chain workflow for exam paper submissions.

6. **Print queue, copy count, and pre-print review**
   Manage print job creation, copy count calculation, and pre-print verification gate.

7. **QR-based paper pickup, room check-in, and attendance**
   QR code generation, camera scan at pickup, room attendance confirmation for exam day.

8. **Invigilator swap requests and approval**
   Allow invigilators to request schedule swaps; route through approval chain.

9. **Draft invigilation payment documents**
   Calculate and preview invigilation payment (ค่าคุมสอบ) based on configured rates.
   **DRAFT ONLY — no final authorization implemented. Teaching workload compensation is explicitly out of scope.**

10. **Role-aware operational dashboard and exports**
    Real-time operational overview per role; export center for schedule, workload, and payment documents.

---

## Authoritative Scope Boundary

From `EMS_SCOPE_BOUNDARY_EXAM_AND_INVIGILATION_ONLY.md`:

### Explicitly IN Scope
- Exam scheduling, room assignment, student exam timetable
- Staff availability and invigilator assignment
- Exam duty workload and fairness
- Check-in, attendance, and confirmation of invigilation duty
- Exam paper distribution
- **Invigilation payment calculation and reporting ONLY**

### Explicitly OUT of Scope
- Excess teaching compensation
- Teaching workload calculation
- Course eligibility for teaching pay
- Co-teaching workload payment
- Thesis/advisor workload payment
- Base workload hours
- Any teaching compensation workbooks

### Key Terminology Rules
- `payment` in EMS = invigilation payment (ค่าคุมสอบ) only
- `compensation` in EMS = invigilation payment only
- `workload` in EMS = exam duty workload only

---

## Readiness Scores (as of 2026-06-30)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Demo readiness | 96–98/100 | Fully interactive, 47 routes certified |
| Pilot readiness | 42/100 | Blocked: Faculty LAN contract, PostgreSQL, DPO signoff |
| Production readiness | 28/100 | Requires pilot evidence + real environment |

---

## Later Scope Additions (Post-Original)

The following features were added after the core operational scope was established. Each was motivated by demo maturity signaling or advanced platform features rather than daily staff operational need.

| Feature | Page/Route | Added In | Motivation | Daily User Need? |
|---------|-----------|----------|------------|-----------------|
| Admin Intelligence Dashboard | `/admin-intelligence-dashboard` | feat(ui): redesign admin intelligence dashboard | Demo platform maturity signal | No |
| Executive Analytics | `/analytics` | refactor(ui): align governance and intelligence pages | Institutional trend analysis for exec demo | No |
| Governance Cockpit | `/governance` | refactor(ui): align governance and intelligence pages | Approval blocker aggregation view | Rarely |
| Operational Health | `/operational-health` | system/platform build phase | Backend and service health monitoring | No (IT/dev) |
| Audit Explorer | `/audit-explorer` | system/platform build phase | User-facing audit event browser | No (compliance/dev) |
| Optimizer Trace Explorer | `/optimizer-trace` | system/platform build phase | Optimization lineage and scoring | No (dev/admin) |
| Platform Configuration | `/platform-config` | system/platform build phase | Faculty governance config (D3–D5 maturity) | No (complex config) |
| Historical Schedules | `/historical-schedules` | historical comparison | 2-term schedule comparison | Seasonally (fairness audit) |
| Co-Exam Planning | `/coexam` | co-exam feature | Shared-exam candidate grouping | Rarely (specialized) |
| Import Audit | `/import-audit` | import v2 build | Import session browser | Rarely (admin review) |

---

## Evidence of Scope Expansion Tension

### From demo limitation docs
> "Rich intelligence layer functional (Admin Intelligence, Workload fairness, Governance, Audit, Operational Health, Executive Analytics)"

This phrase appears in the demo as a **strength claim** — but it describes features built to demonstrate platform maturity, not features requested by faculty staff for daily operations.

### From UX/UI humanization audit
> "Large operational pages (Checkins, MyExam, Optimizer, WorkflowV2) still have higher cognitive load."
> "Legacy vs. V2 page coexistence creates confusion."

The app has grown large enough that even its own audit flags cognitive load problems in core pages.

### From platform config wiring
> "Platform Config: partial wiring; backend snapshot shows empty arrays — UI can imply readiness not yet supported."

Platform Configuration page presents governance config options that are not yet wired to real data, creating a misleading impression of readiness for features that are D3–D5 maturity targets.

### From roadmap gates
> "PENDING_FINANCE_ADMIN_REVIEW — Supporting finance invigilation roster design opened; 5 implementation blockers resolved via clarification."

Payment calculation remains unfinished and blocked on external decisions. Yet the payment-related pages (draft, preview, settings) are all visible in the nav.

### From feature documentation
Pages marked as D5 maturity in the platform capability matrix but appearing in the active nav:
- Governance Cockpit
- Full Analytics Dashboard
- PDPA Runtime Guard
- Operational Health

---

## Current System Scale (as of this audit)

| Metric | Count |
|--------|-------|
| Active routes (App.tsx) | 50 |
| Navigation config entries | 68 |
| Page components (TSX) | 48 |
| Custom hooks | 45+ |
| Backend routers | 35 |
| API endpoint prefixes | 32 |
| Architecture docs | 313 MD files |
| i18n keys (Thai/English) | 1,953 |
| Backend tests passing | 1,428+ |

---

## Safety Boundaries for This De-scoping Pass

The following must NOT be changed during this audit pass or any subsequent Phase B navigation cleanup:

| Area | Why |
|------|-----|
| Payment calculation logic | Draft-only, correctly scoped, unfinished — must not be touched |
| Export logic | Core to exam operations and finance docs |
| Schedule/optimizer | Core product functionality |
| Auth and role guards | Core security — changes require full regression |
| All backend routers | Read-only in this pass |
| Database schema | No schema changes |
| Any route that IS currently flagged `hidden: true` | Already correct |
| Print queue and QR logic | Core exam-day workflow |

---

## Conclusion

The EMS was correctly scoped at its origin. The core operational flow is:

```
period → import → schedule → staff availability → optimize →
submissions → print review → print queue → checkins/QR →
invigilation payment draft → exports
```

Features outside this flow were added to demonstrate platform maturity for demo and exec signoff. They should be classified and handled without code deletion — starting with hiding from the main navigation for the pilot phase.

The de-scoping goal is **not to remove capability** but to **reduce cognitive load and scope confusion for real faculty staff** during the controlled pilot.
