import type { StatusTone } from "@/components/ui/StatusChip";
import type { OptimizationTraceSummary, TraceConstraintHit } from "@/types/optimizationTrace";

export type TraceDisplayState = "queryError" | "missingSession" | "limited" | "valid";

export function getTraceDisplayState(trace: OptimizationTraceSummary | undefined, error: unknown): TraceDisplayState {
  if (error) return "queryError";
  if (!trace) return "missingSession";

  const isEmptyStub =
    trace.trace_id.startsWith("stub-") &&
    trace.events.length === 0 &&
    trace.candidates.length === 0 &&
    trace.constraint_hits.length === 0;

  if (isEmptyStub) return "missingSession";
  if (trace.events.length === 0 && trace.candidates.length === 0 && trace.constraint_hits.length === 0) return "limited";
  return "valid";
}

export function getTraceGovernance(trace: OptimizationTraceSummary) {
  const failedHard = trace.constraint_hits.filter((item) => item.severity === "hard" && !item.passed).length;
  const failedSoft = trace.constraint_hits.filter((item) => item.severity === "soft" && !item.passed).length;
  const recheckIssues = trace.recheck_issues.length;

  if (failedHard > 0 || recheckIssues > 0) {
    return { key: "blocked", tone: "danger" as StatusTone };
  }
  if (failedSoft > 0) {
    return { key: "attention", tone: "warning" as StatusTone };
  }
  return { key: "clear", tone: "success" as StatusTone };
}

export function traceSeverityTone(severity: string): StatusTone {
  if (severity === "error" || severity === "critical" || severity === "hard") return "danger";
  if (severity === "warning" || severity === "soft") return "warning";
  if (severity === "info") return "information";
  return "neutral";
}

export function traceConstraintTone(constraint: TraceConstraintHit): StatusTone {
  if (constraint.passed) return "success";
  return constraint.severity === "hard" ? "danger" : "warning";
}
