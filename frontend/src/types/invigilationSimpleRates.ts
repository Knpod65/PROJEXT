export type SimpleRateConfigurationStatus = "NOT_CONFIGURED" | "INCOMPLETE" | "CONFIGURED";
export type SimpleRateAmountStatus = "PENDING_CONFIGURATION" | "CONFIGURED";
export type SimpleRateDayScope = "WEEKDAY" | "WEEKEND";

export interface SimpleInvigilationRate {
  day_scope: SimpleRateDayScope;
  amount: number | string | null;
  amount_status: SimpleRateAmountStatus;
  rate_rule_id: number | null;
  saved_at: string | null;
}

export interface SimpleInvigilationRates {
  preview_only: boolean;
  payment_authorization_enabled: boolean;
  final_export_enabled: boolean;
  currency: "THB";
  payment_unit: "PER_SESSION";
  configuration_status: SimpleRateConfigurationStatus;
  weekday_rate: SimpleInvigilationRate;
  weekend_rate: SimpleInvigilationRate;
}

export interface SimpleInvigilationRatesPayload {
  weekday_amount: number;
  weekend_amount: number;
}

