import { useQuery } from "@tanstack/react-query";
import { getOptimizationTrace } from "@/services/optimizationTrace.service";

export function useOptimizationTrace(sessionId: number) {
  return useQuery({
    queryKey: ["optimization-trace", sessionId],
    queryFn: () => getOptimizationTrace(sessionId),
    enabled: sessionId > 0,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}
