import { translateWithFallback } from "@/i18n";
import type { WorkloadDutyAnalyticsPayload, WorkloadDutyAnalyticsPerson } from "@/types/workloadDutyAnalytics";

export interface WorkloadSummaryCard {
  label: string;
  value: string;
  hint: string;
  icon: string;
  tone: "accent" | "success" | "warning" | "neutral";
}

function safeNumber(value: any, fallback = 0): number {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

export function presentWorkloadPerson(person: WorkloadDutyAnalyticsPerson) {
  return {
    personId: person.person_id,
    displayName: person.display_name || translateWithFallback("common.unknown", "Unknown"),
    roleGroup: person.role_group
      ? translateWithFallback(`workloadDashboard.roleGroup.${person.role_group}`, person.role_group)
      : translateWithFallback("common.unknown", "Unknown"),
    invigilation: safeNumber(person.invigilation_count),
    distribution: safeNumber(person.distribution_count),
    combined: safeNumber(person.combined_count),
  };
}

export function presentWorkloadSummary(payload: WorkloadDutyAnalyticsPayload): WorkloadSummaryCard[] {
  return [
    {
      label: translateWithFallback("workloadDashboard.summary.totalInvigilation", "Invigilation"),
      value: String(payload.summary.total_invigilation_duties),
      hint: translateWithFallback("workloadDashboard.summary.totalInvigilationHint", "All live invigilation duties"),
      icon: "fact_check",
      tone: "accent",
    },
    {
      label: translateWithFallback("workloadDashboard.summary.totalDistribution", "Paper distribution"),
      value: String(payload.summary.total_distribution_duties),
      hint: translateWithFallback("workloadDashboard.summary.totalDistributionHint", "All paper-distribution duties"),
      icon: "inventory_2",
      tone: "neutral",
    },
    {
      label: translateWithFallback("workloadDashboard.summary.combined", "Combined"),
      value: String(payload.summary.total_combined_duties),
      hint: translateWithFallback("workloadDashboard.summary.combinedHint", "Invigilation and distribution combined"),
      icon: "work_history",
      tone: "accent",
    },
    {
      label: translateWithFallback("workloadDashboard.summary.averagePerPerson", "Average per person"),
      value: payload.summary.average_duties_per_person.toFixed(2),
      hint: translateWithFallback("workloadDashboard.summary.averageHint", "Combined duties divided by people"),
      icon: "groups",
      tone: "neutral",
    },
    {
      label: translateWithFallback("workloadDashboard.summary.overloadedCount", "Overloaded staff"),
      value: String(payload.fairness.overloaded_people.length),
      hint: translateWithFallback("workloadDashboard.summary.overloadedHint", "People above the current threshold"),
      icon: "warning",
      tone: payload.fairness.overloaded_people.length > 0 ? "warning" : "success",
    },
    {
      label: translateWithFallback("workloadDashboard.summary.fairnessScore", "Fairness score"),
      value: payload.summary.imbalance_score.toFixed(2),
      hint: translateWithFallback("workloadDashboard.summary.fairnessHint", "Lower imbalance indicates a fairer distribution"),
      icon: "balance",
      tone: payload.summary.imbalance_score > 0 ? "warning" : "success",
    },
  ];
}

export function hasWorkloadAnalyticsResults(payload: WorkloadDutyAnalyticsPayload) {
  return (
    payload.by_person.length > 0 ||
    payload.daily_series.length > 0 ||
    payload.time_slot_series.length > 0 ||
    payload.fairness.overloaded_people.length > 0 ||
    payload.fairness.underloaded_people.length > 0
  );
}
