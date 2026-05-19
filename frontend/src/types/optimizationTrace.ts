// Optimization trace explorer types.
// Shapes match optimize_trace_aggregator_service output (D2) and the analytics proxy.

export interface TraceCandidate {
  candidate_id: string;
  room_code: string;
  timeslot: string;
  staff_id: string;
  score: number;
  selected: boolean;
  rejection_reasons: string[];
}

export interface TraceConstraintHit {
  constraint_type: string;
  severity: "hard" | "soft";
  passed: boolean;
  detail: string;
}

export interface TraceEvent {
  event_id: string;
  stage: string;
  event_type: string;
  timestamp: string;
  severity: "info" | "warning" | "error";
  detail: string;
}

export interface RecheckIssueItem {
  issue: string;
  severity: string;
}

export interface OptimizationTraceSummary {
  session_id: number;
  trace_id: string;
  generated_at: string;
  overall_quality_score: number;
  traceability_completeness_score: number;
  candidates: TraceCandidate[];
  constraint_hits: TraceConstraintHit[];
  events: TraceEvent[];
  rejected_alternatives_count: number;
  recheck_issues: RecheckIssueItem[];
  quality_note?: string;
}
