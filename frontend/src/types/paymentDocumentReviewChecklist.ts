export type PaymentDocumentReviewChecklistItemKey =
  | "CHECK_PAYMENT_DOCUMENT_SETTINGS"
  | "CHECK_OFFICIAL_PAYMENT_DOCUMENT_DRAFT"
  | "CHECK_REVIEW_PANEL_STATUS"
  | "CHECK_DRAFT_XLSX_FILE_LAYOUT"
  | "CHECK_DRAFT_ONLY_LABEL"
  | "CHECK_NOT_PAYMENT_AUTHORIZATION"
  | "CHECK_FINAL_AUTHORIZATION_DISABLED";

export type PaymentDocumentReviewChecklistStatus =
  | "NOT_STARTED"
  | "IN_PROGRESS"
  | "CHECKED"
  | "NEEDS_ATTENTION"
  | "BLOCKED";

export interface PaymentDocumentReviewChecklistItem {
  checklist_id: number | null;
  document_id: string;
  document_type: "ADVANCE_PAYMENT_DRAFT_SUMMARY";
  term: string | null;
  item_key: PaymentDocumentReviewChecklistItemKey;
  item_order: number;
  item_status: PaymentDocumentReviewChecklistStatus;
  reviewer_user_id: number | null;
  reviewer_name: string | null;
  reviewer_role: string | null;
  comment: string | null;
  checked_at: string | null;
  created_at: string | null;
  updated_at: string | null;
  payment_authorization_enabled: false;
  final_export_enabled: false;
}

export interface PaymentDocumentReviewChecklistResponse {
  document_id: string;
  document_type: "ADVANCE_PAYMENT_DRAFT_SUMMARY";
  term: string | null;
  items: PaymentDocumentReviewChecklistItem[];
  total_items: number;
  checked_items: number;
  remaining_items: number;
  overall_status: PaymentDocumentReviewChecklistStatus;
  decision_gate_status: "HOLD_PENDING_ADDITIONAL_REVIEW";
  payment_authorization_enabled: false;
  final_export_enabled: false;
}

export interface PaymentDocumentReviewChecklistUpdate {
  item_status: PaymentDocumentReviewChecklistStatus;
  comment?: string | null;
}
