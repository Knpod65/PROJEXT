export type UserRole =
  | "admin"
  | "esq_head"
  | "secretary"
  | "dept_supervisor"
  | "staff"
  | "teacher"
  | "student";

export interface UserMe {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  role: UserRole;
  view_as_role: UserRole | null;
  effective_role: UserRole;
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
  course?: CourseOut | null;
  teacher?: UserOut | null;
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

export interface PublicStudentSchedule {
  student_id: string;
  full_name: string;
  major?: string | null;
  faculty?: string | null;
  total_courses: number;
  exams: Array<{
    course_id: string;
    course_name: string;
    section_no: string;
    num_students: number;
    teacher: string;
    exam_date?: string | null;
    exam_time?: string | null;
    room?: string | null;
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
    user_name?: string | null;
    slot_order?: number;
    confirmed?: boolean;
  }>;
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

export interface SignerInfo {
  order: number;
  username: string;
  full_name: string;
  is_me: boolean;
}

export interface ImportSession {
  id: number;
  academic_year: string;
  semester: string;
  exam_type: string;
  opencourse_rows: number;
  enrollment_rows: number;
  created_at?: string | null;
  last_updated?: string | null;
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
    room: string;
  }>;
  subtotal_exam: number;
  fraud_forms: number;
  grand_total: number;
  cost: number;
  sections_count: number;
}

export interface OptimizerResult {
  success: boolean;
  sections_assigned: number;
  sections_total: number;
  fairness_score: number;
  violations: string[];
  details: Array<Record<string, unknown>>;
}
