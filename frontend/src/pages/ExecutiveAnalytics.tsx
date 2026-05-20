import { useExecutiveAnalyticsPage } from '@/hooks/domain/useExecutiveAnalyticsPage';

const ExecutiveAnalytics: React.FC = () => {
  const {
    isLoading,
    error,
    data,
    healthBandColor,
    severityBandColor,
    priorityBandColor,
    kpiGrid,
    topRisks,
    recommendedActions,
    scoreSuffix,
  } = useExecutiveAnalyticsPage();

  if (isLoading) return <div>Loading executive analytics...</div>;
  if (error) return <div>Error loading executive analytics: {(error as Error).message}</div>;
  if (!data) return <div>No data available</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Executive Analytics</h1>
      
      {/* Health Score Card */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-2">Overall Health Score</h2>
        <div className="flex items-baseline">
          <span className="text-4xl font-bold">{data.overall_health_score}</span>
          <span className="ml-2 text-sm text-gray-500">{scoreSuffix}</span>
        </div>
        <div className="mt-2">
          <span className={`px-3 py-1 rounded text-sm font-medium ${healthBandColor}`}>
            Risk Band: {data.risk_band.toUpperCase()}
          </span>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {kpiGrid.map((kpi) => (
          <div key={kpi.key} className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-2">{kpi.label}</h3>
            <p className="text-2xl font-bold">{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Top Risks */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-4">Top Risks</h2>
        {topRisks.length === 0 ? (
          <p className="text-gray-500">No risks identified</p>
        ) : (
          <ul className="space-y-2">
            {topRisks.map((risk, index) => (
              <li key={index} className="flex justify-between items-start">
                <span className="flex-1">{risk.risk}</span>
                <span className={`px-2 py-1 rounded-text-xs ${risk.severityColor}`}>
                  {risk.severity.toUpperCase()}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Recommended Actions */}
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-4">Recommended Actions</h2>
        {recommendedActions.length === 0 ? (
          <p className="text-gray-500">No actions recommended</p>
        ) : (
          <ul className="space-y-2">
            {recommendedActions.map((action, index) => (
              <li key={index} className="flex justify-between items-start">
                <span className="flex-1">{action.action}</span>
                <span className="flex-none">
                  <span className={`px-2 py-1 rounded-text-xs ${action.priorityColor}`}>
                    {action.priority.toUpperCase()}
                  </span>
                  <span className="ml-2 text-xs text-gray-500">
                    by {action.owner}
                  </span>
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default ExecutiveAnalytics;