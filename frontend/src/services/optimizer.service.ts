import { del, get, post } from "./api";

export interface UnavailabilityRecord {
  id: number;
  user_id: number;
  full_name: string | null;
  division?: string | null;
  unit?: string | null;
  block_date: string;
  block_time: string | null;
  start_time?: string | null;
  end_time?: string | null;
  all_day: boolean;
  reason: string | null;
}

export interface StaffPoolMember {
  id: number;
  full_name: string | null;
  username: string;
  role: string;
  is_esq_staff: boolean;
  special_role: string | null;
}

export interface OptimizeSessionData {
  id?: number;
  status: string;
  baseline_saved?: boolean;
  round1?: {
    signatures: Array<{ order: number; username: string; signed_at: string | null }>;
    done: number;
    total: number;
    complete: boolean;
  };
  round2?: {
    signatures: Array<{ order: number; username: string; signed_at: string | null }>;
    done: number;
    total: number;
    complete: boolean;
  };
  next_signer_r1?: string | null;
  next_signer_r2?: string | null;
  message?: string;
}

export interface OptimizerResult {
  sections_assigned: number;
  sections_total: number;
  fairness_score: number;
  violations: string[];
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

export interface StaffAvailabilityListResponse {
  rows: StaffAvailabilityMember[];
  count: number;
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

export interface WorkloadReportResponse {
  summary: WorkloadSummaryRow[];
  details: WorkloadDetailRow[];
  fairness_score: number;
  total_assignments: number;
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

export interface PaperDistributionAssignmentResponse {
  rows: PaperDistributionAssignmentRow[];
  count: number;
}

export function getSession() {
  return get<OptimizeSessionData>("/workflow/session/");
}

export function initSession() {
  return post<OptimizeSessionData>("/workflow/session/init");
}

export function signSession(round: 1 | 2) {
  return post<OptimizeSessionData>(`/workflow/session/sign?round=${round}`);
}

export function getUnavailability() {
  return get<UnavailabilityRecord[]>("/workflow/unavailability/");
}

export function addUnavailability(data: {
  user_id: number;
  block_date: string;
  block_time?: string;
  start_time?: string;
  end_time?: string;
  reason?: string;
}) {
  return post<{ id: number; status: string }>("/workflow/unavailability/", data);
}

export function deleteUnavailability(id: number) {
  return del<{ status: string }>(`/workflow/unavailability/${id}`);
}

export function getStaffPool() {
  return get<{ supervisors: StaffPoolMember[]; room_keepers: StaffPoolMember[] }>(
    "/workflow/staff-pool",
  );
}

export function getStaffAvailabilityStaff() {
  return get<StaffAvailabilityListResponse>("/workflow/staff-availability/staff");
}

export function getStaffWorkloadReport() {
  return get<WorkloadReportResponse>("/workflow/staff-workload");
}

export function getPaperDistributionAssignments() {
  return get<PaperDistributionAssignmentResponse>("/workflow/paper-distribution/assignments");
}

export function runOptimizer(body: {
  semester: string;
  academic_year: string;
  exam_type: string;
}) {
  return post<OptimizerResult>("/schedule/optimize", body);
}
