/**
 * optimizationGovernance.ts — TypeScript contract for the governance UI.
 *
 * Mirrors backend services/optimization_governance_service.py payloads 1:1.
 * Used by: quality score badge, governance status badge, severity summary cards,
 * issue table, explanation drawer, rejected alternative list, trace timeline,
 * override impact panel, audit timeline.
 *
 * No component code here — types and enums only.
 */

// ── Governance state ──────────────────────────────────────────────────────

export type GovernanceState =
  | "AUTO_APPROVED"
  | "APPROVAL_REQUIRED"
  | "MANUAL_REVIEW_REQUIRED"
  | "ESCALATION_REQUIRED"
  | "BLOCKED";

export type ReviewPriority = "LOW" | "NORMAL" | "HIGH" | "CRITICAL";

export type OverrideSeverity = "SAFE" | "REVIEW_REQUIRED" | "HIGH_RISK";

export type IssueSeverity = "INFO" | "SUGGESTION" | "WARNING" | "HARD_FAIL";

export type TraceSource = "POST_HOC_TRACE" | "POLICY_RULE" | "SOLVER_TRACE";

export type TraceEventType =
  | "OPTIMIZATION_STARTED"
  | "CANDIDATE_GENERATED"
  | "CANDIDATE_REJECTED"
  | "CANDIDATE_SCORED"
  | "CONSTRAINT_APPLIED"
  | "PENALTY_APPLIED"
  | "ROOM_SELECTED"
  | "STAFF_SELECTED"
  | "DISTRIBUTOR_SELECTED"
  | "SPLIT_DECISION_MADE"
  | "FALLBACK_USED"
  | "FINAL_SELECTION_ACCEPTED"
  | "RECHECK_STARTED"
  | "RECHECK_COMPLETED"
  | "GOVERNANCE_DECISION_CREATED";

// ── Issue table row ───────────────────────────────────────────────────────

export interface GovernanceIssue {
  severity: IssueSeverity;
  category: string;
  code: string;
  message: string;
  course_id?: string | null;
  section?: string | null;
  exam_date?: string | null;
  exam_time?: string | null;
  room_id?: number | null;
  actor_id?: number | null;
  suggested_fix?: string | null;
  can_override?: boolean;
  blocking?: boolean;
  source?: string | null;
}

// ── Override impact panel ─────────────────────────────────────────────────

export interface OverrideAnalysis {
  override_severity: OverrideSeverity;
  override_recommendation: string;
  override_changes: string[];
  introduced_risks: string[];
  violated_constraints: string[];
  requires_escalation: boolean;
}

// ── Quality score badge ───────────────────────────────────────────────────

export interface QualitySnapshot {
  overall_score: number | null;
  quality_band: string | null;
  risk_level: string | null;
}

// ── Governance status badge + audit timeline row ──────────────────────────

export interface GovernanceDecision {
  governance_state: GovernanceState;
  approval_reasoning: string;
  escalation_reason: string | null;
  override_recommendation: string;
  governance_notes: string[];
  review_priority: ReviewPriority;
  override_analysis: OverrideAnalysis;
  reason: string | null;
  quality_snapshot: QualitySnapshot;
  policy_snapshot: Record<string, unknown>;
  recheck_summary: Record<string, number | boolean>;
}

// ── Severity summary cards ────────────────────────────────────────────────

export interface SeveritySummary {
  hard_fail_count: number;
  warning_count: number;
  info_count: number;
  suggestion_count: number;
}

// ── Trace timeline row ────────────────────────────────────────────────────

export interface TraceEvent {
  event_type: TraceEventType | string;
  entity_type: string | null;
  entity_id: unknown;
  constraint_code: string | null;
  reason_code: string | null;
  score_delta: number | null;
  severity: IssueSeverity | string;
  source: TraceSource | string;
  metadata: Record<string, unknown>;
  timestamp: string;
}

// ── Rejected alternative list ─────────────────────────────────────────────

export interface RejectedAlternative {
  candidate_type: string;
  candidate_id: unknown;
  rejection_reason: string;
  violated_constraint: string | null;
  severity: IssueSeverity | string;
  improvement_hint: string | null;
}

// ── Full report (top-level API response shape) ────────────────────────────

export interface OptimizationGovernanceReport {
  executive_summary: {
    governance_state: GovernanceState;
    review_priority: ReviewPriority;
    quality_score: number | null;
    quality_band: string | null;
    checked_schedule_count: number;
  };
  severity_summary: SeveritySummary;
  issue_summary: GovernanceIssue[];
  governance: GovernanceDecision;
}
