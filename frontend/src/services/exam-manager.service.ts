import type { UserOut } from "@/types/api";
import { del, get, post, put } from "./api";

export interface OwnershipAssignmentItem {
  id?: number;
  section_id?: number;
  exam_type?: "midterm" | "final";
  manager_id?: number | null;
  manager_name?: string | null;
  confirmed?: boolean;
  confirmed_at?: string | null;
  assignment_source?: "auto" | "manual";
  assignment_status?: "auto_assigned" | "manual_assigned" | "needs_attention" | "pending";
  note?: string | null;
}

export interface ExamManagerOverviewItem {
  section_id: number;
  course_id?: string | null;
  course_name?: string | null;
  section_no?: string | null;
  department?: string | null;
  imported_teachers: Array<Pick<UserOut, "id" | "full_name" | "email" | "dept_code">>;
  main_teacher?: string | null;
  num_students?: number;
  teaching_room?: string | null;
  midterm?: OwnershipAssignmentItem | null;
  final?: OwnershipAssignmentItem | null;
  both_ok?: boolean;
  needs_attention?: boolean;
}

export interface ExamManagerOverviewResponse {
  semester: string;
  academic_year: string;
  total: number;
  assigned: number;
  unassigned: number;
  ready_count: number;
  needs_attention_count: number;
  auto_assigned_count: number;
  manual_assigned_count: number;
  pct_complete: number;
  sections: ExamManagerOverviewItem[];
}

export interface OwnershipUpdatePayload {
  midterm_manager_id?: number | null;
  final_manager_id?: number | null;
  note?: string | null;
}

export interface MyExamSectionsResponse {
  sections: Array<Record<string, unknown>>;
  pending_confirm: Array<Record<string, unknown>>;
}

export function getExamManagerOverview(query?: Record<string, string | boolean | number | null | undefined>) {
  return get<ExamManagerOverviewResponse>("/exam-manager/overview", { query });
}

export function updateSectionOwnership(sectionId: number, body: OwnershipUpdatePayload) {
  return put(`/exam-manager/section/${sectionId}/ownership`, body);
}

export function getPendingExamManagerAssignments() {
  return get<OwnershipAssignmentItem[]>("/exam-manager/pending");
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
