import { useMemo, useState } from "react";
import { useOptimizationTrace } from "@/hooks/useOptimizationTrace";
import { translate } from "@/i18n";
import type { OptimizationTraceSummary, TraceCandidate, TraceConstraintHit } from "@/types/optimizationTrace";

export interface UseOptimizationTraceExplorerReturn {
  isLoading: boolean;
  error: unknown;
  refresh: () => void;
  trace: OptimizationTraceSummary | undefined;
  traceSummary: {
    overallQualityScore: number;
    traceabilityCompletenessScore: number;
    rejectedAlternativesCount: number;
  };
  timelineItems: Array<{ id: string; stage: string; event_type: string; severity: string; detail: string; timestamp: string }>;
  rejectedAlternatives: TraceCandidate[];
  constraintItems: TraceConstraintHit[];
  selectedSessionId: number;
  setSelectedSessionId: (id: number) => void;
  mockSessions: Array<{ id: number; label: string; created: string }>;
  hasData: boolean;
  emptyStateKey: string;
}

const MOCK_SESSIONS = [
  { id: 1, label: translate("trace.session1"), created: "2026-05-19 10:00" },
  { id: 2, label: translate("trace.session2"), created: "2026-05-18 14:30" },
];

export function useOptimizationTraceExplorer(): UseOptimizationTraceExplorerReturn {
  const [selectedSessionId, setSelectedSessionId] = useState<number>(MOCK_SESSIONS[0]?.id ?? 1);
  const { data: trace, isLoading, error, refetch } = useOptimizationTrace(selectedSessionId);

  const traceSummary = useMemo(() => ({
    overallQualityScore: trace?.overall_quality_score ?? 0,
    traceabilityCompletenessScore: trace?.traceability_completeness_score ?? 0,
    rejectedAlternativesCount: trace?.rejected_alternatives_count ?? 0,
  }), [trace]);

  const timelineItems = useMemo(
    () =>
      (trace?.events ?? []).map((e) => ({
        id: e.event_id,
        stage: e.stage,
        event_type: e.event_type,
        severity: e.severity,
        detail: e.detail,
        timestamp: e.timestamp,
      })),
    [trace],
  );

  const rejectedAlternatives = trace?.candidates?.filter((c: TraceCandidate) => !c.selected) ?? [];
  const constraintItems = trace?.constraint_hits ?? [];

  return {
    isLoading,
    error,
    refresh: () => void refetch(),
    trace,
    traceSummary,
    timelineItems,
    rejectedAlternatives,
    constraintItems,
    selectedSessionId,
    setSelectedSessionId,
    mockSessions: MOCK_SESSIONS,
    hasData: !!trace && trace.events.length > 0,
    emptyStateKey: "trace.noData",
  };
}
