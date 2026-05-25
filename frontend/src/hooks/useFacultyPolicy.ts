import { useEffect, useState } from "react";

import type {
  GovernanceFlowSummary,
  WorkloadPolicySummary,
} from "@/services/platformConfig.service";
import { buildApiUrl } from "@/services/api";

export function useFacultyPolicy(facultyId: number | null): {
  policy: WorkloadPolicySummary | null;
  flow: GovernanceFlowSummary | null;
  isLoading: boolean;
  error: Error | null;
} {
  const [policy, setPolicy] = useState<WorkloadPolicySummary | null>(null);
  const [flow, setFlow] = useState<GovernanceFlowSummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (facultyId === null) {
      setPolicy(null);
      setFlow(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    const policyUrl = buildApiUrl(`/platform/faculty-configs/${facultyId}/workload-policy`);
    const flowUrl = buildApiUrl(`/platform/faculty-configs/${facultyId}/governance-flow`);

    Promise.all([
      fetch(policyUrl).then((r) => (r.ok ? (r.json() as Promise<WorkloadPolicySummary>) : null)),
      fetch(flowUrl).then((r) => (r.ok ? (r.json() as Promise<GovernanceFlowSummary>) : null)),
    ])
      .then(([policyData, flowData]) => {
        setPolicy(policyData);
        setFlow(flowData);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err : new Error(String(err)));
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [facultyId]);

  return { policy, flow, isLoading, error };
}
