import type { CoExamGroup } from "@/types/api";
import { del, get, post, put } from "./api";

export interface CoExamSuggestionsResponse {
  suggestions: Array<Record<string, unknown>>;
  count: number;
  note?: string;
}

export function listCoExamGroups() {
  return get<CoExamGroup[]>("/co-exam");
}

export function createCoExamGroup(body: Record<string, unknown>) {
  return post<CoExamGroup>("/co-exam", body);
}

export function updateCoExamGroup(groupId: number, body: Record<string, unknown>) {
  return put<CoExamGroup>(`/co-exam/${groupId}`, body);
}

export function deleteCoExamGroup(groupId: number) {
  return del<{ success: boolean }>(`/co-exam/${groupId}`);
}

export function autoDetectCoExam() {
  return post<CoExamSuggestionsResponse>("/co-exam/auto-detect");
}
