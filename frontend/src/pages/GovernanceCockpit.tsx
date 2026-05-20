import { useGovernanceCockpit } from "@/hooks/domain/useGovernanceCockpit";
import { translate } from "@/i18n";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";

function RiskBadge({ severity }: { severity: string }) {
  const cls =
    severity === "critical" || severity === "high"
      ? "bg-red-100 text-red-800"
      : severity === "medium"
        ? "bg-yellow-100 text-yellow-800"
        : "bg-green-100 text-green-800";
  const label = translate(`severity.${severity}`) || severity.toUpperCase();
  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${cls}`}>
      {label}
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
      <div className="p-6">
        <p className="text-gray-500">{translate("common.loading")}</p>
      </div>
    );
  }

  if (error || !overview) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<Icon name={error ? "warning" : "info"} />}
          title={translate(error ? "errors.requestFailed" : "governance.noData")}
          description={error ? translate("governance.loadError") : translate("governance.noDataDesc")}
        />
      </div>
    );
  }

  const { top_risks, recent_events, faculty_summary } = overview;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{translate("navigation.pages.governance-cockpit.title")}</h1>
        <HealthBand band={healthBadgeBand} />
      </div>

      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-2">{translate("governance.healthScore")}</h2>
        <div className="flex items-baseline">
          <span className="text-4xl font-bold">{governanceHealth}</span>
          <span className="ml-2 text-sm text-gray-500">{translate("governance.of100")}</span>
        </div>
        <p className="text-xs text-gray-400 mt-1">{translate("governance.healthNote")}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {summaryCards.map((card) => (
          <StatCard key={card.key} label={card.label} value={card.value} />
        ))}
      </div>

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

      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-4">{translate("governance.recentEvents")}</h2>
        {hasEvents ? (
          <ul className="space-y-2">
            {(recent_events as Array<{ event_type: string; detail: string; timestamp: string }>).map((evt, i) => (
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
                {(faculty_summary as Array<{ faculty_id: string; faculty_name: string; health_score: number; blocker_count: number }>).map((row) => (
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
};
