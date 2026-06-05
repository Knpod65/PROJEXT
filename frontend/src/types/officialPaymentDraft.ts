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
  weekday_rate: number;
  weekend_rate: number;
  rate_scope: string;
  paper_distribution_source_status: string;
}

export interface OfficialPaymentDraftRow {
  exam_date: string;
  normalized_exam_date: string | null;
  time_slot: string;
  start_time: string | null;
  end_time: string | null;
  day_type: "WEEKDAY" | "WEEKEND" | "UNKNOWN";
  rate_amount: number;
  invigilation_committee_count: number;
  invigilation_compensation_amount: number;
  paper_distribution_committee_count: number;
  paper_distribution_compensation_amount: number;
  total_compensation_amount: number;
  source_notes: string[];
  warnings: string[];
}

export interface OfficialPaymentDraftTotals {
  invigilation_committee_count: number;
  invigilation_compensation_amount: number;
  paper_distribution_committee_count: number;
  paper_distribution_compensation_amount: number;
  grand_total_amount: number;
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
