export type UserRole =
  | "admin"
  | "esq_head"
  | "secretary"
  | "dept_supervisor"
  | "staff"
  | "teacher"
  | "student"
  | "print_shop";

export type RoleSelectionValue = UserRole | "governance";

export interface UserMe {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  role: UserRole;
  active_role: UserRole;
  view_as_role: UserRole | null;
  effective_role: UserRole;
  available_roles?: UserRole[] | null;
}

export interface UserOut {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  role: UserRole;
  department?: string | null;
  dept_code?: string | null;
  is_active: boolean;
  created_at?: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  message?: string;
  user: UserMe;
}

export interface CourseOut {
  id: number;
  course_id: string;
  course_name_th: string | null;
  course_name_en?: string | null;
  credits?: number;
  department?: string | null;
  academic_group?: string | null;
  academic_group_label?: string | null;
}

export interface RoomOut {
  id: number;
  room_name: string;
  building?: string | null;
  capacity: number;
  is_active?: boolean;
}

export interface SupervisionOut {
  id: number;
  user?: UserOut | null;
  role_in_exam?: string;
  slot_order: number;
  compensation?: number;
  confirmed: boolean;
  is_swapped?: boolean;
  is_emergency_sub?: boolean;
  swap_requested?: boolean;
}

export interface ScheduleOut {
  id: number;
  exam_date: string;
  exam_time: string;
  exam_type?: string;
  status: string;
  num_pages: number;
  total_sheets: number;
  paper_distributor?: string | null;
  notes?: string | null;
  room?: RoomOut | null;
  supervisions: SupervisionOut[];
}

export interface SectionOut {
  id: number;
  section_no: string;
  num_students: number;
  is_co_exam: boolean;
  co_group_id?: string | null;
  semester: string;
  academic_year: string;
  academic_group?: string | null;
  academic_group_label?: string | null;
  course?: CourseOut | null;
  teacher?: UserOut | null;
  teaching_room?: RoomOut | null;
  schedules?: ScheduleOut[];
}

export interface ScheduleWithSection extends ScheduleOut {
  section?: SectionOut | null;
}

export interface DashboardStats {
  total_sections: number;
  total_students: number;
  total_sheets: number;
  total_teachers: number;
  scheduled_sections: number;
  unscheduled_sections: number;
  rooms_in_use: number;
  copy_cost: number;
  recent_logs: Array<{
    id: number;
    action: string;
    actor: string;
    table_name?: string | null;
    record_id?: number | null;
    timestamp?: string | null;
  }>;
}

export interface DashboardAnalytics {
  submission_status: Record<string, number>;
  teacher_stats: { submitted: number; not_submitted: number };
  supervision_stats: { confirmed: number; pending: number };
  swap_status: Record<string, number>;
  copy_per_room: Array<{ room: string; sheets: number; cost: number }>;
  checkin_by_date: Array<{ date: string; count: number }>;
}

export interface SubmissionListItem {
  id: number;
  section_id: number;
  course_id: string | null;
  course_name: string | null;
  section_no: string | null;
  status: string;
  version?: number;
  exam_type_choice?: string | null;
  has_uploaded_pdf?: boolean;
  submitted_at?: string | null;
  submitter?: string | null;
}

export interface SubmissionDetail {
  exists: boolean;
  id?: number;
  section_id: number;
  status?: string;
  version?: number;
  date_confirmed?: boolean;
  exam_type_choice?: string | null;
  answer_formats?: string[] | null;
  a4_pages_count?: number;
  has_uploaded_pdf?: boolean;
  no_cover_page_confirmed?: boolean;
  is_shared_exam?: boolean;
  shared_with_sections?: number[] | null;
  submitted_at?: string | null;
  approved_at?: string | null;
  rejected_reason?: string | null;
  admin_note?: string | null;
  course_name?: string | null;
  versions?: Array<{ version: number; created_at: string; reason: string }>;
}

export interface SubmissionMessage {
  id: number;
  sender_name?: string;
  message: string;
  created_at: string;
}

export interface SwapItem {
  id: number;
  status: string;
  is_requester?: boolean;
  is_direct_handoff?: boolean;
  requester_name?: string | null;
  target_name?: string | null;
  message?: string | null;
  reject_reason?: string | null;
  created_at?: string | null;
  responded_at?: string | null;
  my_shift?: {
    date?: string | null;
    time?: string | null;
    course?: string | null;
    room?: string | null;
    section_no?: string | null;
    supervision_id?: number | null;
  };
  their_shift?: {
    date?: string | null;
    time?: string | null;
    course?: string | null;
    room?: string | null;
    section_no?: string | null;
  };
}

export interface CheckinEventItem {
  id: number;
  user?: string | null;
  checkin_type: string;
  checked_in_at?: string | null;
  students_present?: number | null;
  late_count?: number | null;
  absent_count?: number;
  notes?: string | null;
  confirmed: boolean;
  confirmed_by_all?: boolean;
  confirmations?: Record<string, string>;
}

export interface PickupScheduleSummary {
  schedule_id?: number;
  id?: number;
  course_code?: string | null;
  course_name?: string | null;
  section_no?: string | null;
  room_name?: string | null;
  exam_date?: string | null;
  exam_time?: string | null;
  teacher_name?: string | null;
  status?: string | null;
}

export interface PickupAssignment {
  user_id: number;
  full_name: string;
  role: string;
}

export interface PickupQrSummary {
  id: number;
  schedule_id: number;
  version: number;
  qr_type: string;
  is_active: boolean;
  confirmed_at?: string | null;
  generated_at?: string | null;
  valid_from?: string | null;
  valid_until?: string | null;
  course_code?: string | null;
  section_no?: string | null;
  exam_date?: string | null;
  start_time?: string | null;
  end_time?: string | null;
  qr_value?: string | null;
}

export interface PickupQrStatusResponse {
  schedule: PickupScheduleSummary;
  assignments: PickupAssignment[];
  active_qr?: PickupQrSummary | null;
  latest_qr?: PickupQrSummary | null;
  has_pending_regeneration: boolean;
}

export interface PickupQrMutationResponse extends PickupQrStatusResponse {
  pending_qr?: PickupQrSummary | null;
}

export interface PickupScanResult {
  success: boolean;
  status: string;
  message: string;
  schedule: PickupScheduleSummary;
  assignment?: PickupAssignment | null;
  checked_in_at?: string | null;
  qr_version?: number | null;
}

export interface PickupMonitorRow {
  schedule_id: number;
  date: string;
  time: string;
  course_code?: string | null;
  course_name?: string | null;
  section_no?: string | null;
  room_name?: string | null;
  assigned_person: string;
  role: string;
  checkin_status: string;
  checkin_time?: string | null;
  latest_message?: string | null;
  active_qr_version?: number | null;
  latest_qr_version?: number | null;
  has_pending_regeneration: boolean;
  action_details?: {
    checkin_id?: number | null;
    duplicate_attempt?: boolean;
  };
}

export interface PublicStudentSchedule {
  student_id: string;
  full_name: string;
  major?: string | null;
  faculty?: string | null;
  term_label?: string | null;
  total_courses: number;
  exams: Array<{
    course_id: string;
    course_name: string;
    section_no: string;
    teacher: string;
    exam_date?: string | null;
    exam_time?: string | null;
    room?: string | null;
    seat_group?: string | null;
    status: string;
    has_schedule: boolean;
  }>;
}

export interface PeriodItem {
  id: number;
  academic_year: string;
  semester: string;
  exam_type: string;
  label: string;
  is_active: boolean;
  stats?: Record<string, unknown>;
}

export type TermLifecycleStatus = "draft" | "active" | "archived" | "locked";

export interface TermLifecyclePreviewItem {
  id: number;
  academic_year: string;
  semester: string;
  exam_type: string;
  label?: string | null;
  is_active: boolean;
  lifecycle_status: TermLifecycleStatus;
  is_historical: boolean;
  is_editable: boolean;
  is_read_only: boolean;
  status_summary: string;
  preview_summary: string;
  archived_at?: string | null;
  locked_at?: string | null;
  created_at?: string | null;
}

export interface TermSettingsPreview {
  current_active_term?: TermLifecyclePreviewItem | null;
  latest_term?: TermLifecyclePreviewItem | null;
  latest_historical_term?: TermLifecyclePreviewItem | null;
  selected_term?: TermLifecyclePreviewItem | null;
  available_terms: TermLifecyclePreviewItem[];
  default_preview_term_id?: number | null;
  selected_term_status?: TermLifecycleStatus | null;
  selected_term_editable: boolean;
  selected_term_read_only: boolean;
  plain_language_summary: string;
  historical_visibility_summary: string;
}

export type ExamFileRetentionMode = "manual" | "semester_end" | "academic_year_end" | "years";

export interface RetentionPolicyPlainLanguage {
  exam_file_retention_summary: string;
  archive_summary: string;
  destruction_summary: string;
  historical_visibility_summary: string;
}

export interface RetentionPolicy {
  exam_file_retention_mode: ExamFileRetentionMode;
  exam_file_retention_years?: number | null;
  exam_file_destroy_requires_approval: boolean;
  exam_file_archive_before_destroy: boolean;
  retain_import_audit_logs_years: number;
  retain_import_raw_files: boolean;
  parsed_snapshot_storage: string;
  historical_term_data_retained_indefinitely: boolean;
  plain_language: RetentionPolicyPlainLanguage;
}

export interface RetentionPolicyUpdateInput {
  exam_file_retention_mode: ExamFileRetentionMode;
  exam_file_retention_years?: number | null;
  exam_file_destroy_requires_approval: boolean;
  exam_file_archive_before_destroy: boolean;
  retain_import_audit_logs_years: number;
  retain_import_raw_files: boolean;
  historical_term_data_retained_indefinitely: boolean;
}

export interface PeriodCloseResponse {
  success: boolean;
  period_id: number;
  previous_lifecycle_status?: TermLifecycleStatus | null;
  new_lifecycle_status?: TermLifecycleStatus | null;
  locked_at?: string | null;
  plain_language_summary: string;
  blocking_reasons: string[];
}

export interface CoExamGroup {
  id: number;
  group_key: string;
  label: string;
  exam_date: string;
  exam_time: string;
  exam_type: string;
  total_students: number;
  members: Array<{
    section_id: number;
    course_id?: string | null;
    course_name?: string | null;
    section_no?: string | null;
    teacher_name?: string | null;
    num_students?: number | null;
  }>;
  member_count: number;
}

export interface CoExamSuggestion {
  type: string;
  label: string;
  exam_date: string;
  exam_time: string;
  exam_type: string;
  total_students: number;
  section_ids: number[];
  sections: Array<Record<string, unknown>>;
}

export interface ExternalExam {
  id: number;
  title?: string;
  organizer?: string | null;
  exam_date?: string;
  exam_time?: string;
  room_name?: string | null;
  num_students?: number;
  invigilators_needed?: number;
  notes?: string | null;
  status?: string;
  supervisions?: Array<{
    id: number;
    user_id?: number | null;
    full_name?: string | null;
    user_name?: string | null;
    slot_order?: number;
    confirmed?: boolean;
    assigned_by?: string | null;
  }>;
}

export interface ExternalExamAssignmentPreview {
  exam: ExternalExam;
  allocation_mode: "staff_only";
  required_count: number;
  assigned_count: number;
  needed_count: number;
  shortage_count: number;
  eligible_candidates: Array<{
    user_id: number;
    full_name: string | null;
    division?: string | null;
    unit?: string | null;
    total_load: number;
  }>;
  recommended_assignment: Array<{
    user_id: number;
    full_name: string | null;
    division?: string | null;
    unit?: string | null;
    total_load: number;
  }>;
  conflicted_staff: Array<{
    user_id: number;
    full_name: string | null;
    division?: string | null;
    unit?: string | null;
    total_load: number;
    reason: string;
    conflict_type?: string;
  }>;
  excluded_staff: Array<{
    user_id: number;
    full_name: string | null;
    division?: string | null;
    unit?: string | null;
    total_load: number;
    reason: string;
  }>;
  assigned_staff: Array<{
    user_id: number;
    full_name: string | null;
    division?: string | null;
    unit?: string | null;
    total_load: number;
  }>;
  fairness: {
    current_score: number;
    projected_score: number;
  };
  warnings: string[];
  note?: string;
}

export interface WorkflowSession {
  id?: number;
  exam_period_id?: number;
  status: string;
  baseline_saved?: boolean;
  round1?: {
    signatures: Array<{ order: number; user?: string | null; signed_at?: string | null }>;
    done: number;
    total: number;
    complete: boolean;
  };
  round2?: {
    signatures: Array<{ order: number; user?: string | null; signed_at?: string | null }>;
    done: number;
    total: number;
    complete: boolean;
  };
  next_signer_r1?: string | null;
  next_signer_r2?: string | null;
  message?: string;
}

export type WorkflowIssueType =
  | "no_invigilator_assigned"
  | "room_capacity_exceeded"
  | "high_student_invigilator_ratio"
  | "external_staff_shortage";

export interface WorkflowIssueItem {
  id: string;
  type: WorkflowIssueType;
  severity: "error" | "warning";
  scope: "internal" | "external";
  title: string;
  message: string;
  reference: string;
}

export interface SignerInfo {
  order: number;
  username: string;
  full_name: string;
  is_me: boolean;
}

export interface ImportSession {
  id: number;
  import_session_id?: number;
  import_type?: string;
  academic_year: string;
  semester: string;
  exam_type: string;
  imported_by?: string;
  started_at?: string | null;
  completed_at?: string | null;
  status?: string;
  total_rows?: number;
  valid_rows?: number;
  warning_rows?: number;
  error_rows?: number;
  imported_rows?: number;
  skipped_rows?: number;
  opencourse_rows: number;
  enrollment_rows: number;
  created_at?: string | null;
  last_updated?: string | null;
}

export interface ImportAuditIssueSummaryItem {
  code: string | null;
  message: string | null;
  count: number;
}

export interface ImportAuditSessionDetail {
  session: ImportSession;
  issue_summary: ImportAuditIssueSummaryItem[];
}

export interface ImportAuditRowLog {
  id: number;
  row_number: number;
  status: string;
  error_code?: string | null;
  error_message?: string | null;
  was_selected: boolean;
  was_imported: boolean;
  override_reason?: string | null;
  raw_data: Record<string, unknown>;
  raw_data_preview: string;
  created_at?: string | null;
}

export interface ImportAuditRowLogList {
  session_id: number;
  total_rows: number;
  rows: ImportAuditRowLog[];
}

export type ImportV2Type = "opencourse" | "personnel" | "employee" | "enrollment" | "room_capacity";
export type ImportV2OverridePolicy = "allowed" | "disallowed" | "requires_mapping";
export type ImportV2RowStatus = "valid" | "warning" | "error";

export interface ImportV2TermContext {
  academic_year?: string | null;
  semester?: string | null;
  exam_type?: string | null;
}

export interface ImportV2IssueSummaryItem {
  code: string;
  message: string;
  count: number;
}

export interface ImportV2OverrideRequestItem {
  row: number;
  reason: string;
}

export interface ImportV2ValidationRow {
  _row: number;
  status: ImportV2RowStatus;
  errors: string[];
  warnings: string[];
  error_codes: string[];
  warning_codes: string[];
  can_override: boolean;
  override_policy: ImportV2OverridePolicy;
  selected: boolean;
  override_required: boolean;
  override_reason?: string | null;
  historical_mode: boolean;
  import_term_context: ImportV2TermContext;
  data: Record<string, unknown>;
}

export interface ImportV2PreviewResponse {
  file_token: string;
  file_name: string;
  academic_year: string;
  semester: string;
  exam_type: string;
  total_rows: number;
  sample_rows: Array<Record<string, unknown>>;
}

export interface ImportV2ValidationResponse {
  total_rows: number;
  valid_count: number;
  warning_count: number;
  error_count: number;
  error_summary: ImportV2IssueSummaryItem[];
  warning_summary: ImportV2IssueSummaryItem[];
  rows: ImportV2ValidationRow[];
}

export interface ImportV2PrepareResponse {
  import_type: ImportV2Type;
  academic_year: string;
  semester: string;
  exam_type?: string | null;
  historical_mode: boolean;
  total_rows: number;
  selected_count: number;
  skipped_count: number;
  override_count: number;
  error_blocking_count: number;
  rows_preview: ImportV2ValidationRow[];
}

export interface ImportV2SessionPlan {
  import_type: ImportV2Type;
  academic_year: string;
  semester: string;
  exam_type?: string | null;
  historical_mode: boolean;
  source_filename?: string | null;
  confirmed_by: number;
  dry_run: boolean;
}

export interface ImportV2ConfirmCheckResponse {
  total_rows: number;
  selected_count: number;
  blocked_count: number;
  override_count: number;
  importable_count: number;
  non_importable_count: number;
  blocking_reasons: ImportV2IssueSummaryItem[];
  ready_for_execution: boolean;
  session_plan?: ImportV2SessionPlan | null;
}

export interface ImportV2ExecuteResponse {
  success: boolean;
  total_rows: number;
  imported_count: number;
  skipped_count: number;
  override_count: number;
  import_session_id: number;
  summary: Record<string, unknown>;
}

export interface CopyCountSummary {
  rows: Array<{
    course_id: string;
    course_name_th: string;
    section_no: string;
    num_students: number;
    num_pages: number;
    total_sheets: number;
    exam_date: string;
    exam_time?: string | null;
    room: string | null;
    print_duplex: boolean;
    print_staple: string;
    print_staple_page?: number | null;
    print_note?: string | null;
    a4_pages_count: number;
    answer_formats?: string[] | null;
    answer_paper_sheets: number;
    answer_paper_staple: boolean;
    answer_booklet_count: number;
    omr_sheet_count: number;
    scratch_paper_sheets: number;
    special_note?: string | null;
  }>;
  subtotal_exam: number;
  fraud_forms: number;
  grand_total: number;
  cost: number;
  sections_count: number;
}

export type PrintQueuePriority = "high" | "medium" | "standard";
export type PrintQueueStatus = "queued" | "processing" | "completed" | "dispatched" | "delivered";

export interface PrintQueueJob {
  id: number;
  submission_id: number | null;
  course_code: string;
  subject_name: string;
  section: string;
  room: string;
  exam_date: string | null;
  exam_time?: string | null;
  students: number;
  pages: number;
  total_sheets: number;
  priority: PrintQueuePriority;
  status: PrintQueueStatus;
  specs: string[];
  notes?: string | null;
  delivery_note?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  dispatched_at?: string | null;
  delivered_at?: string | null;
  created_at?: string | null;
  assigned_to?: string | null;
}

export interface OptimizerResult {
  success: boolean;
  sections_assigned: number;
  sections_total: number;
  fairness_score: number;
  violations: string[];
  details: Array<Record<string, unknown>>;
  paper_distribution_assigned?: number;
  paper_distribution_slots?: number;
  paper_distribution_unfilled?: number;
  paper_distribution_warnings?: string[];
}

export interface StaffAvailabilityMember {
  id: number;
  username: string;
  full_name: string | null;
  division?: string | null;
  unit?: string | null;
  department?: string | null;
  is_paper_distribution_candidate: boolean;
  excluded_reason?: string | null;
  availability_block_count: number;
  invigilation_count: number;
  paper_distribution_count: number;
  external_exam_count: number;
  total_workload: number;
}

export interface WorkloadSummaryRow {
  user_id: number;
  staff_name: string;
  department: string;
  invigilation_count: number;
  paper_distribution_count: number;
  external_exam_count: number;
  total_workload: number;
  historical_total_workload: number;
}

export interface WorkloadDetailRow {
  user_id: number;
  staff_name: string;
  department: string;
  duty_type: string;
  date: string;
  time: string;
  context_label: string;
  room?: string | null;
  workload_count: number;
}

export interface PaperDistributionAssignmentRow {
  id: number;
  user_id: number;
  staff_name: string;
  department: string;
  exam_date: string;
  exam_time: string;
  start_time?: string | null;
  end_time?: string | null;
  duty_type: string;
  workload_count: number;
  covered_schedule_count: number;
  covered_courses: string[];
  covered_rooms: string[];
  assignment_mode?: string | null;
  notes?: string | null;
}
