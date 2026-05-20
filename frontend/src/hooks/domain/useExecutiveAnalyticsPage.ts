import { useMemo } from "react";
import { useExecutiveAnalytics } from "@/hooks/useExecutiveAnalytics";
import { translate } from "@/i18n";
import type { ExecutiveDashboardSummary } from "@/types/analytics";
import { getBandColor, getSeverityBandColor, getPriorityBandColor } from "@/utils/presenters";

export interface UseExecutiveAnalyticsPageReturn {
  isLoading: boolean;
  error: unknown;
  refresh: () => void;
  data: ExecutiveDashboardSummary | undefined;
  healthBandColor: string;
  severityBandColor: (severity: string) => string;
  priorityBandColor: (priority: string) => string;
  kpiGrid: Array<{ label: string; value: number; key: string }>;
  topRisks: Array<{ risk: string; severity: string; category: string; severityColor: string }>;
  recommendedActions: Array<{ action: string; owner: string; priority: string; priorityColor: string }>;
  scoreSuffix: string;
  emptyStateKey: string;
}

export function useExecutiveAnalyticsPage(): UseExecutiveAnalyticsPageReturn {
  const { data, isLoading, error, refetch } = useExecutiveAnalytics();

  const healthBandColor = useMemo(() => {
    return getBandColor(data?.risk_band);
  }, [data]);

  const severityBandColor = (severity: string) => {
    return getSeverityBandColor(severity);
  };

  const priorityBandColor = (priority: string) => {
    return getPriorityBandColor(priority);
  };

  const kpiGrid = useMemo(() => {
    if (!data) return [];
    return [
      { label: translate("analytics.overallHealthScore"), value: data.overall_health_score, key: "health" },
      { label: translate("analytics.optimizationQuality"), value: data.optimization_quality_avg, key: "opt" },
      { label: translate("analytics.governanceBlockers"), value: data.governance_blocker_count, key: "blockers" },
      { label: translate("analytics.publicationReady"), value: data.publication_ready_count, key: "pub" },
      { label: translate("analytics.workloadBalance"), value: data.workload_balance_score, key: "workload" },
      { label: translate("analytics.roomUtilization"), value: data.room_utilization_score, key: "room" },
      { label: translate("analytics.pdpaAlerts"), value: data.pdpa_alert_count, key: "pdpa" },
    ];
  }, [data]);

  const topRisks = useMemo(() => {
    if (!data?.top_risks) return [];
    return data.top_risks.map((r) => ({
      risk: r.risk,
      severity: r.severity,
      category: r.category,
      severityColor: severityBandColor(r.severity),
    }));
  }, [data, severityBandColor]);

  const recommendedActions = useMemo(() => {
    if (!data?.recommended_actions) return [];
    return data.recommended_actions.map((a) => ({
      action: a.action,
      owner: a.owner,
      priority: a.priority,
      priorityColor: priorityBandColor(a.priority),
    }));
  }, [data, priorityBandColor]);

  return {
    isLoading,
    error,
    refresh: () => void refetch(),
    data,
    healthBandColor,
    severityBandColor,
    priorityBandColor,
    kpiGrid,
    topRisks,
    recommendedActions,
    scoreSuffix: translate("analytics.scoreSuffix"),
    emptyStateKey: "analytics.noData",
  };
}