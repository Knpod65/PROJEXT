import { useMemo } from "react";
import { useOperationalHealth } from "@/hooks/useOperationalHealth";
import { translate } from "@/i18n";
import { getBandColor, getRiskBand } from "@/utils/presenters";

export interface UseOperationalHealthPageReturn {
  isLoading: boolean;
  error: unknown;
  refresh: () => void;
  data: {
    backend_healthy: boolean;
    health_timestamp: string | null;
    analytics_score: number | null;
    integration_active: number;
    integration_total: number;
  } | undefined;
  backendHealthy: boolean;
  analyticsScore: number | null;
  analyticsBand: "green" | "amber" | "red" | null;
  analyticsBandColor: string;
  integrationRatio: string;
  healthTimestamp: string | null;
  livenessLabel: string;
  emptyStateKey: string;
}

export function useOperationalHealthPage(): UseOperationalHealthPageReturn {
  const { data, isLoading, error, refetch } = useOperationalHealth();

  const backendHealthy = data?.backend_healthy ?? false;
  const analyticsScore = data?.analytics_score ?? null;

  const analyticsBand = useMemo(() => {
    return getRiskBand(analyticsScore);
  }, [analyticsScore]);

  const analyticsBandColor = useMemo(() => {
    return getBandColor(analyticsBand);
  }, [analyticsBand]);

  const integrationRatio = useMemo(() => {
    if (data && data.integration_total > 0) {
      return `${data.integration_active}/${data.integration_total}`;
    }
    return "—";
  }, [data]);

  const livenessLabel = backendHealthy
    ? translate("operationalHealth.okStatus")
    : translate("operationalHealth.unreachable");

  return {
    isLoading,
    error,
    refresh: () => void refetch(),
    data,
    backendHealthy,
    analyticsScore,
    analyticsBand,
    analyticsBandColor,
    integrationRatio,
    healthTimestamp: data?.health_timestamp ?? null,
    livenessLabel,
    emptyStateKey: "operationalHealth.noData",
  };
}