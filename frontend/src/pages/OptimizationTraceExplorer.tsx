import { useOptimizationTraceExplorer } from "@/hooks/domain/useOptimizationTraceExplorer";
import { translate } from "@/i18n";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";

function SeverityBadge({ severity }: { severity: string }) {
  const cls =
    severity === "error" || severity === "critical"
      ? "bg-red-100 text-red-800"
      : severity === "warning"
        ? "bg-yellow-100 text-yellow-800"
        : "bg-gray-100 text-gray-800";
  const label = translate(`severity.${severity}`) || severity.toUpperCase();
  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${cls}`}>
      {label}
    </span>
  );
}

function ScoreRing({ score }: { score: number }) {
  const pct = Math.min(Math.max(score, 0), 100);
  const r = 24;
  const circumference = 2 * Math.PI * r;
  const offset = circumference - (pct / 100) * circumference;

  return (
    <div className="flex items-center gap-3">
      <svg width="64" height="64" className="flex-shrink-0">
        <circle cx="32" cy="32" r={r} fill="none" stroke="#e5e7eb" strokeWidth="4" />
        <circle
          cx="32"
          cy="32"
          r={r}
          fill="none"
          stroke={pct >= 80 ? "#16a34a" : pct >= 50 ? "#ca8a04" : "#dc2626"}
          strokeWidth="4"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 32 32)"
        />
      </svg>
      <div>
        <p className="text-2xl font-bold">{score}</p>
        <p className="text-xs text-gray-400">{translate("trace.qualityOf100")}</p>
      </div>
    </div>
  );
}

export default function OptimizationTraceExplorer() {
  const {
    isLoading,
    error,
    refresh,
    trace,
    traceSummary,
    timelineItems,
    rejectedAlternatives,
    constraintItems,
    selectedSessionId,
    setSelectedSessionId,
    mockSessions,
    hasData,
    emptyStateKey,
  } = useOptimizationTraceExplorer();

  if (isLoading) {
    return (
      <div className="p-6">
        <p className="text-gray-500">{translate("common.loading")}</p>
      </div>
    );
  }

  if (error || !trace) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<Icon name="search_off" />}
          title={translate("trace.noData")}
          description={
            error
              ? translate("trace.loadError")
              : translate("trace.selectSessionHint")
          }
        />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{translate("trace.pageTitle")}</h1>
          <p className="text-sm text-gray-500">
            {translate("trace.sessionLabel")}: {mockSessions.find((s) => s.id === selectedSessionId)?.label}
          </p>
        </div>
        <ScoreRing score={traceSummary.overallQualityScore} />
      </div>

      {trace.quality_note ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">
          {trace.quality_note}
        </div>
      ) : null}

      {/* Trace events timeline */}
      {timelineItems.length > 0 ? (
        <div className="bg-white rounded-lg shadow p-4 space-y-2">
          <h2 className="text-lg font-semibold mb-3">{translate("trace.events")}</h2>
          {timelineItems.map((evt) => (
            <div key={evt.id} className="flex items-start justify-between border-b pb-2 last:border-0">
              <div>
                <p className="font-medium text-sm">{evt.detail}</p>
                <p className="text-xs text-gray-400">{evt.event_type} · {evt.stage}</p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <p className="text-xs text-gray-400">
                  {new Date(evt.timestamp).toLocaleTimeString()}
                </p>
                <SeverityBadge severity={evt.severity} />
              </div>
            </div>
          ))}
        </div>
      ) : null}

      {/* Candidate table */}
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-3">
          {translate("trace.candidates")} ({trace.candidates.length})
        </h2>
        {trace.candidates.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-3">{translate("trace.room")}</th>
                  <th className="text-left py-2 px-3">{translate("trace.timeslot")}</th>
                  <th className="text-left py-2 px-3">{translate("trace.staff")}</th>
                  <th className="text-right py-2 px-3">{translate("trace.score")}</th>
                  <th className="text-left py-2 px-3">{translate("trace.status")}</th>
                  <th className="text-left py-2 px-3">{translate("trace.rejectionReasons")}</th>
                </tr>
              </thead>
              <tbody>
                {trace.candidates.map((c, i) => (
                  <tr key={i} className="border-b last:border-0">
                    <td className="py-2 px-3">{c.room_code}</td>
                    <td className="py-2 px-3">{c.timeslot}</td>
                    <td className="py-2 px-3">{c.staff_id}</td>
                    <td className="py-2 px-3 text-right">{c.score}</td>
                    <td className="py-2 px-3">
                      <SeverityBadge severity={c.selected ? "info" : "hard"} />
                    </td>
                    <td className="py-2 px-3 text-xs text-gray-500">
                      {c.rejection_reasons.join(", ") || translate("common.none")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500 text-sm">{translate("trace.noCandidates")}</p>
        )}
      </div>

      {/* Constraint hits */}
      {constraintItems.length > 0 ? (
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-3">
            {translate("trace.constraints")} ({constraintItems.length})
          </h2>
          <div className="space-y-2">
            {constraintItems.map((c, i) => (
              <div key={i} className="flex items-start justify-between border-b pb-2 last:border-0">
                <div>
                  <p className="font-medium text-sm">{c.constraint_type}</p>
                  <p className="text-xs text-gray-500">{c.detail}</p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <SeverityBadge severity={c.severity === "hard" ? "critical" : "warning"} />
                  <SeverityBadge severity={c.passed ? "info" : "error"} />
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {/* Recheck issues */}
      {trace.recheck_issues.length > 0 ? (
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-3">
            {translate("trace.recheckIssues")} ({trace.recheck_issues.length})
          </h2>
          <ul className="space-y-1">
            {trace.recheck_issues.map((issue, i) => (
              <li key={i} className="flex items-center gap-2 text-sm">
                <SeverityBadge severity={issue.severity} />
                <span>{issue.issue}</span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
