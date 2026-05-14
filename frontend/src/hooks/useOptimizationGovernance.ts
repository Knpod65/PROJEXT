import { get } from "@/services/api";
import type { OptimizationGovernanceReport } from "@/types/optimizationGovernance";
import { useAsyncData, type AsyncState } from "./useAsyncData";

/**
 * Fetches the optimization governance report for a given workflow session.
 *
 * Returns null report when sessionId is null (no fetch is performed).
 * Uses the shared useAsyncData hook for loading/error/reload semantics.
 *
 * HUMAN-APPROVAL GATE: This hook is read-only. Any action derived from the
 * report must be presented to an authorized user before execution.
 */
export function useOptimizationGovernance(
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
