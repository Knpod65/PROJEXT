import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  getPaymentDocumentSettings,
  savePaymentDocumentSettings,
} from "@/services/paymentDocumentSettings.service";
import type { PaymentDocumentSettingsPayload } from "@/types/paymentDocumentSettings";

export const paymentDocumentSettingsQueryKey = (term: string) => ["payment-document-settings", term] as const;

export function usePaymentDocumentSettings(term: string) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: paymentDocumentSettingsQueryKey(term),
    queryFn: () => getPaymentDocumentSettings(term),
    enabled: Boolean(term.trim()),
    staleTime: 30_000,
    retry: 1,
  });

  const mutation = useMutation({
    mutationFn: (payload: PaymentDocumentSettingsPayload) => savePaymentDocumentSettings(term, payload),
    onSuccess: (saved) => {
      queryClient.setQueryData(paymentDocumentSettingsQueryKey(term), saved);
    },
  });

  return {
    ...query,
    save: mutation.mutateAsync,
    isSaving: mutation.isPending,
    saveError: mutation.error,
  };
}
