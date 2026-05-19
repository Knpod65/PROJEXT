import { useOperationalHealth } from "@/hooks/useOperationalHealth";
import { translate } from "@/i18n";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";

function StatusDot({ ok }: { ok: boolean | null }) {
  const color = ok === true ? "bg-green-500" : ok === false ? "bg-red-500" : "bg-gray-400";
  return <span className={`inline-block w-3 h-3 rounded-full ${color}`} />;
}

function StatLine({
  label,
  value,
  ok,
}: {
  label: string;
  value: string;
  ok?: boolean | null;
}) {
  return (
    <div className="flex items-center justify-between py-2 border-b last:border-0">
      <span className="text-sm text-gray-600">{label}</span>
      <span className="flex items-center gap-2 text-sm font-medium">
        {ok !== undefined && <StatusDot ok={ok} />}
        {value}
      </span>
    </div>
  );
}

export default function OperationalHealth() {
  const { data, isLoading, error } = useOperationalHealth();

  if (isLoading) {
    return (
      <div className="p-6">
        <p className="text-gray-500">{translate("common.loading")}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<Icon name="warning" />}
          title={translate("errors.requestFailed")}
        />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<Icon name="info" />}
          title={translate("operationalHealth.noData")}
          description={translate("operationalHealth.noDataDesc")}
        />
      </div>
    );
  }

  const analyticsBand =
    data.analytics_score == null
      ? null
      : data.analytics_score >= 75
        ? "green"
        : data.analytics_score >= 50
          ? "amber"
          : "red";

  const integrationRatio =
    data.integration_total > 0
      ? `${data.integration_active}/${data.integration_total}`
      : "—";

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">
        {translate("navigation.pages.operational-health.title")}
      </h1>

      <div className="bg-white rounded-lg shadow p-4 space-y-1">
        <h2 className="text-base font-semibold mb-2">
          {translate("operationalHealth.backendHealth")}
        </h2>
        <StatLine
          label={translate("operationalHealth.liveness")}
          value={
            data.backend_healthy
              ? translate("operationalHealth.okStatus")
              : translate("operationalHealth.unreachable")
          }
          ok={data.backend_healthy}
        />
        <StatLine
          label={translate("operationalHealth.lastCheck")}
          value={
            data.health_timestamp
              ? new Date(data.health_timestamp).toLocaleTimeString()
              : translate("common.notAvailable")
          }
        />
      </div>

      <div className="bg-white rounded-lg shadow p-4 space-y-1">
        <h2 className="text-base font-semibold mb-2">
          {translate("operationalHealth.analyticsHealth")}
        </h2>
        <StatLine
          label={translate("operationalHealth.healthScore")}
          value={
            data.analytics_score != null
              ? `${data.analytics_score} / 100`
              : translate("common.notAvailable")
          }
          ok={analyticsBand === "green" ? true : analyticsBand === "red" ? false : null}
        />
      </div>

      <div className="bg-white rounded-lg shadow p-4 space-y-1">
        <h2 className="text-base font-semibold mb-2">
          {translate("operationalHealth.integrationReadiness")}
        </h2>
        <StatLine
          label={translate("operationalHealth.activeContracts")}
          value={integrationRatio}
        />
      </div>

      <div className="text-xs text-gray-400 text-center">
        {translate("operationalHealth.autoRefreshNote")}
      </div>
    </div>
  );
}
