export interface AdvanceBatchPreviewQuery {
  period_id?: number | null;
  academic_year?: string | null;
  semester?: string | null;
  exam_type?: string | null;
}

export interface AdvanceBatchPreviewSummary {
  preview_only: boolean;
  amount_calculation: string;
  amount_calculation_enabled: boolean;
  amount_status: string;
  preview_amount_enabled: boolean;
  preview_total_amount: number;
  preview_weekday_count: number;
  preview_weekend_count: number;
  total_rows: number;
  total_assignments: number;
  ready_for_batch_review: number;
  included_in_advance_batch: number;
  blocked_missing_assignment_data: number;
  blocked_duplicate_duty: number;
  blocked_rule_gap: number;
  blocked_rows: number;
  pending_rate_rule_count: number;
  missing_exam_date_count: number;
  invalid_exam_date_count: number;
  blocked_roster_amount_count: number;
  warning_count: number;
  payment_authorization_enabled: boolean;
  final_export_enabled: boolean;
}

export interface AdvanceBatchRosterRow {
  advance_batch_id: string | null;
  batch_period: string | null;
  academic_year: string | null;
  semester: string | null;
  exam_period: string | null;
  batch_status: string;
  duty_id: number | null;
  exam_id: number | null;
  schedule_id: number | null;
  course_code: string | null;
  course_title: string | null;
  section: string | null;
  exam_date: string | null;
  exam_date_calendar: string | null;
  normalized_exam_date: string | null;
  start_time: string | null;
  end_time: string | null;
  room_name: string | null;
  person_id: string | null;
  person_name: string | null;
  person_type: string | null;
  department: string | null;
  duty_role: string;
  advance_inclusion_status: string;
  inclusion_reason: string | null;
  blocked_reason: string | null;
  rate_rule_status: string;
  amount_status: string;
  amount_preview: number | null;
  rate_day_type: "WEEKDAY" | "WEEKEND" | "UNKNOWN";
  rate_source: string | null;
  payment_authorization_status: "NOT_AUTHORIZED_PREVIEW_ONLY";
  reconciliation_status: string;
  post_duty_evidence_status: string;
  absence_explanation_status: string;
  refund_offset_status: string;
  source_record_ref: string;
  audit_note: string;
  warnings: string[];
}

export interface AdvanceBatchPreviewPayload {
  summary: AdvanceBatchPreviewSummary;
  roster_rows: AdvanceBatchRosterRow[];
  blockers: string[];
  warnings: string[];
  rule_gaps: string[];
}
