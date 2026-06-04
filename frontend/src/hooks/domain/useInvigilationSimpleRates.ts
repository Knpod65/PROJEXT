import { useQuery } from "@tanstack/react-query";

import { getSimpleInvigilationRates } from "@/services/invigilationSimpleRates.service";

export const invigilationSimpleRatesQueryKey = ["invigilation-simple-rates"] as const;

export function useInvigilationSimpleRates() {
  return useQuery({
    queryKey: invigilationSimpleRatesQueryKey,
    queryFn: getSimpleInvigilationRates,
    staleTime: 30_000,
    retry: 1,
  });
}

