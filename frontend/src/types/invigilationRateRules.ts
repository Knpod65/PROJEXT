export type InvigilationPaymentUnit = "PER_SESSION";
export type InvigilationRateRuleStatus = "DRAFT" | "ACTIVE" | "ARCHIVED";

export interface InvigilationRateRule {
  rate_rule_id: number;
  rate_name: string;
  payment_unit: InvigilationPaymentUnit;
  rate_amount: string | number;
  currency: string;
  role_scope: string;
  person_type_scope: string;
  effective_from: string | null;
  effective_to: string | null;
  status: InvigilationRateRuleStatus;
  created_by: number | null;
  created_at: string | null;
  updated_by: number | null;
  updated_at: string | null;
  activated_by: number | null;
  activated_at: string | null;
  archived_by: number | null;
  archived_at: string | null;
  note: string | null;
  preview_only: boolean;
  payment_authorization_enabled: boolean;
  final_export_enabled: boolean;
}

export interface InvigilationRateRulePayload {
  rate_name: string;
  payment_unit: InvigilationPaymentUnit;
  rate_amount: string;
  currency: string;
  role_scope: string;
  person_type_scope: string;
  effective_from?: string | null;
  effective_to?: string | null;
  note?: string | null;
}

export interface InvigilationRateRuleListResponse {
  rate_rules: InvigilationRateRule[];
  preview_only: boolean;
  payment_authorization_enabled: boolean;
  final_export_enabled: boolean;
}

export interface InvigilationRateRuleMutationResponse {
  rate_rule: InvigilationRateRule;
  preview_only: boolean;
  payment_authorization_enabled: boolean;
  final_export_enabled: boolean;
}

