import { get, post, put } from "./api";
import type {
  InvigilationRateRuleListResponse,
  InvigilationRateRuleMutationResponse,
  InvigilationRateRulePayload,
} from "@/types/invigilationRateRules";

export function listInvigilationRateRules() {
  return get<InvigilationRateRuleListResponse>("/invigilation-payment/rate-rules");
}

export function createInvigilationRateRule(body: InvigilationRateRulePayload) {
  return post<InvigilationRateRuleMutationResponse>("/invigilation-payment/rate-rules", body);
}

export function updateInvigilationRateRule(rateRuleId: number, body: InvigilationRateRulePayload) {
  return put<InvigilationRateRuleMutationResponse>(`/invigilation-payment/rate-rules/${rateRuleId}`, body);
}

export function activateInvigilationRateRule(rateRuleId: number) {
  return post<InvigilationRateRuleMutationResponse>(`/invigilation-payment/rate-rules/${rateRuleId}/activate`);
}

export function archiveInvigilationRateRule(rateRuleId: number) {
  return post<InvigilationRateRuleMutationResponse>(`/invigilation-payment/rate-rules/${rateRuleId}/archive`);
}

