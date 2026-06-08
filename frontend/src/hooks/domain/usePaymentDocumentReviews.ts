import { useCallback, useEffect, useState } from "react";

import {
  createPaymentDocumentReview,
  listPaymentDocumentReviews,
  updatePaymentDocumentReview,
} from "@/services/paymentDocumentReview.service";
import type {
  PaymentDocumentReviewCreate,
  PaymentDocumentReviewRecord,
  PaymentDocumentReviewUpdate,
} from "@/types/paymentDocumentReview";

export function usePaymentDocumentReviews(documentId: string) {
  const [records, setRecords] = useState<PaymentDocumentReviewRecord[]>([]);
  const [error, setError] = useState<unknown>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const refresh = useCallback(async () => {
    if (!documentId) {
      setRecords([]);
      return [];
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await listPaymentDocumentReviews(documentId);
      setRecords(response.records);
      return response.records;
    } catch (caught) {
      setError(caught);
      throw caught;
    } finally {
      setIsLoading(false);
    }
  }, [documentId]);

  const create = useCallback(
    async (payload: PaymentDocumentReviewCreate) => {
      setIsSaving(true);
      setError(null);
      try {
        const response = await createPaymentDocumentReview(payload);
        await refresh();
        return response;
      } catch (caught) {
        setError(caught);
        throw caught;
      } finally {
        setIsSaving(false);
      }
    },
    [refresh],
  );

  const update = useCallback(
    async (reviewId: number, payload: PaymentDocumentReviewUpdate) => {
      setIsSaving(true);
      setError(null);
      try {
        const response = await updatePaymentDocumentReview(reviewId, payload);
        await refresh();
        return response;
      } catch (caught) {
        setError(caught);
        throw caught;
      } finally {
        setIsSaving(false);
      }
    },
    [refresh],
  );

  useEffect(() => {
    void refresh().catch(() => undefined);
  }, [refresh]);

  return {
    records,
    latestRecord: records[0] ?? null,
    error,
    isError: Boolean(error),
    isLoading,
    isSaving,
    refresh,
    create,
    update,
  };
}
