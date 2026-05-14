import { get } from "@/services/api";
import type { OptimizationGovernanceReport } from "@/types/optimizationGovernance";
import { useAsyncData, type AsyncState } from "./useAsyncData";

/**
 * Fetches the full optimization governance report for a given workflow session.
 * Alias for useOptimizationGovernance — targets the /governance endpoint.
 *
 * HUMAN-APPROVAL GATE: Read-only. Any action must be presented to an authorized
 * user before execution.
 */
export function useScheduleGovernance(
  sessionId: number | null,
): AsyncState<OptimizationGovernanceReport> {
  return useAsyncData<OptimizationGovernanceReport>(
    async () => {
      if (sessionId === null) {
        return null as unknown as OptimizationGovernanceReport;
      }
      return get<OptimizationGovernanceReport>(
        `/workflow/sessions/${sessionId}/governance`,
      );
    },
    [sessionId],
  );
}
