/** useAdminIntelligenceDashboard — fetch & cache the Admin 10-group intelligence dashboard. */
import { useQuery } from "@tanstack/react-query";
import { fetchAdminIntelligenceDashboard } from "@/services/dashboardIntelligence.service";
import type { AdminIntelligenceDashboard } from "@/types/dashboardMetrics";

export function useAdminIntelligenceDashboard(semester?: string, academicYear?: string) {
  return useQuery<AdminIntelligenceDashboard>({
    queryKey: ["admin-intelligence", semester, academicYear],
    queryFn: () => fetchAdminIntelligenceDashboard(semester, academicYear),
    staleTime: 60_000,
    retry: 1,
  });
}
