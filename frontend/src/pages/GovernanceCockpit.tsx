import { useGovernanceCockpit } from "@/hooks/domain/useGovernanceCockpit";
import { translate } from "@/i18n";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { DataTable, type DataTableColumn } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton } from "@/components/ui/Skeleton";
import { StatusChip, type StatusTone } from "@/components/ui/StatusChip";

function RiskBadge({ severity }: { severity: string }) {
  const tone: StatusTone = severity === "critical" || severity === "high"
    ? "danger"
    : severity === "medium"
      ? "warning"
      : "success";
  const label = translate(`severity.${severity}`) || severity.toUpperCase();
  return <StatusChip tone={tone}>{label}</StatusChip>;
}

function GovernanceStatCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: React.ReactNode;
  sub?: string;
}) {
  return (
    <Card title={label} subtitle={sub}>
      <p className="metric-value">{value}</p>
    </Card>
  );
}

function HealthBand({ band }: { band: string }) {
  const tone: StatusTone = band === "green" ? "success" : band === "amber" ? "warning" : "danger";
  return <StatusChip tone={tone}>{translate("governance.riskBand", { band: band.toUpperCase() })}</StatusChip>;
}

export const GovernanceCockpitPage = function GovernanceCockpit() {
  const {
    isLoading,
    error,
    refresh,
    overview,
    summaryCards,
    healthBadgeBand,
    hasRisks,
    hasEvents,
    hasFaculty,
    governanceHealth,
    emptyStateKey,
  } = useGovernanceCockpit();

  if (isLoading) {
    return (
      <div className="page-stack page-stack--spacious">
        <div className="stitch-metric-grid">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="dashboard-skeleton" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !overview) {
    return (
      <div className="page-stack page-stack--spacious">
        <EmptyState
          icon={<Icon name={error ? "warning" : "info"} />}
          title={translate(error ? "errors.requestFailed" : "governance.noData")}
          description={error ? translate("governance.loadError") : translate("governance.noDataDesc")}
        />
      </div>
    );
  }

  const { top_risks, recent_events, faculty_summary } = overview;
  const facultyColumns: Array<DataTableColumn<{ faculty_id: string; faculty_name: string; health_score: number; blocker_count: number }>> = [
    { key: "faculty_name", label: translate("governance.faculty"), minWidth: "220px" },
    { key: "health_score", label: translate("governance.healthScore"), width: "140px", align: "right" },
    { key: "blocker_count", label: translate("governance.blockers"), width: "140px", align: "right" },
  ];

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        className="page-hero--dashboard"
        eyebrow={translate("governance.eyebrow")}
        title={translate("navigation.pages.governance-cockpit.title")}
        status={<HealthBand band={healthBadgeBand} />}
      />

      <Card title={translate("governance.healthScore")} subtitle={translate("governance.healthNote")}>
        <p className="metric-value">{governanceHealth} {translate("governance.of100")}</p>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {summaryCards.map((card) => (
          <GovernanceStatCard key={card.key} label={card.label} value={card.value} />
        ))}
      </div>

      <Card title={translate("governance.topRisks")}>
        {hasRisks ? (
          <ul className="timeline-list">
            {(top_risks as Array<{ risk: string; severity: string; category: string }>).map((risk, i) => (
              <li key={i} className="timeline-list__item">
                <span>{risk.risk}</span>
                <RiskBadge severity={risk.severity} />
              </li>
            ))}
          </ul>
        ) : (
          <EmptyState icon={<Icon name="info" />} title={translate("governance.noRisks")} />
        )}
      </Card>

      <Card title={translate("governance.recentEvents")}>
        {hasEvents ? (
          <ul className="timeline-list">
            {(recent_events as Array<{ event_type: string; detail: string; timestamp: string }>).map((evt, i) => (
              <li key={i} className="timeline-list__item">
                <span>{evt.detail}</span>
                <span className="timeline-list__meta">{evt.event_type}</span>
              </li>
            ))}
          </ul>
        ) : (
          <EmptyState icon={<Icon name="info" />} title={translate("governance.noEvents")} />
        )}
      </Card>

      <Card title={translate("governance.facultySummary")}>
        {hasFaculty ? (
          <DataTable
            columns={facultyColumns}
            rows={faculty_summary as Array<{ faculty_id: string; faculty_name: string; health_score: number; blocker_count: number }>}
            rowKey={(row) => row.faculty_id}
            tableLayout="fixed"
            compact
          />
        ) : (
          <EmptyState icon={<Icon name="info" />} title={translate("governance.noFacultyData")} />
        )}
      </Card>
    </div>
  );
};
