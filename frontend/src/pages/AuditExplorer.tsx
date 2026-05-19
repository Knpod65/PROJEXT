import { useState } from "react";
import { useAuditEvents, useGovernanceTimeline, useLifecycleTimeline } from "@/hooks/useAuditExplorer";
import { translate } from "@/i18n";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";

type TabKey = "audit" | "governance" | "lifecycle";

export default function AuditExplorer() {
  const [tab, setTab] = useState<TabKey>("audit");
  const { data: auditEvents, isLoading: loadingAudit, error: errorAudit } = useAuditEvents();
  const { data: governance, isLoading: loadingGov, error: errorGov } = useGovernanceTimeline();
  const { data: lifecycle, isLoading: loadingLifecycle, error: errorLifecycle } = useLifecycleTimeline("");

  const TabButton = ({ active, onClick, label }: { active: boolean; onClick: () => void; label: string }) => (
    <button
      onClick={onClick}
      className={`px-4 py-2 text-sm font-medium border-b-2 ${
        active ? "border-blue-500 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"
      }`}
    >
      {label}
    </button>
  );

  if (loadingAudit || loadingGov || loadingLifecycle) {
    return (
      <div className="p-6">
        <p className="text-gray-500">{translate("common.loading")}</p>
      </div>
    );
  }

  if (errorAudit || errorGov || errorLifecycle) {
    return (
      <div className="p-6">
        <EmptyState icon={<Icon name="warning" />} title={translate("errors.requestFailed")} />
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">{translate("navigation.pages.audit-explorer.title")}</h1>

      <div className="border-b mb-4">
        <div className="flex">
          <TabButton active={tab === "audit"} onClick={() => setTab("audit")} label={translate("auditEvents.tab")} />
          <TabButton active={tab === "governance"} onClick={() => setTab("governance")} label={translate("governanceTimeline.tab")} />
          <TabButton active={tab === "lifecycle"} onClick={() => setTab("lifecycle")} label={translate("lifecycleTimeline.tab")} />
        </div>
      </div>

      {tab === "audit" && (
        <div className="overflow-x-auto">
          {auditEvents && auditEvents.length > 0 ? (
            <table className="min-w-full bg-white border">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">ID</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Actor</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Action</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Table</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Time</th>
                </tr>
              </thead>
              <tbody>
                {auditEvents.map((e) => (
                  <tr key={e.id} className="border-t">
                    <td className="px-4 py-2 text-sm">{e.id}</td>
                    <td className="px-4 py-2 text-sm">{e.actor}</td>
                    <td className="px-4 py-2 text-sm">{e.action}</td>
                    <td className="px-4 py-2 text-sm">{e.table_name || "-"}</td>
                    <td className="px-4 py-2 text-sm">{new Date(e.timestamp).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState icon={<Icon name="info" />} title={translate("auditEvents.noData")} />
          )}
        </div>
      )}

      {tab === "governance" && (
        <div>
          {governance && governance.length > 0 ? (
            <ul className="space-y-2">
              {governance.map((e) => (
                <li key={e.id} className="border-l-4 border-blue-500 pl-4 py-2">
                  <div className="font-medium">{e.actor}</div>
                  <div className="text-sm text-gray-600">{e.action}</div>
                  <div className="text-xs text-gray-400">{new Date(e.timestamp).toLocaleString()}</div>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState icon={<Icon name="info" />} title={translate("governanceTimeline.noData")} />
          )}
        </div>
      )}

      {tab === "lifecycle" && (
        <div>
          <EmptyState icon={<Icon name="info" />} title={translate("lifecycleTimeline.placeholder")} />
        </div>
      )}
    </div>
  );
}