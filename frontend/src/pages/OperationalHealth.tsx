import { useOperationalHealthPage } from "@/hooks/domain/useOperationalHealthPage";
import { translate } from "@/i18n";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton } from "@/components/ui/Skeleton";

function StatusDot({ ok }: { ok: boolean | null }) {
  const className = ok === true ? "status-dot status-dot--ok" : ok === false ? "status-dot status-dot--error" : "status-dot";
  return <span className={className} />;
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
    <div className="status-line">
      <span>{label}</span>
      <span className="status-line__value">
        {ok !== undefined && <StatusDot ok={ok} />}
        {value}
      </span>
    </div>
  );
}

export default function OperationalHealth() {
  const {
    isLoading,
    error,
    backendHealthy,
    analyticsScore,
    analyticsBand,
    integrationRatio,
    healthTimestamp,
    livenessLabel,
  } = useOperationalHealthPage();

  if (isLoading) {
    return (
      <div className="page-stack page-stack--spacious">
        <div className="stitch-metric-grid">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="dashboard-skeleton" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-stack page-stack--spacious">
        <EmptyState
          icon={<Icon name="warning" />}
          title={translate("errors.requestFailed")}
          description={translate("operationalHealth.noData")}
        />
      </div>
    );
  }

  const analyticsOk = analyticsBand === "green" ? true : analyticsBand === "red" ? false : null;

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        className="page-hero--dashboard"
        eyebrow={translate("operationalHealth.backendHealth")}
        title={translate("navigation.pages.operational-health.title")}
        description={translate("operationalHealth.autoRefreshNote")}
      />

      <Card
        title={translate("operationalHealth.backendHealth")}
        subtitle={translate("operationalHealth.liveness")}
        actions={<Badge variant={backendHealthy ? "green" : "crimson"}>{livenessLabel}</Badge>}
      >
        <StatLine
          label={translate("operationalHealth.liveness")}
          value={livenessLabel}
          ok={backendHealthy}
        />
        <StatLine
          label={translate("operationalHealth.lastCheck")}
          value={
            healthTimestamp
              ? new Date(healthTimestamp).toLocaleTimeString()
              : translate("common.notAvailable")
          }
        />
        </Card>

        <Card
          title={translate("operationalHealth.analyticsHealth")}
          subtitle={translate("operationalHealth.healthScore")}
          actions={
            analyticsBand ? (
              <Badge variant={analyticsBand === "red" ? "crimson" : analyticsBand === "amber" ? "gold" : "green"}>
                {analyticsBand}
              </Badge>
            ) : null
          }
        >
        <StatLine
          label={translate("operationalHealth.healthScore")}
          value={
            analyticsScore != null
              ? `${analyticsScore} ${translate("analytics.scoreSuffix")}`
              : translate("common.notAvailable")
          }
          ok={analyticsOk}
        />
      </Card>

      <Card
        title={translate("operationalHealth.integrationReadiness")}
        subtitle={translate("operationalHealth.activeContracts")}
        actions={<Badge variant="blue">{integrationRatio}</Badge>}
      >
        <StatLine
          label={translate("operationalHealth.activeContracts")}
          value={integrationRatio}
        />
      </Card>

      <div className="text-muted">
        {translate("operationalHealth.autoRefreshNote")}
      </div>
    </div>
  );
}
