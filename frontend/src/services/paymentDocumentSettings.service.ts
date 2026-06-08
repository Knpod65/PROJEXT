import { get, put } from "./api";
import type {
  PaymentDocumentSettings,
  PaymentDocumentSettingsListResponse,
  PaymentDocumentSettingsPayload,
} from "@/types/paymentDocumentSettings";

export function listPaymentDocumentSettings(): Promise<PaymentDocumentSettingsListResponse> {
  return get<PaymentDocumentSettingsListResponse>("/payment-document-settings");
}

export function getPaymentDocumentSettings(term: string): Promise<PaymentDocumentSettings> {
  return get<PaymentDocumentSettings>(`/payment-document-settings/${encodeURIComponent(term)}`);
}

export function savePaymentDocumentSettings(
  term: string,
  payload: PaymentDocumentSettingsPayload,
): Promise<PaymentDocumentSettings> {
  return put<PaymentDocumentSettings>(`/payment-document-settings/${encodeURIComponent(term)}`, payload);
}
