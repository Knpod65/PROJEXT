import { useQuery } from "@tanstack/react-query";
import { fetchWorkloadDutyAnalytics, type WorkloadDutyAnalyticsQuery } from "@/services/workloadDutyAnalytics.service";
import type { WorkloadDutyAnalyticsPayload } from "@/types/workloadDutyAnalytics";

export function useWorkloadDutyAnalytics(query: WorkloadDutyAnalyticsQuery = {}) {
  return useQuery<WorkloadDutyAnalyticsPayload>({
    queryKey: ["workload-duty-analytics", query],
    queryFn: () => fetchWorkloadDutyAnalytics(query),
    staleTime: 60_000,
    retry: 1,
  });
}
