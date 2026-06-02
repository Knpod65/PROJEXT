import { useQuery } from "@tanstack/react-query";

import { listInvigilationRateRules } from "@/services/invigilationRateRules.service";

export const invigilationRateRulesQueryKey = ["invigilation-rate-rules"] as const;

export function useInvigilationRateRules() {
  return useQuery({
    queryKey: invigilationRateRulesQueryKey,
    queryFn: listInvigilationRateRules,
    staleTime: 30_000,
    retry: 1,
  });
}

