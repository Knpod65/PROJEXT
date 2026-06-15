import { post } from "./api";
import type {
  FinanceSupportingRosterRequest,
  FinanceSupportingRosterStatus,
  OfficialPaymentDraftRequest,
  OfficialPaymentDraftResponse,
} from "@/types/officialPaymentDraft";

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

export function getFinanceSupportingRosterStatus(
  payload: FinanceSupportingRosterRequest,
): Promise<FinanceSupportingRosterStatus> {
  return post<FinanceSupportingRosterStatus>("/invigilation-advance-batch/finance-support-roster-status", payload);
}

export function exportFinanceSupportingRosterExcel(
  payload: FinanceSupportingRosterRequest,
): Promise<Blob> {
  return post<Blob>("/invigilation-advance-batch/finance-support-roster-export", payload);
}
