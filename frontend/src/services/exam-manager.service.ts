import { del, get, post, put } from "./api";

export interface ExamManagerOverviewItem {
  id: number;
  section_id?: number;
  course_id?: string | null;
  course_name?: string | null;
  section_no?: string | null;
  teacher_name?: string | null;
  manager_name?: string | null;
  manager_id?: number | null;
  confirmed?: boolean;
  needs_exam_manager?: boolean;
}

export interface ExamManagerOverviewResponse {
  semester: string;
  academic_year: string;
  total: number;
  assigned: number;
  unassigned: number;
  pct_complete: number;
  sections: ExamManagerOverviewItem[];
}

export interface MyExamSectionsResponse {
  sections: Array<Record<string, unknown>>;
  pending_confirm: Array<Record<string, unknown>>;
}

export function getExamManagerOverview() {
  return get<ExamManagerOverviewResponse>("/exam-manager/overview");
}

export function getPendingExamManagerAssignments() {
  return get<ExamManagerOverviewItem[]>("/exam-manager/pending");
}

export function getMyExamManagerSections() {
  return get<MyExamSectionsResponse>("/exam-manager/my-sections");
}

export function proposeExamManager(body: Record<string, unknown>) {
  return post("/exam-manager/propose", body);
}

export function confirmExamManager(managerId: number) {
  return post(`/exam-manager/${managerId}/confirm`);
}

export function reassignExamManager(managerId: number, body: Record<string, unknown>) {
  return put(`/exam-manager/${managerId}/reassign`, body);
}

export function deleteExamManager(managerId: number) {
  return del<{ success: boolean }>(`/exam-manager/${managerId}`);
}
