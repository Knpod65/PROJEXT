import { useQuery } from "@tanstack/react-query";

import { fetchAdvanceBatchPreview } from "@/services/invigilationAdvanceBatch.service";
import type { AdvanceBatchPreviewPayload, AdvanceBatchPreviewQuery } from "@/types/invigilationAdvanceBatch";

export function useAdvanceBatchPreview(query: AdvanceBatchPreviewQuery = {}) {
  return useQuery<AdvanceBatchPreviewPayload>({
    queryKey: ["advance-batch-preview", query],
    queryFn: () => fetchAdvanceBatchPreview(query),
    staleTime: 60_000,
    retry: 1,
  });
}
