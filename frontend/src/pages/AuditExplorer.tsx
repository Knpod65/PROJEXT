import { useAuditExplorer } from "@/hooks/domain/useAuditExplorer";
import { translate } from "@/i18n";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { DataTable, type DataTableColumn } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";

type AuditEventRow = {
  _id: string | number;
  action: string;
  actor: string;
  id?: string | number | null;
  table_name?: string | null;
  timestamp: string;
};

export default function AuditExplorer() {
  const {
    activeTab,
    setActiveTab,
    auditEvents,
    governanceEvents,
    lifecycleEvents,
    error,
    errorAudit,
    errorGov,
    errorLifecycle,
    isLoading,
    columnHeaders,
    tabKeys,
    emptyStateKey,
  } = useAuditExplorer();

  const anyError = !!error;
  const loading = isLoading;
  const consoleEyebrow = translate("audit.consoleEyebrow");
  const tabItems = tabKeys.map(({ key, labelKey }) => {
    const badge =
      key === "audit"
        ? auditEvents.length
        : key === "governance" && Array.isArray(governanceEvents)
          ? governanceEvents.length
          : key === "lifecycle" && Array.isArray(lifecycleEvents)
            ? lifecycleEvents.length
            : undefined;

    return {
      key,
      label: translate(labelKey),
      badge,
    };
  });
  const auditColumns: Array<DataTableColumn<AuditEventRow>> = columnHeaders.map(({ key, labelKey }) => {
    if (key === "id") {
      return { key, label: translate(labelKey), width: "110px", render: (row) => String(row.id ?? "-") };
    }
    if (key === "timestamp") {
      return { key, label: translate(labelKey), minWidth: "180px", render: (row) => new Date(row.timestamp).toLocaleString() };
    }
    return { key, label: translate(labelKey), minWidth: key === "action" ? "180px" : "140px" };
  });

  if (loading) {
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

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        className="page-hero--dashboard"
        eyebrow={consoleEyebrow}
        title={translate("navigation.pages.audit-explorer.title")}
      />

      <Card title={translate("auditEvents.tab")} subtitle={consoleEyebrow}>
        <Tabs activeKey={activeTab} items={tabItems} onChange={setActiveTab} />
      </Card>

      {activeTab === "audit" && (
        <Card
          title={translate("auditEvents.tab")}
          subtitle={translate("navigation.pages.audit-explorer.title")}
          actions={<Badge variant="navy">{auditEvents.length}</Badge>}
        >
          {auditEvents.length > 0 ? (
            <DataTable
              columns={auditColumns}
              rows={auditEvents as AuditEventRow[]}
              rowKey={(row) => row._id}
              tableLayout="fixed"
              compact
            />
          ) : (
            <EmptyState icon={<Icon name="info" />} title={translate(emptyStateKey)} />
          )}
        </Card>
      )}

      {activeTab === "governance" && (
        <Card
          title={translate("governanceTimeline.tab")}
          subtitle={consoleEyebrow}
          actions={<Badge variant="blue">{Array.isArray(governanceEvents) ? governanceEvents.length : 0}</Badge>}
        >
          {Array.isArray(governanceEvents) && (governanceEvents as unknown[]).length > 0 ? (
            <ul className="timeline-list">
              {(governanceEvents as unknown[]).map((evt: unknown, index) => {
                const row = evt as Record<string, unknown>;
                return (
                  <li
                    key={String(row.id ?? index)}
                    className="timeline-list__item"
                  >
                    <div>
                      <strong>{String(row.actor ?? "-")}</strong>
                      <p>{String(row.action ?? "-")}</p>
                    </div>
                    <div className="timeline-list__meta">
                      {new Date(String(row.timestamp ?? "")).toLocaleString()}
                    </div>
                  </li>
                );
              })}
            </ul>
          ) : (
            <EmptyState icon={<Icon name="info" />} title={translate("governanceTimeline.noData")} />
          )}
        </Card>
      )}

      {activeTab === "lifecycle" && (
        <Card title={translate("lifecycleTimeline.tab")} subtitle={consoleEyebrow}>
          <EmptyState icon={<Icon name="info" />} title={translate("lifecycleTimeline.placeholder")} />
        </Card>
      )}
    </div>
  );
}
