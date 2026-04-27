import { get, put } from "@/services/api";

export type HistoricalScheduleVersion = "final_adjusted" | "optimized_baseline";

export interface HistoricalBatchSummary {
  id: number;
  version_kind: HistoricalScheduleVersion;
  source_label: string;
  source_filename: string;
  semester: string;
  academic_year: string;
  exam_type: string;
  room_opening_start_username: string | null;
  row_count: number;
  manual_review_count: number;
  imported_at: string | null;
  parse_log: string[];
}

export interface HistoricalScheduleOverview {
  term: {
    semester: string;
    academic_year: string;
    exam_type: string;
  };
  room_opening_start_username: string;
  room_opening_candidates: Array<{
    id: number;
    username: string;
    full_name: string;
  }>;
  final_adjusted_batch: HistoricalBatchSummary | null;
  optimized_baseline_batch: HistoricalBatchSummary | null;
  comparison_count: number;
}

export interface HistoricalInvigilatorRow {
  display_name: string;
  role_kind: string | null;
  user_id: number | null;
}

export interface HistoricalScheduleRow {
  id: number;
  exam_date: string;
  exam_time: string;
  course_code: string;
  section_no: string;
  instructor_name: string;
  student_count: number;
  room_name: string | null;
  invigilators_raw: string | null;
  distribution_raw: string | null;
  paper_distribution_staff_name: string | null;
  room_opening_staff_name: string | null;
  parse_flags: string[];
  invigilators: HistoricalInvigilatorRow[];
}

export interface HistoricalDistributionRow {
  id: number;
  exam_date: string;
  exam_time: string;
  paper_distribution_staff_name: string | null;
  room_opening_staff_name: string | null;
  paper_distribution_user_id: number | null;
  room_opening_user_id: number | null;
  raw_value: string | null;
  source_mode: string;
  covered_courses: string[];
  covered_rooms: string[];
  covered_row_count: number;
  counted_or_not_counted: {
    paper_distribution: boolean;
    room_opening: boolean;
  };
  notes: string | null;
}

export interface HistoricalWorkloadAssignmentRow {
  person_name: string;
  user_id: number | null;
  duty_type: "INVIGILATION" | "PAPER_DISTRIBUTION" | "ROOM_OPENING";
  date: string;
  time_slot: string;
  courses_covered: string[];
  rooms: string[];
  workload_count: number;
  counted_or_not_counted: boolean;
  source_file: string;
  version_kind: HistoricalScheduleVersion;
  role_kind: string | null;
}

export interface HistoricalWorkloadSummaryRow {
  person_name: string;
  user_id: number | null;
  invigilation_count: number;
  paper_distribution_count: number;
  room_opening_count: number;
  total_counted_workload: number;
  assignments: HistoricalWorkloadAssignmentRow[];
}

export interface HistoricalComparisonRow {
  key: string;
  status: string;
  course_code: string;
  section_no: string;
  exam_date: string;
  exam_time: string;
  changes: string[];
  baseline: Record<string, string | number | null> | null;
  final: Record<string, string | number | null> | null;
}

export function getHistoricalScheduleOverview() {
  return get<HistoricalScheduleOverview>("/historical-schedules/overview");
}

export function getHistoricalScheduleRows(version_kind: HistoricalScheduleVersion) {
  return get<{ batch: HistoricalBatchSummary; rows: HistoricalScheduleRow[] }>("/historical-schedules/rows", {
    query: { version_kind },
  });
}

export function getHistoricalDistributionRows(version_kind: HistoricalScheduleVersion) {
  return get<{ batch: HistoricalBatchSummary; rows: HistoricalDistributionRow[] }>("/historical-schedules/distribution", {
    query: { version_kind },
  });
}

export function getHistoricalWorkload(version_kind: HistoricalScheduleVersion) {
  return get<{
    batch: HistoricalBatchSummary;
    summary: HistoricalWorkloadSummaryRow[];
    rows: HistoricalWorkloadAssignmentRow[];
  }>("/historical-schedules/workload", {
    query: { version_kind },
  });
}

export function getHistoricalComparison() {
  return get<{
    baseline_batch: HistoricalBatchSummary;
    final_batch: HistoricalBatchSummary;
    count: number;
    rows: HistoricalComparisonRow[];
  }>("/historical-schedules/comparison");
}

export function updateHistoricalRoomOpeningStart(username: string) {
  return put<{ username: string }>("/historical-schedules/room-opening-start", { username });
}

export function buildHistoricalComparisonCsvUrl() {
  return "/api/historical-schedules/export/comparison-csv";
}

export function buildHistoricalWorkloadCsvUrl(version_kind: HistoricalScheduleVersion) {
  return `/api/historical-schedules/export/workload-csv?version_kind=${encodeURIComponent(version_kind)}`;
}
