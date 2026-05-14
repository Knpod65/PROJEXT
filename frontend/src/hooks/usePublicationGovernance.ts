import { get } from "@/services/api";
import { useAsyncData, type AsyncState } from "./useAsyncData";

export interface PublicationBlocker {
  code: string;
  severity: string;
  message: string;
  can_override: boolean;
}

export interface PublicationReadiness {
  can_publish: boolean;
  risk_score: number;
  blockers: PublicationBlocker[];
  warnings: string[];
  governance_state: string;
  approval_metadata: Record<string, unknown>;
}

/**
 * Fetches the publication readiness assessment for a given workflow session.
 *
 * HUMAN-APPROVAL GATE: Read-only. Any publish action must be manually confirmed
 * by an authorized user before execution.
 */
export function usePublicationGovernance(
  sessionId: number | null,
): AsyncState<PublicationReadiness> {
  return useAsyncData<PublicationReadiness>(
    async () => {
      if (sessionId === null) {
        return null as unknown as PublicationReadiness;
      }
      return get<PublicationReadiness>(
        `/workflow/sessions/${sessionId}/publication-readiness`,
      );
    },
    [sessionId],
  );
}
