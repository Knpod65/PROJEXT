import type { ExternalExam } from "@/types/api";
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
  return del<{ success: boolean }>(`/external/${examId}`);
}
