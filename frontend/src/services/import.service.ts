import type {
  ImportAuditRowLogList,
  ImportAuditSessionDetail,
  ImportSession,
} from "@/types/api";
import { get } from "./api";

export function listImportSessions() {
  return get<ImportSession[]>("/import/sessions");
}

export function getImportSummary(sessionId: number) {
  return get<Record<string, unknown>>(`/import/sessions/${sessionId}/summary`);
}

export function getImportSessionAudit(sessionId: number) {
  return get<ImportAuditSessionDetail>(`/import/sessions/${sessionId}/audit`);
}

interface ListSessionRowsOptions {
  status?: string;
  error_code?: string;
  q?: string;
}

export function listImportSessionRows(sessionId: number, options: ListSessionRowsOptions = {}) {
  return get<ImportAuditRowLogList>(`/import/sessions/${sessionId}/rows`, {
    query: {
      status: options.status,
      error_code: options.error_code,
      q: options.q,
    },
  });
}
