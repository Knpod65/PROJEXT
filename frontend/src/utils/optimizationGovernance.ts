/**
 * optimizationGovernance.ts — Utility helpers for governance UI rendering.
 *
 * Pure functions only — no React, no side effects, no API calls.
 * All functions accept typed interfaces from types/optimizationGovernance.ts
 * and return display-ready primitives (string, boolean, badge variant).
 *
 * Usage:
 *   import { isGovernanceBlocked, governanceStateBadgeVariant } from "@/utils/optimizationGovernance";
 */

import type {
  GovernanceDecision,
  GovernanceIssue,
  GovernanceState,
  IssueSeverity,
  OptimizationGovernanceReport,
  OverrideSeverity,
  QualitySnapshot,
  ReviewPriority,
  SeveritySummary,
  TraceEvent,
} from "@/types/optimizationGovernance";

// ── Governance state helpers ──────────────────────────────────────────────

/** Returns true if the schedule is blocked from release. */
export function isGovernanceBlocked(state: GovernanceState): boolean {
  return state === "BLOCKED";
}

/** Returns true if any human approval or review step is required. */
export function requiresHumanAction(state: GovernanceState): boolean {
  return state !== "AUTO_APPROVED";
}

/** Returns true if governance has been fully approved without conditions. */
export function isAutoApproved(state: GovernanceState): boolean {
  return state === "AUTO_APPROVED";
}

/** Returns true if escalation to a higher authority is required. */
export function requiresEscalation(state: GovernanceState): boolean {
  return state === "ESCALATION_REQUIRED";
}

// ── Badge variant helpers ─────────────────────────────────────────────────

/** Maps governance state → badge colour token for the status badge component. */
export function governanceStateBadgeVariant(
  state: GovernanceState,
): "success" | "warning" | "error" | "info" {
  switch (state) {
    case "AUTO_APPROVED":
      return "success";
    case "BLOCKED":
    case "ESCALATION_REQUIRED":
      return "error";
    case "MANUAL_REVIEW_REQUIRED":
    case "APPROVAL_REQUIRED":
      return "warning";
    default:
      return "info";
  }
}

/** Maps review priority → badge colour token. */
export function reviewPriorityBadgeVariant(
  priority: ReviewPriority,
): "success" | "warning" | "error" | "info" {
  switch (priority) {
    case "LOW":
      return "success";
    case "CRITICAL":
      return "error";
    case "HIGH":
      return "warning";
    default:
      return "info";
  }
}

/** Maps issue severity → badge colour token. */
export function issueSeverityBadgeVariant(
  severity: IssueSeverity | string,
): "success" | "warning" | "error" | "info" {
  switch (severity) {
    case "HARD_FAIL":
      return "error";
    case "WARNING":
      return "warning";
    case "SUGGESTION":
      return "info";
    default:
      return "info";
  }
}

/** Maps quality score (0–100) → badge colour token. */
export function qualityScoreBadgeVariant(
  score: number | null,
): "success" | "warning" | "error" | "info" {
  if (score === null) return "info";
  if (score >= 85) return "success";
  if (score >= 70) return "warning";
  return "error";
}

// ── Issue helpers ─────────────────────────────────────────────────────────

/** Returns true if the issue is an operational blocker. */
export function isBlockingIssue(issue: GovernanceIssue): boolean {
  return issue.blocking === true || issue.severity === "HARD_FAIL";
}

/** Returns true if the issue can be overridden by a human decision. */
export function isOverridable(issue: GovernanceIssue): boolean {
  return issue.can_override === true;
}

/** Filter to only blocking issues. */
export function filterBlockingIssues(
  issues: GovernanceIssue[],
): GovernanceIssue[] {
  return issues.filter(isBlockingIssue);
}

/** Filter to only overridable issues. */
export function filterOverridableIssues(
  issues: GovernanceIssue[],
): GovernanceIssue[] {
  return issues.filter(isOverridable);
}

/** Returns the dominant (worst) severity across an issue list. */
export function dominantSeverity(
  issues: GovernanceIssue[],
): IssueSeverity {
  if (issues.some((i) => i.severity === "HARD_FAIL")) return "HARD_FAIL";
  if (issues.some((i) => i.severity === "WARNING")) return "WARNING";
  if (issues.some((i) => i.severity === "SUGGESTION")) return "SUGGESTION";
  return "INFO";
}

// ── Override impact helpers ───────────────────────────────────────────────

/** Returns a user-facing override warning message, or null if safe. */
export function overrideWarningMessage(
  decision: GovernanceDecision,
): string | null {
  const { override_severity, override_recommendation } =
    decision.override_analysis;
  if (override_severity === "SAFE") return null;
  return override_recommendation || null;
}

/** Returns true if overriding would introduce high risk. */
export function isHighRiskOverride(decision: GovernanceDecision): boolean {
  return decision.override_analysis.override_severity === "HIGH_RISK";
}

// ── Quality score helpers ─────────────────────────────────────────────────

/** Returns a display string for the quality score (e.g. "88 / 100"). */
export function qualityScoreLabel(snapshot: QualitySnapshot): string {
  if (snapshot.overall_score === null) return "N/A";
  return `${Math.round(snapshot.overall_score)} / 100`;
}

/** Returns true if the quality score is below the review threshold (70). */
export function isBelowReviewThreshold(snapshot: QualitySnapshot): boolean {
  return snapshot.overall_score !== null && snapshot.overall_score < 70;
}

// ── Severity summary helpers ──────────────────────────────────────────────

/** Returns total issue count across all severities. */
export function totalIssueCount(summary: SeveritySummary): number {
  return (
    summary.hard_fail_count +
    summary.warning_count +
    summary.info_count +
    summary.suggestion_count
  );
}

/** Returns true if the severity summary has any blocking issues. */
export function hasBlockingIssues(summary: SeveritySummary): boolean {
  return summary.hard_fail_count > 0;
}

// ── Trace timeline helpers ────────────────────────────────────────────────

/** Returns a human-readable label for a trace event type. */
export function traceEventLabel(eventType: string): string {
  return eventType
    .replace(/_/g, " ")
    .toLowerCase()
    .replace(/^./, (c) => c.toUpperCase());
}

/** Returns true if the trace event represents a blocking constraint. */
export function isBlockingTraceEvent(event: TraceEvent): boolean {
  return event.severity === "HIGH_RISK" || event.severity === "HARD_FAIL";
}

/** Sort trace events chronologically (ascending). */
export function sortTraceEvents(events: TraceEvent[]): TraceEvent[] {
  return [...events].sort((a, b) =>
    a.timestamp < b.timestamp ? -1 : a.timestamp > b.timestamp ? 1 : 0,
  );
}

// ── Report-level helpers ──────────────────────────────────────────────────

/** Extract the executive summary governance state from a full report. */
export function reportGovernanceState(
  report: OptimizationGovernanceReport,
): GovernanceState {
  return report.executive_summary.governance_state;
}

/** Returns true if the full report requires immediate attention. */
export function reportRequiresImmediateAction(
  report: OptimizationGovernanceReport,
): boolean {
  return (
    report.executive_summary.governance_state === "BLOCKED" ||
    report.executive_summary.review_priority === "CRITICAL"
  );
}
