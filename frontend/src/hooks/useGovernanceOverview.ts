import { useQuery } from "@tanstack/react-query";
import { getGovernanceOverview } from "@/services/governanceCockpit.service";

export function useGovernanceOverview() {
  return useQuery({
    queryKey: ["governance-overview"],
    queryFn: getGovernanceOverview,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
