// Governance cockpit type contracts.
// Read-only aggregate shapes derived from existing backend services.
export interface GovernanceOverview {
  overall_health_score: number;
  risk_band: "green" | "amber" | "red";
  blocker_count: number;
  override_count: number;
  rollback_count: number;
  escalation_count: number;
  publication_ready_count: number;
  publication_blocked_count: number;
  pending_approval_count: number;
  overdue_signing_count: number;
  top_risks: Array<{
    risk: string;
    severity: string;
    category: string;
  }>;
  recent_events: Array<{
    event_type: string;
    timestamp: string;
    severity: string;
    detail: string;
  }>;
  faculty_summary: Array<{
    faculty_id: string;
    faculty_name: string;
    health_score: number;
    blocker_count: number;
  }>;
}

export interface GovernanceRiskItem {
  risk: string;
  severity: "low" | "medium" | "high" | "critical";
  category: string;
}

export interface GovernanceEventItem {
  event_type: string;
  timestamp: string;
  severity: "info" | "warning" | "error" | "critical";
  detail: string;
}

export interface FacultyGovernanceSummary {
  faculty_id: string;
  faculty_name: string;
  health_score: number;
  blocker_count: number;
}
