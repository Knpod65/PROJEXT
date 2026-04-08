import type { ImportSession } from "@/types/api";
import { get } from "./api";

export function listImportSessions() {
  return get<ImportSession[]>("/import/sessions");
}

export function getImportSummary(sessionId: number) {
  return get<Record<string, unknown>>(`/import/sessions/${sessionId}/summary`);
}
