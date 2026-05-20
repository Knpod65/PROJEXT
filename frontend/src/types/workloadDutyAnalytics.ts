export type DutyType = "invigilation" | "paper_distribution" | "combined" | "all";
export type WorkloadRoleGroup = "all" | "admin" | "staff" | "supervisor" | "teacher";

export interface WorkloadDutyAnalyticsFilters {
  semester: string | null;
  academic_year: string | null;
  period_id: number | null;
  exam_type: string | null;
  role_group: WorkloadRoleGroup;
  person_id: string | null;
  duty_type: DutyType;
}

export interface WorkloadDutyAnalyticsPerson {
  person_id: string;
  display_name: string;
  role_group: WorkloadRoleGroup;
  invigilation_count: number;
  distribution_count: number;
  combined_count: number;
}

export interface WorkloadDutyAnalyticsDailyPoint {
  date: string;
  invigilation_count: number;
  distribution_count: number;
  combined_count: number;
  cumulative_invigilation: number;
  cumulative_distribution: number;
  cumulative_combined: number;
}

export interface WorkloadDutyAnalyticsTimeSlotPoint {
  time_slot: string;
  invigilation_count: number;
  distribution_count: number;
  combined_count: number;
}

export interface WorkloadDutyAnalyticsSummary {
  total_people: number;
  total_invigilation_duties: number;
  total_distribution_duties: number;
  total_combined_duties: number;
  average_duties_per_person: number;
  max_duties: number;
  imbalance_score: number;
}

export interface WorkloadDutyAnalyticsFairness {
  imbalance_score: number;
  overloaded_people: WorkloadDutyAnalyticsPerson[];
  underloaded_people: WorkloadDutyAnalyticsPerson[];
  risk_band: "good" | "info" | "warning" | "critical";
}

export interface WorkloadDutyAnalyticsPayload {
  filters: WorkloadDutyAnalyticsFilters;
  summary: WorkloadDutyAnalyticsSummary;
  by_person: WorkloadDutyAnalyticsPerson[];
  daily_series: WorkloadDutyAnalyticsDailyPoint[];
  time_slot_series: WorkloadDutyAnalyticsTimeSlotPoint[];
  fairness: WorkloadDutyAnalyticsFairness;
}
