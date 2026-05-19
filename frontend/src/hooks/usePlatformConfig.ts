import { useQuery } from "@tanstack/react-query";
import { getPlatformConfig } from "@/services/platformConfiguration.service";

export function usePlatformConfig() {
  return useQuery({
    queryKey: ["platform-config"],
    queryFn: getPlatformConfig,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
