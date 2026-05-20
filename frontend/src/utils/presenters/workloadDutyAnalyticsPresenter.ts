import { translateWithFallback } from "@/i18n";
import type { WorkloadDutyAnalyticsPayload, WorkloadDutyAnalyticsPerson } from "@/types/workloadDutyAnalytics";

export interface WorkloadSummaryCard {
  label: string;
  value: string;
  hint: string;
}

export function presentWorkloadPerson(person: WorkloadDutyAnalyticsPerson) {
  return {
    personId: person.person_id,
    displayName: person.display_name,
    roleGroup: translateWithFallback(`workloadDashboard.roleGroup.${person.role_group}`, person.role_group),
    invigilation: person.invigilation_count,
    distribution: person.distribution_count,
    combined: person.combined_count,
  };
}

export function presentWorkloadSummary(payload: WorkloadDutyAnalyticsPayload): WorkloadSummaryCard[] {
  return [
    {
      label: translateWithFallback("workloadDashboard.summary.totalInvigilation", "Invigilation"),
      value: String(payload.summary.total_invigilation_duties),
      hint: translateWithFallback("workloadDashboard.summary.totalPeople", "People"),
    },
    {
      label: translateWithFallback("workloadDashboard.summary.totalDistribution", "Paper distribution"),
      value: String(payload.summary.total_distribution_duties),
      hint: translateWithFallback("workloadDashboard.summary.combined", "Combined"),
    },
    {
      label: translateWithFallback("workloadDashboard.summary.combined", "Combined"),
      value: String(payload.summary.total_combined_duties),
      hint: translateWithFallback("workloadDashboard.summary.averagePerPerson", "Average per person"),
    },
    {
      label: translateWithFallback("workloadDashboard.summary.averagePerPerson", "Average per person"),
      value: payload.summary.average_duties_per_person.toFixed(2),
      hint: translateWithFallback("workloadDashboard.summary.overloadedCount", "Overloaded staff"),
    },
    {
      label: translateWithFallback("workloadDashboard.summary.overloadedCount", "Overloaded staff"),
      value: String(payload.fairness.overloaded_people.length),
      hint: translateWithFallback("workloadDashboard.summary.fairnessScore", "Fairness"),
    },
    {
      label: translateWithFallback("workloadDashboard.summary.fairnessScore", "Fairness score"),
      value: payload.summary.imbalance_score.toFixed(2),
      hint: translateWithFallback("workloadDashboard.recommendations.balanceWorkload", "Rebalance duties"),
    },
  ];
}
