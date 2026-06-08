import { get, post, put } from "./api";
import type {
  PaymentDocumentReviewCreate,
  PaymentDocumentReviewListResponse,
  PaymentDocumentReviewRecord,
  PaymentDocumentReviewUpdate,
} from "@/types/paymentDocumentReview";

export function listPaymentDocumentReviews(documentId: string): Promise<PaymentDocumentReviewListResponse> {
  return get<PaymentDocumentReviewListResponse>("/payment-document-reviews", {
    query: { document_id: documentId },
  });
}

export function createPaymentDocumentReview(
  payload: PaymentDocumentReviewCreate,
): Promise<PaymentDocumentReviewRecord> {
  return post<PaymentDocumentReviewRecord>("/payment-document-reviews", payload);
}

export function updatePaymentDocumentReview(
  reviewId: number,
  payload: PaymentDocumentReviewUpdate,
): Promise<PaymentDocumentReviewRecord> {
  return put<PaymentDocumentReviewRecord>(`/payment-document-reviews/${reviewId}`, payload);
}
