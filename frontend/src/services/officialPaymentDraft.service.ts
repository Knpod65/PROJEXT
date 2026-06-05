import { post } from "./api";
import type { OfficialPaymentDraftRequest, OfficialPaymentDraftResponse } from "@/types/officialPaymentDraft";

export function previewOfficialPaymentDraft(
  payload: OfficialPaymentDraftRequest,
): Promise<OfficialPaymentDraftResponse> {
  return post<OfficialPaymentDraftResponse>("/invigilation-advance-batch/official-document-draft-preview", payload);
}
