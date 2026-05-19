import { usePlatformConfig } from "@/hooks/usePlatformConfig";
import { translate } from "@/i18n";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";

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
  const { data, isLoading, error } = usePlatformConfig();

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
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">
          {translate("navigation.pages.platform-configuration.title")}
        </h1>
        <span className="text-xs text-gray-400">
          {translate("platformConfig.readOnlyNotice")}
        </span>
      </div>

      {/* Faculty Config */}
      <SectionCard title={translate("platformConfig.facultyConfig")}>
        <ConfigTable
          headers={[
            translate("platformConfig.table.id"),
            translate("platformConfig.table.code"),
            translate("platformConfig.table.nameTh"),
            translate("platformConfig.table.nameEn"),
            translate("platformConfig.table.active"),
          ]}
          rows={data.faculty_configs}
          render={(row: any, i) => (
            <tr key={i} className="border-b last:border-0">
              <td className="py-2 px-3">{row.faculty_id}</td>
              <td className="py-2 px-3">{row.code}</td>
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
          headers={[
            translate("platformConfig.table.facultyId"),
            translate("platformConfig.table.division"),
            translate("platformConfig.table.maxSupervision"),
            translate("platformConfig.table.crossDept"),
          ]}
          rows={(data as any).workload_policies}
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
          headers={["Faculty ID", "Flow Name", "Requires Review", "Quorum"]}
          rows={(data as any).governance_flows}
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
          headers={["System", "Direction", "Domain", "Sync Mode", "Owner Unit"]}
          rows={(data as any).integration_contracts}
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
          headers={["Code", "Name", "Category", "Unit", "PDPA Level"]}
          rows={(data as any).analytics_metrics}
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
