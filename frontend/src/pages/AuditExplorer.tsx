import { useAuditExplorer } from "@/hooks/domain/useAuditExplorer";
import { translate } from "@/i18n";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";

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
      <section className="page-hero page-hero--dashboard">
        <div>
          <span className="page-hero__eyebrow">{consoleEyebrow}</span>
          <h2 className="page-hero__title">{translate("navigation.pages.audit-explorer.title")}</h2>
        </div>
      </section>

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
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    {columnHeaders.map(({ key: hk, labelKey }) => (
                      <th key={hk}>{translate(labelKey)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {auditEvents.map((e) => (
                    <tr key={e._id}>
                      <td>{String(e.id ?? "-")}</td>
                      <td>{e.actor}</td>
                      <td>{e.action}</td>
                      <td>{e.table_name || "-"}</td>
                      <td>{new Date(e.timestamp).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
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
            <ul className="space-y-2">
              {(governanceEvents as unknown[]).map((evt: unknown, index) => {
                const row = evt as Record<string, unknown>;
                return (
                  <li
                    key={String(row.id ?? index)}
                    className="border-l-4 border-blue-500 pl-4 py-2"
                  >
                    <div className="font-medium">{String(row.actor ?? "-")}</div>
                    <div className="text-sm text-gray-600">{String(row.action ?? "-")}</div>
                    <div className="text-xs text-gray-400">
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
