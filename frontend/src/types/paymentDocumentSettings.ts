export type PaymentDocumentSettingsStatus =
  | "DRAFT_CONFIG"
  | "ACTIVE_FOR_DRAFT_PREVIEW"
  | "ARCHIVED";

export type PaymentDocumentSettingsConfigurationStatus =
  | "PENDING_CONFIGURATION"
  | "CONFIGURED";

export interface PaymentDocumentSettings {
  settings_id: string;
  term: string;
  weekday_rate: number | string | null;
  weekend_rate: number | string | null;
  currency: "THB";
  payment_unit: "PER_PERSON_SESSION";
  paper_distribution_responsible_group: string;
  paper_distribution_responsible_person: string | null;
  status: PaymentDocumentSettingsStatus;
  configuration_status: PaymentDocumentSettingsConfigurationStatus;
  effective_from: string | null;
  effective_to: string | null;
  note: string | null;
  updated_by: number | null;
  updated_at: string | null;
  payment_authorization_enabled: false;
  final_export_enabled: false;
}

export interface PaymentDocumentSettingsPayload {
  term: string;
  weekday_rate: number;
  weekend_rate: number;
  currency: "THB";
  payment_unit: "PER_PERSON_SESSION";
  paper_distribution_responsible_group: string;
  paper_distribution_responsible_person?: string | null;
  status: PaymentDocumentSettingsStatus;
  effective_from?: string | null;
  effective_to?: string | null;
  note?: string | null;
}

export interface PaymentDocumentSettingsListResponse {
  settings: PaymentDocumentSettings[];
  payment_authorization_enabled: false;
  final_export_enabled: false;
}
