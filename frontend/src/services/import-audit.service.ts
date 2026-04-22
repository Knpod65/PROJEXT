import type {
  ImportAuditRowLogList,
  ImportAuditSessionDetail,
  ImportSession,
} from "@/types/api";
import { get } from "./api";

export function listImportAuditSessions() {
  return get<ImportSession[]>("/import/sessions");
}

export function getImportAuditSessionDetail(sessionId: number) {
  return get<ImportAuditSessionDetail>(`/import/sessions/${sessionId}/audit`);
}

interface ListImportAuditRowsOptions {
  status?: string;
  error_code?: string;
  q?: string;
}

export function listImportAuditRows(sessionId: number, options: ListImportAuditRowsOptions = {}) {
  return get<ImportAuditRowLogList>(`/import/sessions/${sessionId}/rows`, {
    query: {
      status: options.status,
      error_code: options.error_code,
      q: options.q,
    },
  });
}
