import { useGovernanceOverview } from "@/hooks/useGovernanceOverview";
import { translate } from "@/i18n";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import type { GovernanceEventItem, GovernanceOverview, FacultyGovernanceSummary } from "@/types/governance";

function RiskBadge({ severity }: { severity: string }) {
  const cls =
    severity === "critical" || severity === "high"
      ? "bg-red-100 text-red-800"
      : severity === "medium"
        ? "bg-yellow-100 text-yellow-800"
        : "bg-green-100 text-green-800";
  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${cls}`}>
      {severity.toUpperCase()}
    </span>
  );
}

function StatCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: React.ReactNode;
  sub?: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <p className="text-sm font-medium text-gray-500 mb-1">{label}</p>
      <p className="text-2xl font-bold">{value}</p>
      {sub ? <p className="text-xs text-gray-400 mt-1">{sub}</p> : null}
    </div>
  );
}

function HealthBand({ band }: { band: string }) {
  const cls =
    band === "green"
      ? "bg-green-100 text-green-800"
      : band === "amber"
        ? "bg-yellow-100 text-yellow-800"
        : "bg-red-100 text-red-800";
  return (
    <span className={`px-3 py-1 rounded text-sm font-medium ${cls}`}>
      {translate("governance.riskBand", { band: band.toUpperCase() })}
    </span>
  );
}

export const GovernanceCockpitPage = function GovernanceCockpit() {
  const { data, isLoading, error } = useGovernanceOverview();

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
          description={translate("governance.loadError")}
        />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<Icon name="info" />}
          title={translate("governance.noData")}
          description={translate("governance.noDataDesc")}
        />
      </div>
    );
  }

  // The backend returns GovernanceOverview. Cast confirms the type boundary at the component edge.
  const overview = data as GovernanceOverview;
  const { top_risks, recent_events, faculty_summary } = overview;
  const hasRisks = Array.isArray(top_risks) && top_risks.length > 0;
  const hasEvents = Array.isArray(recent_events) && recent_events.length > 0;
  const hasFaculty = Array.isArray(faculty_summary) && faculty_summary.length > 0;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{translate("navigation.pages.governance-cockpit.title")}</h1>
        <HealthBand band={overview.risk_band} />
      </div>

      {/* Health score card */}
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-2">{translate("governance.healthScore")}</h2>
        <div className="flex items-baseline">
          <span className="text-4xl font-bold">{overview.overall_health_score}</span>
          <span className="ml-2 text-sm text-gray-500">/ 100</span>
        </div>
        <p className="text-xs text-gray-400 mt-1">{translate("governance.healthNote")}</p>
      </div>

      {/* Blocker / escalation / publication grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label={translate("governance.blockers")} value={overview.blocker_count} />
        <StatCard label={translate("governance.overrides")} value={overview.override_count} />
        <StatCard label={translate("governance.rollbacks")} value={overview.rollback_count} />
        <StatCard label={translate("governance.escalations")} value={overview.escalation_count} />
        <StatCard label={translate("governance.publicationReady")} value={overview.publication_ready_count} />
        <StatCard label={translate("governance.publicationBlocked")} value={overview.publication_blocked_count} />
        <StatCard label={translate("governance.pendingApprovals")} value={overview.pending_approval_count} />
        <StatCard label={translate("governance.overdueSigning")} value={overview.overdue_signing_count} />
      </div>

        {/* Top risks */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-4">{translate("governance.topRisks")}</h2>
          {hasRisks ? (
            <ul className="space-y-2">
              {(top_risks as Array<{ risk: string; severity: string; category: string }>).map((risk, i) => (
                <li key={i} className="flex justify-between items-start">
                  <span className="flex-1">{risk.risk}</span>
                  <RiskBadge severity={risk.severity} />
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">{translate("governance.noRisks")}</p>
          )}
        </div>

        {/* Recent events feed */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-4">{translate("governance.recentEvents")}</h2>
          {hasEvents ? (
            <ul className="space-y-2">
              {(recent_events as GovernanceEventItem[]).slice(0, 20).map((evt, i) => (
                <li key={i} className="flex justify-between items-start text-sm">
                  <span className="flex-1">{evt.detail}</span>
                  <span className="ml-4 text-gray-400">{evt.event_type}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">{translate("governance.noEvents")}</p>
          )}
        </div>

      {/* Faculty governance summary */}
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-4">{translate("governance.facultySummary")}</h2>
        {hasFaculty ? (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-3">{translate("governance.faculty")}</th>
                  <th className="text-left py-2 px-3">{translate("governance.healthScore")}</th>
                  <th className="text-left py-2 px-3">{translate("governance.blockers")}</th>
                </tr>
              </thead>
                <tbody>
                  {(faculty_summary as FacultyGovernanceSummary[]).map((row) => (
                  <tr key={row.faculty_id} className="border-b last:border-0">
                    <td className="py-2 px-3">{row.faculty_name}</td>
                    <td className="py-2 px-3">{row.health_score}</td>
                    <td className="py-2 px-3">{row.blocker_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500">{translate("governance.noFacultyData")}</p>
        )}
      </div>
    </div>
  );
}
