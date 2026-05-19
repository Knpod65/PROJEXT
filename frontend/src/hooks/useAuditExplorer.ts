import { useQuery } from "@tanstack/react-query";
import { fetchAuditEvents, fetchGovernanceTimeline, fetchLifecycleTimeline } from "@/services/auditExplorer.service";

export function useAuditEvents() {
  return useQuery({
    queryKey: ["audit-events"],
    queryFn: fetchAuditEvents,
    staleTime: 60 * 1000,
  });
}

export function useGovernanceTimeline(sessionId?: string) {
  return useQuery({
    queryKey: ["governance-timeline", sessionId],
    queryFn: () => fetchGovernanceTimeline(sessionId),
    staleTime: 60 * 1000,
    enabled: !!sessionId,
  });
}

export function useLifecycleTimeline(sessionId: string) {
  return useQuery({
    queryKey: ["lifecycle-timeline", sessionId],
    queryFn: () => fetchLifecycleTimeline(sessionId),
    staleTime: 60 * 1000,
    enabled: !!sessionId,
  });
}