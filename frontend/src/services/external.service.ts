import type { ExternalExam, ExternalExamAssignmentPreview } from "@/types/api";
import { del, get, post, put } from "./api";

export function listExternalExams() {
  return get<ExternalExam[]>("/external");
}

export function createExternalExam(body: Record<string, unknown>) {
  return post<ExternalExam>("/external", body);
}

export function updateExternalExam(examId: number, body: Record<string, unknown>) {
  return put<ExternalExam>(`/external/${examId}`, body);
}

export function deleteExternalExam(examId: number) {
  return del<{ status: string }>(`/external/${examId}`);
}

export function previewExternalExamAssignment(examId: number) {
  return post<ExternalExamAssignmentPreview>(`/external/${examId}/assign-preview`);
}

export function applyExternalExamAssignment(examId: number, compensation?: number) {
  return post<{
    status: string;
    assigned: Array<{ user_id: number; full_name: string | null; load_before: number }>;
    fairness_score: number;
    preview: ExternalExamAssignmentPreview;
    exam: ExternalExam;
  }>(`/external/${examId}/assign`, undefined, {
    query: compensation !== undefined ? { compensation } : undefined,
  });
}
