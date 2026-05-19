import { get } from "./api";
import type { GovernanceOverview } from "@/types/governance";

/**
 * Fetch the executive summary and derive a governance overview from it.
 * The executive-summary endpoint (D4.9) already returns 7 of the 12 governance fields:
 *   overall_health_score, risk_band, governance_blocker_count,
 *   publication_ready_count, optimization_quality_avg, room_utilization_score,
 *   pdpa_alert_count, top_risks, recommended_actions
 *
 * Fields derived or defaulted here:
 *   override_count, rollback_count, escalation_count, publication_blocked_count,
 *   pending_approval_count, overdue_signing_count → 0 (safe default until D5.8
 *   thin proxy endpoints expose governance-timeline and lifecycle-timeline).
 *   recent_events → [] (same rationale).
 *   faculty_summary → [] (single-faculty mode; populated when multi-faculty is active).
 */
export function getGovernanceOverview() {
  return get<GovernanceOverview>("/analytics/executive-summary").then((summary) => ({
    ...summary,
    override_count: 0,
    rollback_count: 0,
    escalation_count: 0,
    publication_blocked_count: 0,
    pending_approval_count: 0,
    overdue_signing_count: 0,
    recent_events: [],
    faculty_summary: [],
  }));
}
