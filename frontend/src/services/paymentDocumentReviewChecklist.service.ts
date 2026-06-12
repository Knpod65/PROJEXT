import { get, put } from "./api";
import type {
  PaymentDocumentReviewChecklistResponse,
  PaymentDocumentReviewChecklistUpdate,
} from "@/types/paymentDocumentReviewChecklist";

function checklistPath(documentId: string) {
  return `/payment-document-review-checklist/${encodeURIComponent(documentId)}`;
}

export function getPaymentDocumentReviewChecklist(documentId: string): Promise<PaymentDocumentReviewChecklistResponse> {
  return get<PaymentDocumentReviewChecklistResponse>(checklistPath(documentId));
}

export function updatePaymentDocumentReviewChecklistItem(
  documentId: string,
  itemKey: string,
  payload: PaymentDocumentReviewChecklistUpdate,
): Promise<PaymentDocumentReviewChecklistResponse> {
  return put<PaymentDocumentReviewChecklistResponse>(
    `${checklistPath(documentId)}/items/${encodeURIComponent(itemKey)}`,
    payload,
  );
}
