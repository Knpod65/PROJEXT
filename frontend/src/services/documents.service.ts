import type { PickupQrMutationResponse, PickupQrStatusResponse } from "@/types/api";

import { get, post } from "./api";

export type OperationalDocumentType =
  | "all"
  | "participant_codes"
  | "signature_sheet"
  | "envelope_cover";

export interface DocumentExportQuery {
  schedule_id?: number;
  course_id?: string;
  section_no?: string;
  room_id?: number;
  academic_year?: string;
  semester?: string;
  exam_type?: string;
  document_type?: OperationalDocumentType;
}

export function getPickupQrStatus(scheduleId: number) {
  return get<PickupQrStatusResponse>(`/documents/pickup-qr/${scheduleId}`);
}

export function regeneratePickupQr(scheduleId: number) {
  return post<PickupQrMutationResponse>(`/documents/pickup-qr/${scheduleId}/regenerate`);
}

export function confirmPickupQr(scheduleId: number, qrId?: number) {
  return post<PickupQrMutationResponse>(`/documents/pickup-qr/${scheduleId}/confirm`, undefined, {
    query: { qr_id: qrId },
  });
}

export function buildDocumentExportUrl(query: DocumentExportQuery = {}) {
  const url = new URL("/api/documents/export-pdf", window.location.origin);
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });
  return url.toString();
}
