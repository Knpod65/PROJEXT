/** useRoleDashboard — fetch & cache the role-specific dashboard. */
import { useQuery } from "@tanstack/react-query";
import { fetchRoleSummary } from "@/services/dashboardIntelligence.service";
import type { RoleDashboardPayload } from "@/types/dashboardMetrics";

export function useRoleDashboard(role?: string) {
  return useQuery<RoleDashboardPayload>({
    queryKey: ["role-dashboard", role ?? "auto"],
    queryFn: () => fetchRoleSummary(role),
    staleTime: 60_000,
    retry: 1,
  });
}
