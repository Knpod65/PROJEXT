import { get } from "./api";
import type { OptimizationTraceSummary } from "@/types/optimizationTrace";

/**
 * Fetch the optimization trace for a given optimizer session.
 * The backend aggregates trace data from the optimization pipeline observer
 * and recheck service. Returns a safe empty stub when no trace records exist
 * for the given session.
 */
export function getOptimizationTrace(sessionId: number) {
  return get<OptimizationTraceSummary>(`/analytics/optimization-trace/${sessionId}`);
}
