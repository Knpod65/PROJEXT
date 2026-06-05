import type { ReactNode } from "react";

import { usePlatformConfigurationPage } from "@/hooks/domain/usePlatformConfigurationPage";
import { translate } from "@/i18n";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton } from "@/components/ui/Skeleton";

function SectionCard({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <Card title={title}>
      {children}
    </Card>
  );
}

function ConfigTable({
  headers,
  rows,
  render,
}: {
  headers: string[];
  rows: unknown[];
  render: (row: unknown, i: number) => React.ReactNode;
}) {
  if (!rows || rows.length === 0) {
    return (
      <p className="text-sm text-gray-500">{translate("governance.noData")}</p>
    );
  }
  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr className="border-b">
            {headers.map((h) => (
              <th key={h}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>{rows.map((row, i) => render(row, i))}</tbody>
      </table>
    </div>
  );
}

export default function PlatformConfiguration() {
  const {
    isLoading,
    error,
    data,
    facultyConfigs,
    workloadPolicies,
    governanceFlows,
    integrationContracts,
    analyticsMetrics,
    facultyHeaders,
    workloadHeaders,
    governanceHeaders,
    integrationHeaders,
    analyticsHeaders,
  } = usePlatformConfigurationPage();

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
          description={translate("platformConfig.loadError")}
        />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="page-stack page-stack--spacious">
        <EmptyState
          icon={<Icon name="info" />}
          title={translate("platformConfig.noData")}
          description={translate("platformConfig.noDataDesc")}
        />
      </div>
    );
  }

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        className="page-hero--dashboard"
        eyebrow={translate("platformConfig.eyebrow")}
        title={translate("navigation.pages.platform-configuration.title")}
        description={translate("platformConfig.readOnlyNotice")}
      />

      {/* Faculty Config */}
      <SectionCard title={translate("platformConfig.facultyConfig")}>
        <ConfigTable
          headers={facultyHeaders}
          rows={facultyConfigs}
          render={(row: any, i) => (
            <tr key={i}>
              <td>{row.faculty_id}</td>
              <td>{row.code}</td>
              <td>{row.name}</td>
              <td>{row.name_th}</td>
              <td>{row.name_en}</td>
              <td>
                {row.is_active ? "✓" : translate("common.no")}
              </td>
            </tr>
          )}
        />
        {(data as any).export_metadata?.note && (
          <p className="text-xs text-gray-400 mt-2">
            {(data as any).export_metadata.note}
          </p>
        )}
      </SectionCard>

      {/* Workload Policy */}
      <SectionCard title={translate("platformConfig.workloadPolicy")}>
        <ConfigTable
          headers={workloadHeaders}
          rows={workloadPolicies}
          render={(row: any, i) => (
            <tr key={i}>
              <td>{row.faculty_id ?? "—"}</td>
              <td>{row.paper_distribution_division}</td>
              <td>{row.max_supervision_sessions}</td>
              <td>
                {row.allow_cross_department ? translate("common.yes") : translate("common.no")}
              </td>
            </tr>
          )}
        />
      </SectionCard>

      {/* Governance Flow */}
      <SectionCard title={translate("platformConfig.governanceFlow")}>
        <ConfigTable
          headers={governanceHeaders}
          rows={governanceFlows}
          render={(row: any, i) => (
            <tr key={i}>
              <td>{row.faculty_id ?? "—"}</td>
              <td>{row.flow_name}</td>
              <td>
                {row.requires_governance_review ? translate("common.yes") : translate("common.no")}
              </td>
              <td>{row.approval_quorum}</td>
            </tr>
          )}
        />
      </SectionCard>

      {/* Integration Contracts */}
      <SectionCard title={translate("platformConfig.integrationContracts")}>
        <ConfigTable
          headers={integrationHeaders}
          rows={integrationContracts}
          render={(row: any, i) => (
            <tr key={i}>
              <td>{row.system_code}</td>
              <td>{row.integration_direction}</td>
              <td>{row.data_domain}</td>
              <td>{row.sync_mode}</td>
              <td>{row.owner_unit}</td>
            </tr>
          )}
        />
      </SectionCard>

      {/* Analytics Metrics */}
      <SectionCard title={translate("platformConfig.analyticsMetrics")}>
        <ConfigTable
          headers={analyticsHeaders}
          rows={analyticsMetrics}
          render={(row: any, i) => (
            <tr key={i}>
              <td className="font-mono text-xs">{row.metric_code}</td>
              <td>{row.name}</td>
              <td>{row.category}</td>
              <td>{row.unit}</td>
              <td>{row.pdpa_level}</td>
            </tr>
          )}
        />
      </SectionCard>
    </div>
  );
}
