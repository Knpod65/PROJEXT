import { useCallback, useEffect, useState } from "react";

import {
  getPaymentDocumentReviewChecklist,
  updatePaymentDocumentReviewChecklistItem,
} from "@/services/paymentDocumentReviewChecklist.service";
import type {
  PaymentDocumentReviewChecklistItemKey,
  PaymentDocumentReviewChecklistResponse,
  PaymentDocumentReviewChecklistUpdate,
} from "@/types/paymentDocumentReviewChecklist";

export function usePaymentDocumentReviewChecklist(documentId: string) {
  const [data, setData] = useState<PaymentDocumentReviewChecklistResponse | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [savingItemKey, setSavingItemKey] = useState<PaymentDocumentReviewChecklistItemKey | null>(null);

  const refresh = useCallback(async () => {
    if (!documentId) return null;
    setIsLoading(true);
    setError(null);
    try {
      const response = await getPaymentDocumentReviewChecklist(documentId);
      setData(response);
      return response;
    } catch (caught) {
      setError(caught);
      throw caught;
    } finally {
      setIsLoading(false);
    }
  }, [documentId]);

  const updateItem = useCallback(async (
    itemKey: PaymentDocumentReviewChecklistItemKey,
    payload: PaymentDocumentReviewChecklistUpdate,
  ) => {
    setSavingItemKey(itemKey);
    setError(null);
    try {
      const response = await updatePaymentDocumentReviewChecklistItem(documentId, itemKey, payload);
      setData(response);
      return response;
    } catch (caught) {
      setError(caught);
      throw caught;
    } finally {
      setSavingItemKey(null);
    }
  }, [documentId]);

  useEffect(() => {
    void refresh().catch(() => undefined);
  }, [refresh]);

  return {
    data,
    error,
    isError: Boolean(error),
    isLoading,
    savingItemKey,
    refresh,
    updateItem,
  };
}
