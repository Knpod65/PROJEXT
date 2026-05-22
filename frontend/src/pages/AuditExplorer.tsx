import { useAuditExplorer } from "@/hooks/domain/useAuditExplorer";
import { renderTabButton } from "@/utils/presenters/auditPresenter";
import { translate } from "@/i18n";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Skeleton } from "@/components/ui/Skeleton";
import { Fragment } from "react";

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
          <span className="page-hero__eyebrow">{translate("audit.eyebrow")}</span>
          <h2 className="page-hero__title">{translate("navigation.pages.audit-explorer.title")}</h2>
        </div>
      </section>

      <div className="border-b mb-4">
        <div className="flex">
          {tabKeys.map(({ key, labelKey }) => (
            <Fragment key={key}>
              {renderTabButton({
                active: activeTab === key,
                onClick: () => setActiveTab(key),
                label: translate(labelKey),
              })}
            </Fragment>
          ))}
        </div>
      </div>

      {activeTab === "audit" && (
        <div className="overflow-x-auto">
          {auditEvents.length > 0 ? (
            <table className="min-w-full bg-white border">
              <thead className="bg-gray-50">
                <tr>
                  {columnHeaders.map(({ key: hk, labelKey }) => (
                    <th key={hk} className="px-4 py-2 text-left text-sm font-medium text-gray-700">
                      {translate(labelKey)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {auditEvents.map((e) => (
                  <tr key={e._id} className="border-t">
                    <td className="px-4 py-2 text-sm">{String(e.id ?? "-")}</td>
                    <td className="px-4 py-2 text-sm">{e.actor}</td>
                    <td className="px-4 py-2 text-sm">{e.action}</td>
                    <td className="px-4 py-2 text-sm">{e.table_name || "-"}</td>
                    <td className="px-4 py-2 text-sm">{new Date(e.timestamp).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState icon={<Icon name="info" />} title={translate(emptyStateKey)} />
          )}
        </div>
      )}

      {activeTab === "governance" && (
        <div>
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
        </div>
      )}

      {activeTab === "lifecycle" && (
        <div>
          <EmptyState icon={<Icon name="info" />} title={translate("lifecycleTimeline.placeholder")} />
        </div>
      )}
    </div>
  );
}
