import { useMemo } from "react";
import { useGovernanceOverview } from "@/hooks/useGovernanceOverview";
import { translate } from "@/i18n";
import type { GovernanceOverview, GovernanceEventItem, FacultyGovernanceSummary } from "@/types/governance";

export interface UseGovernanceCockpitReturn {
  isLoading: boolean;
  error: unknown;
  refresh: () => void;
  overview: GovernanceOverview | undefined;
  summaryCards: Array<{ label: string; value: number; key: string }>;
  healthBadgeBand: string;
  hasRisks: boolean;
  hasEvents: boolean;
  hasFaculty: boolean;
  governanceHealth: number;
  emptyStateKey: string;
}

export function useGovernanceCockpit(): UseGovernanceCockpitReturn {
  const { data, isLoading, error, refetch } = useGovernanceOverview();

  const summaryCards = useMemo(() => {
    if (!data) return [];
    return [
      { label: translate("governance.blockers"), value: data.blocker_count, key: "blockers" },
      { label: translate("governance.overrides"), value: data.override_count, key: "overrides" },
      { label: translate("governance.rollbacks"), value: data.rollback_count, key: "rollbacks" },
      { label: translate("governance.escalations"), value: data.escalation_count, key: "escalations" },
      { label: translate("governance.publicationReady"), value: data.publication_ready_count, key: "pubReady" },
      { label: translate("governance.publicationBlocked"), value: data.publication_blocked_count, key: "pubBlocked" },
      { label: translate("governance.pendingApprovals"), value: data.pending_approval_count, key: "pendingApprovals" },
      { label: translate("governance.overdueSigning"), value: data.overdue_signing_count, key: "overdueSigning" },
    ];
  }, [data]);

  const healthBadgeBand = data?.risk_band ?? "green";
  const hasRisks = Array.isArray(data?.top_risks) && data.top_risks.length > 0;
  const hasEvents = Array.isArray(data?.recent_events) && data.recent_events.length > 0;
  const hasFaculty = Array.isArray(data?.faculty_summary) && data.faculty_summary.length > 0;
  const governanceHealth = data?.overall_health_score ?? 0;
  const emptyStateKey = "governance.noData";

  return {
    isLoading,
    error,
    refresh: () => void refetch(),
    overview: data,
    summaryCards,
    healthBadgeBand,
    hasRisks,
    hasEvents,
    hasFaculty,
    governanceHealth,
    emptyStateKey,
  };
}
