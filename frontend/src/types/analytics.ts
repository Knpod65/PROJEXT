// Only types that model the analytics contract layer.
// No dashboard components here.
export type CategoryKey =
  | "optimization"
  | "schedule"
  | "workload"
  | "room_utilization"
  | "governance"
  | "publication"
  | "print"
  | "pickup_qr"
  | "student_conflict"
  | "faculty_operations"
  | "pdpa_compliance";

export interface MetricDefinition {
  metric_code: string;
  name: string;
  category: CategoryKey;
  description: string;
  unit: string;
  aggregation: "count" | "sum" | "avg" | "ratio" | "score";
  pdpa_level: "public" | "internal" | "confidential" | "restricted";
}

export interface MetricValueResponse {
  metric_code: string;
  value: number;
  computed_at: string;
  period_key: string;
  scope?: Record<string, unknown>;
}

export interface ExecutiveDashboardSummary {
  overall_health_score: number;
  risk_band: "green" | "amber" | "red";
  optimization_quality_avg: number;
  governance_blocker_count: number;
  publication_ready_count: number;
  workload_balance_score: number;
  room_utilization_score: number;
  pdpa_alert_count: number;
  top_risks: Array<{ risk: string; severity: string; category: string }>;
  recommended_actions: Array<{ action: string; owner: string; priority: string }>;
}

export interface IntegrationContractField {
  source_field: string;
  target_field: string;
}

export interface IntegrationContract {
  contract_id: string;
  source_system: string;
  target_system: string;
  version: string;
  status: "active" | "deprecated" | "draft";
  last_validated_at: string;
  fields: IntegrationContractField[];
}