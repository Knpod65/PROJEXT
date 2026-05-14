# Optimization Governance UI Contract

**Status:** Implemented — Phase 1C  
**Date:** 2026-05-14  
**Files:** `frontend/src/types/optimizationGovernance.ts`, `frontend/src/utils/optimizationGovernance.ts`

---

## Purpose

Define the typed contract between backend governance payloads and frontend UI
components. No full UI components are built in this phase — only the type
definitions and pure utility formatters that all future governance UI widgets
will depend on.

---

## Type Hierarchy

```
OptimizationGovernanceReport          ← top-level API response
├── executive_summary
│   ├── GovernanceState               ← "AUTO_APPROVED" | "BLOCKED" | ...
│   ├── ReviewPriority                ← "LOW" | "NORMAL" | "HIGH" | "CRITICAL"
│   ├── quality_score: number | null
│   └── checked_schedule_count: number
├── severity_summary: SeveritySummary
│   ├── hard_fail_count: number
│   ├── warning_count: number
│   ├── info_count: number
│   └── suggestion_count: number
├── issue_summary: GovernanceIssue[]  ← issue table rows
└── governance: GovernanceDecision
    ├── governance_state: GovernanceState
    ├── override_analysis: OverrideAnalysis
    │   └── override_severity: OverrideSeverity
    └── quality_snapshot: QualitySnapshot
```

Additional standalone types: `TraceEvent`, `RejectedAlternative`

---

## UI Widget → Type Mapping

| Widget | Type Used |
|---|---|
| Quality score badge | `QualitySnapshot`, `qualityScoreBadgeVariant()` |
| Governance status badge | `GovernanceState`, `governanceStateBadgeVariant()` |
| Severity summary cards | `SeveritySummary`, `totalIssueCount()`, `hasBlockingIssues()` |
| Issue table | `GovernanceIssue[]`, `issueSeverityBadgeVariant()`, `filterBlockingIssues()` |
| Explanation drawer | `GovernanceDecision`, `overrideWarningMessage()` |
| Rejected alternative list | `RejectedAlternative[]` |
| Trace timeline | `TraceEvent[]`, `sortTraceEvents()`, `traceEventLabel()` |
| Override impact panel | `OverrideAnalysis`, `isHighRiskOverride()` |
| Audit timeline | `GovernanceDecision.governance_notes[]` |

---

## Utility Functions

```typescript
// Governance state
isGovernanceBlocked(state)           → boolean
requiresHumanAction(state)           → boolean
isAutoApproved(state)                → boolean
requiresEscalation(state)            → boolean

// Badge variants
governanceStateBadgeVariant(state)   → "success"|"warning"|"error"|"info"
reviewPriorityBadgeVariant(priority) → "success"|"warning"|"error"|"info"
issueSeverityBadgeVariant(severity)  → "success"|"warning"|"error"|"info"
qualityScoreBadgeVariant(score)      → "success"|"warning"|"error"|"info"

// Issue helpers
isBlockingIssue(issue)               → boolean
filterBlockingIssues(issues)         → GovernanceIssue[]
dominantSeverity(issues)             → IssueSeverity

// Override helpers
overrideWarningMessage(decision)     → string | null
isHighRiskOverride(decision)         → boolean

// Quality
qualityScoreLabel(snapshot)          → string  e.g. "88 / 100"
isBelowReviewThreshold(snapshot)     → boolean  (threshold: 70)

// Severity summary
totalIssueCount(summary)             → number
hasBlockingIssues(summary)           → boolean

// Trace timeline
traceEventLabel(eventType)           → string
isBlockingTraceEvent(event)          → boolean
sortTraceEvents(events)              → TraceEvent[]  (chronological)

// Report-level
reportGovernanceState(report)        → GovernanceState
reportRequiresImmediateAction(report) → boolean
```

---

## Test Plan (TypeScript-only — no test runner installed)

Since no Jest/Vitest is configured, validation is TypeScript-compile-only:

1. **`npm run build` must pass** with zero TS errors after adding these two files.
2. **Import smoke check:** Adding `import { isGovernanceBlocked } from "@/utils/optimizationGovernance"` to any existing page file must not break the build.
3. **Logical smoke checks** (manual or future Vitest setup):
   - `isGovernanceBlocked("BLOCKED")` → `true`
   - `isGovernanceBlocked("AUTO_APPROVED")` → `false`
   - `governanceStateBadgeVariant("AUTO_APPROVED")` → `"success"`
   - `governanceStateBadgeVariant("BLOCKED")` → `"error"`
   - `qualityScoreBadgeVariant(88)` → `"success"`
   - `qualityScoreBadgeVariant(55)` → `"error"`
   - `dominantSeverity([{severity:"WARNING"}, {severity:"INFO"}])` → `"WARNING"`
   - `overrideWarningMessage({override_analysis:{override_severity:"SAFE",...}})` → `null`
   - `totalIssueCount({hard_fail_count:1,warning_count:2,info_count:0,suggestion_count:0})` → `3`
   - `sortTraceEvents([b,a])` returns `[a,b]` when `a.timestamp < b.timestamp`

---

## Backend Correspondence

| TypeScript | Python |
|---|---|
| `GovernanceState` | `governance_state` string in `determine_governance_state()` return |
| `ReviewPriority` | `review_priority` field in governance dict |
| `GovernanceIssue` | `RecheckIssue` (recheck_service) + governance issue list |
| `TraceEvent` | `build_trace_event()` output (optimization_trace_service) |
| `QualitySnapshot` | `compute_quality_report()` subset (quality_service) |
| `OverrideAnalysis` | `analyze_override_safety()` return (governance_service) |
