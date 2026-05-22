import { usePlatformConfigurationPage } from "@/hooks/domain/usePlatformConfigurationPage";
import { translate } from "@/i18n";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Skeleton } from "@/components/ui/Skeleton";

function SectionCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-4 mb-4">
      <h2 className="text-lg font-semibold mb-3">{title}</h2>
      {children}
    </div>
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
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b">
            {headers.map((h) => (
              <th key={h} className="text-left py-2 px-3">{h}</th>
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
      <div className="p-6">
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
      <section className="page-hero page-hero--dashboard">
        <div>
          <span className="page-hero__eyebrow">{translate("platformConfig.eyebrow")}</span>
          <h2 className="page-hero__title">
            {translate("navigation.pages.platform-configuration.title")}
          </h2>
          <p className="page-hero__description">
            {translate("platformConfig.readOnlyNotice")}
          </p>
        </div>
      </section>

      {/* Faculty Config */}
      <SectionCard title={translate("platformConfig.facultyConfig")}>
        <ConfigTable
          headers={facultyHeaders}
          rows={facultyConfigs}
          render={(row: any, i) => (
            <tr key={i} className="border-b last:border-0">
              <td className="py-2 px-3">{row.faculty_id}</td>
              <td className="py-2 px-3">{row.code}</td>
              <td className="py-2 px-3">{row.name}</td>
              <td className="py-2 px-3">{row.name_th}</td>
              <td className="py-2 px-3">{row.name_en}</td>
              <td className="py-2 px-3">
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
            <tr key={i} className="border-b last:border-0">
              <td className="py-2 px-3">{row.faculty_id ?? "—"}</td>
              <td className="py-2 px-3">{row.paper_distribution_division}</td>
              <td className="py-2 px-3">{row.max_supervision_sessions}</td>
              <td className="py-2 px-3">
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
            <tr key={i} className="border-b last:border-0">
              <td className="py-2 px-3">{row.faculty_id ?? "—"}</td>
              <td className="py-2 px-3">{row.flow_name}</td>
              <td className="py-2 px-3">
                {row.requires_governance_review ? translate("common.yes") : translate("common.no")}
              </td>
              <td className="py-2 px-3">{row.approval_quorum}</td>
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
            <tr key={i} className="border-b last:border-0">
              <td className="py-2 px-3">{row.system_code}</td>
              <td className="py-2 px-3">{row.integration_direction}</td>
              <td className="py-2 px-3">{row.data_domain}</td>
              <td className="py-2 px-3">{row.sync_mode}</td>
              <td className="py-2 px-3">{row.owner_unit}</td>
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
            <tr key={i} className="border-b last:border-0">
              <td className="py-2 px-3 font-mono text-xs">{row.metric_code}</td>
              <td className="py-2 px-3">{row.name}</td>
              <td className="py-2 px-3">{row.category}</td>
              <td className="py-2 px-3">{row.unit}</td>
              <td className="py-2 px-3">{row.pdpa_level}</td>
            </tr>
          )}
        />
      </SectionCard>
    </div>
  );
}