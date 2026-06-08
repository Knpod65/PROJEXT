export type PaymentDocumentType =
  | "ADVANCE_PAYMENT_DRAFT_SUMMARY"
  | "PAYMENT_RECONCILIATION_DRAFT"
  | "ABSENCE_EXPLANATION_REQUEST"
  | "REFUND_OFFSET_TRACKING_DRAFT";

export type PaymentDocumentReviewStatus =
  | "DRAFT_NOT_AUTHORIZED"
  | "DRAFT_READY_FOR_REVIEW"
  | "UNDER_REVIEW"
  | "REVISIONS_REQUESTED"
  | "ACCEPTED_FOR_DRAFT_EXPORT"
  | "REJECTED_REDESIGN_REQUIRED"
  | "FINAL_AUTHORIZATION_REQUIRED";

export interface PaymentDocumentReviewRecord {
  review_id: number;
  document_id: string;
  document_type: PaymentDocumentType;
  term: string | null;
  review_status: PaymentDocumentReviewStatus;
  comment: string | null;
  decision: string | null;
  reviewer_name: string | null;
  reviewer_role: string | null;
  reviewer_user_id: number | null;
  prepared_by: string | null;
  created_at: string | null;
  updated_at: string | null;
  reviewed_at: string | null;
  revision_required: boolean;
  note: string | null;
  payment_authorization_enabled: false;
  final_export_enabled: false;
}

export interface PaymentDocumentReviewCreate {
  document_id: string;
  document_type: PaymentDocumentType;
  term?: string | null;
  review_status?: PaymentDocumentReviewStatus;
  comment?: string | null;
  decision?: string | null;
  prepared_by?: string | null;
  revision_required?: boolean;
  note?: string | null;
}

export interface PaymentDocumentReviewUpdate {
  review_status?: PaymentDocumentReviewStatus;
  comment?: string | null;
  decision?: string | null;
  revision_required?: boolean;
  note?: string | null;
}

export interface PaymentDocumentReviewListResponse {
  records: PaymentDocumentReviewRecord[];
  payment_authorization_enabled: false;
  final_export_enabled: false;
}
