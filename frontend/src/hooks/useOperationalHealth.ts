import { useQuery } from "@tanstack/react-query";
import { getOperationalHealth } from "@/services/operationalHealth.service";

export function useOperationalHealth() {
  return useQuery({
    queryKey: ["operational-health"],
    queryFn: getOperationalHealth,
    staleTime: 30 * 1000, // 30 seconds — refreshes often
    refetchInterval: 60 * 1000, // auto-refresh every 60s
  });
}
