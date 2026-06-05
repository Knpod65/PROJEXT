import { useCallback, useState } from "react";

import { previewOfficialPaymentDraft } from "@/services/officialPaymentDraft.service";
import type { OfficialPaymentDraftRequest, OfficialPaymentDraftResponse } from "@/types/officialPaymentDraft";

export function useOfficialPaymentDraftPreview() {
  const [data, setData] = useState<OfficialPaymentDraftResponse | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [isLoading, setIsLoading] = useState(false);

  const preview = useCallback(async (payload: OfficialPaymentDraftRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await previewOfficialPaymentDraft(payload);
      setData(response);
      return response;
    } catch (caught) {
      setError(caught);
      throw caught;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { data, error, isError: Boolean(error), isLoading, preview, setData };
}
