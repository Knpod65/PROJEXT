import { post } from "./api";
import type { OfficialPaymentDraftRequest, OfficialPaymentDraftResponse } from "@/types/officialPaymentDraft";

export function previewOfficialPaymentDraft(
  payload: OfficialPaymentDraftRequest,
): Promise<OfficialPaymentDraftResponse> {
  return post<OfficialPaymentDraftResponse>("/invigilation-advance-batch/official-document-draft-preview", payload);
}

export function exportOfficialPaymentDraftExcel(
  payload: OfficialPaymentDraftRequest,
): Promise<Blob> {
  return post<Blob>("/invigilation-advance-batch/official-document-draft-export", payload);
}
