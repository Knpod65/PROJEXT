export interface OfficialPaymentDraftManualPaperRow {
  exam_date: string;
  exam_time?: string | null;
  start_time?: string | null;
  end_time?: string | null;
  committee_count: number;
  notes?: string | null;
}

export interface OfficialPaymentDraftRequest {
  period_id?: number | null;
  academic_year?: string | null;
  semester?: string | null;
  exam_type?: string | null;
  paper_distribution_rows: OfficialPaymentDraftManualPaperRow[];
}

export interface OfficialPaymentDraftMetadata {
  academic_year: string | null;
  semester: string | null;
  exam_type: string | null;
  term_label: string;
  document_status: "DRAFT_NOT_AUTHORIZED";
  rate_source: string;
  weekday_rate: number | null;
  weekend_rate: number | null;
  rate_scope: string;
  paper_distribution_source_status: string;
  settings_source_status: "CONFIGURED" | "PENDING_SETTINGS" | "INCOMPLETE_SETTINGS";
  settings_term: string | null;
  settings_status: string | null;
  settings_weekday_rate: number | null;
  settings_weekend_rate: number | null;
  currency: string;
  payment_unit: string;
  paper_distribution_responsible_group: string | null;
  paper_distribution_responsible_person: string | null;
  calculation_status:
    | "CALCULATED_FROM_SETTINGS"
    | "BLOCKED_PENDING_SETTINGS"
    | "BLOCKED_INCOMPLETE_SETTINGS";
  settings_issues: string[];
}

export interface OfficialPaymentDraftRow {
  exam_date: string;
  normalized_exam_date: string | null;
  time_slot: string;
  start_time: string | null;
  end_time: string | null;
  day_type: "WEEKDAY" | "WEEKEND" | "UNKNOWN";
  rate_amount: number | null;
  invigilation_committee_count: number;
  invigilation_compensation_amount: number | null;
  paper_distribution_committee_count: number;
  paper_distribution_compensation_amount: number | null;
  total_compensation_amount: number | null;
  source_notes: string[];
  warnings: string[];
}

export interface OfficialPaymentDraftTotals {
  invigilation_committee_count: number;
  invigilation_compensation_amount: number | null;
  paper_distribution_committee_count: number;
  paper_distribution_compensation_amount: number | null;
  grand_total_amount: number | null;
  row_count: number;
}

export interface OfficialPaymentDraftResponse {
  metadata: OfficialPaymentDraftMetadata;
  rows: OfficialPaymentDraftRow[];
  totals: OfficialPaymentDraftTotals;
  warnings: string[];
  draft_only: boolean;
  payment_authorization_enabled: boolean;
  final_export_enabled: boolean;
  supervisor_finance_review_required: boolean;
}
