# Frontend Governance Contract
## EMS Academic Operations Platform — Canonical API Shapes
**Date:** 2026-05-14
**Phase:** C1–C9 Lifecycle Capability + Authoritative Governance

---

## 1. Design Rules

1. **Frontend MUST NOT infer lifecycle state.** Use `derived_schedule_state` from the backend. Never compute it from `session_status` in the client.
2. **Frontend MUST NOT compute capabilities.** Use the `/capabilities` endpoint. Never replicate the role × state × governance matrix in the client.
3. **Frontend MUST NOT decide publishability.** Use `can_publish` from `/capabilities` or `risk_score` from `/publication-readiness`.
4. **Frontend MUST NOT bypass governance.** All state-mutating actions must be confirmed against the transition-check result before being submitted.

---

## 2. Lifecycle Semantics — session_status → derived_schedule_state

| `session_status` (OptimizeSession.status) | `derived_schedule_state` | Meaning |
|---|---|---|
| `draft` | `OPTIMIZED` | Schedule generated, not yet in governance review |
| `confirming` | `GOVERNANCE_REVIEW` | Round-1 signing in progress |
| `confirmed` | `APPROVED` | All required signatures collected |
| `swap_open` | `APPROVED` | Approved; exam swap window is open |
| `swap_confirming` | `GOVERNANCE_REVIEW` | Post-swap round-2 signing in progress |
| `locked` | `APPROVED` | Fully locked, all swap rounds complete |

**Governance override:** If `governance_state == "BLOCKED"` and derived state would be `APPROVED`, backend overrides to `GOVERNANCE_REVIEW`.

---

## 3. Endpoint Shapes

### 3.1 GET /api/workflow/sessions/{id}/governance

```typescript
interface GovernanceReport {
  governance: {
    governance_state: string;          // AUTO_APPROVED | BLOCKED | ESCALATION_REQUIRED | ...
    review_priority: string;           // LOW | MEDIUM | HIGH | CRITICAL
    approval_reasoning: string;
    escalation_reason?: string;
  };
  quality_breakdown: {
    overall_score: number;
    quality_band: string;              // EXCELLENT | GOOD | ACCEPTABLE | POOR
    risk_level: string;
    warnings: string[];
    future_operational_risks: string[];
    fairness_instability_warnings: string[];
    staffing_fragility_warnings: string[];
    overloaded_day_warnings: string[];
    risk_summary: string;
  };
  severity_summary: {
    hard_fail_count: number;
    warning_count: number;
  };
  derived_schedule_state: string;      // DO NOT infer — use this value directly
  valid_next_states: string[];
  session_status: string;
}
```

### 3.2 GET /api/workflow/sessions/{id}/publication-readiness

```typescript
interface PublicationReadiness {
  can_publish: boolean;
  risk_score: number;                  // 0–100; lower is safer
  blockers: Array<{
    code: string;
    reason: string;
    severity: "HARD_FAIL" | "WARNING";
    can_override: boolean;
  }>;
  warnings: string[];
  derived_schedule_state: string;
  valid_next_states: string[];
  session_status: string;
}
```

### 3.3 GET /api/workflow/sessions/{id}/capabilities

Returns what the **current authenticated user** can do on this session.

```typescript
interface ScheduleCapabilities {
  can_publish: boolean;
  can_unpublish: boolean;
  can_archive: boolean;
  can_reopen: boolean;
  can_rollback: boolean;
  can_edit: boolean;
  can_regenerate: boolean;
  can_open_swap_window: boolean;
  can_finalize: boolean;
  blocking_reasons: string[];          // Human-readable why a capability is false
  warnings: string[];
  required_actions: string[];          // e.g. "resolve_hard_failures"
}
```

**Rules:**
- All admin-only actions (`can_publish`, `can_archive`, `can_rollback`, `can_regenerate`, `can_open_swap_window`) are `false` for non-admin roles.
- `can_finalize` is `true` for admin/esq_head/secretary when session_status is `confirming` or `swap_confirming`.
- `can_edit` is `true` for admin, dept_supervisor, teacher when schedule is not LOCKED or ARCHIVED.
  - Note: dept_supervisor and teacher are scoped to their own department — query layer enforces this; capability returns `true` for the role check.

### 3.4 GET /api/workflow/sessions/{id}/transition-check?target_state=PUBLISHED

Pre-flight check. **Never mutates state.** Frontend should call this before showing a confirmation dialog.

```typescript
interface TransitionCheckResult {
  allowed: boolean;
  target_state: string;
  transition_type: "normal" | "rollback" | "publication" | "archival";
  blockers: Array<{
    code: string;
    reason: string;
    severity: "HARD_FAIL" | "WARNING";
    can_override: boolean;
  }>;
  warnings: string[];
  required_actions: string[];
  audit_required: boolean;
  requires_emergency_override: boolean;
  state_machine_result: object | null;  // Present only when allowed=true
}
```

**Blocker codes:**
| Code | Meaning |
|---|---|
| `ROLE_INSUFFICIENT` | Current role cannot trigger this transition |
| `GOVERNANCE_BLOCKED` | Governance state is BLOCKED |
| `HARD_FAILS_PRESENT` | Hard failures must be resolved first |
| `INVALID_TRANSITION_EDGE` | This transition is not in the state machine |
| `ROLLBACK_REQUIRES_ADMIN` | Only admin can roll back |
| `STATE_MACHINE_GUARD` | State machine guard condition not met |

### 3.5 GET /api/workflow/sessions/{id}/executive-risk

```typescript
interface ExecutiveRiskReport {
  overall_risk_band: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  publishability_score: number;         // 100 - risk_score; higher is safer
  governance_health: "HEALTHY" | "REVIEW_REQUIRED" | "BLOCKED";
  critical_blockers: Array<{
    code: string;
    reason: string;
    severity: "HARD_FAIL";
    can_override: boolean;
  }>;
  operational_risks: string[];
  pdpa_risks: string[];                 // Warnings flagged for PDPA/PII keywords
  fairness_risks: string[];
  staffing_risks: string[];
  overloaded_day_risks: string[];
  quality_snapshot: {
    overall_score: number;
    quality_band: string;
    risk_level: string;
  };
  risk_summary: string;
  hard_fail_count: number;
  warning_count: number;
}
```

**Risk band logic (read-only, do not replicate):**
- `CRITICAL`: governance_state == "BLOCKED" OR hard_fail_count > 0
- `HIGH`: risk_score >= 70 OR governance_state in (ESCALATION_REQUIRED, MANUAL_REVIEW_REQUIRED)
- `MEDIUM`: risk_score >= 40 OR warning_count > 3
- `LOW`: otherwise

---

## 4. Usage Patterns

### Display a publish button
```typescript
const { can_publish, blocking_reasons } = await fetchCapabilities(sessionId);
// Only render the button if can_publish === true
// Show blocking_reasons as tooltip when false
```

### Pre-flight before mutation
```typescript
const check = await fetchTransitionCheck(sessionId, "PUBLISHED");
if (!check.allowed) {
  showBlockerDialog(check.blockers);
  return;
}
if (check.audit_required) {
  requireAuditAnnotation();
}
// Proceed with the actual mutation call
await publishSchedule(sessionId);
```

### Executive dashboard
```typescript
const risk = await fetchExecutiveRisk(sessionId);
// risk.overall_risk_band → color-coded badge
// risk.publishability_score → gauge component
// risk.critical_blockers → list of hard blockers
// risk.pdpa_risks → PDPA attention section
```

---

## 5. Auth Requirements

| Endpoint | Minimum Role |
|---|---|
| `/governance` | admin, esq_head, or secretary (VIEW_ALL_ROLES) |
| `/publication-readiness` | admin, esq_head, or secretary (VIEW_ALL_ROLES) |
| `/capabilities` | any authenticated user (capabilities scoped to their role) |
| `/transition-check` | any authenticated user (result scoped to their role) |
| `/executive-risk` | admin, esq_head, or secretary (VIEW_ALL_ROLES) |
