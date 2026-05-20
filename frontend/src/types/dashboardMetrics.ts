/** OPS-DASH: Role-based significant metrics types. */

export type TrendDirection = "up" | "down" | "flat" | "unknown";
export type MetricSeverity = "good" | "info" | "warning" | "critical";
export type RiskBand = "green" | "amber" | "red" | "unknown";
export type PdpaLevel = "public" | "internal" | "confidential" | "restricted";

export interface DashboardMetric {
  metric_code: string;
  title_i18n_key: string;
  description_i18n_key: string;
  value: number | string;
  unit: string;
  trend: TrendDirection;
  trend_label_i18n_key: string;
  severity: MetricSeverity;
  why_it_matters_i18n_key: string;
  recommended_action_i18n_key: string;
  owner_role: string;
  drilldown_route: string | null;
  updated_at: string | null;
  pdpa_level: PdpaLevel;
}

export interface DashboardMetricGroup {
  group_code: string;
  title_i18n_key: string;
  description_i18n_key: string;
  metrics: DashboardMetric[];
  alerts: string[];
  recommended_actions: string[];
}

export interface DashboardAlert {
  alert_code: string;
  severity: string;
  title_i18n_key: string;
  body_i18n_key: string;
  metric_codes: string[];
  pdpa_level: PdpaLevel;
}

export interface DashboardRoleSummary {
  role: string;
  role_label_i18n_key: string;
  health_score: number | null;
  risk_band: RiskBand | null;
  key_metrics: DashboardMetric[];
  alerts: string[];
  recommended_actions: string[];
  last_updated: string | null;
}

export interface AdminIntelligenceDashboard {
  role: string;
  overall_health_score: number | null;
  overall_risk_band: string | null;
  last_computed_at: string | null;
  groups: DashboardMetricGroup[];
}

export interface RoleDashboardPayload {
  role: string;
  role_label_i18n_key: string;
  summary: DashboardRoleSummary;
  groups: DashboardMetricGroup[];
  unauthorized: boolean;
}

export interface OpsHealthPayload {
  groups: DashboardMetricGroup[];
  last_updated: string;
}

export interface PdpaHealthPayload {
  groups: DashboardMetricGroup[];
  last_updated: string;
}

export interface ExecDashboardPayload {
  overall_health_score: number;
  risk_band: string;
  optimization_quality_avg: number;
  governance_blocker_count: number;
  publication_ready_count: number;
  workload_balance_score: number;
  room_utilization_score: number;
  pdpa_alert_count: number;
  top_risks: { label_i18n_key: string; risk: string }[];
  recommended_actions: { label_i18n_key: string; route: string }[];
}
