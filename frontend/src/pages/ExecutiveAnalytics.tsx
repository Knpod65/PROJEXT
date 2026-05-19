import { useExecutiveAnalytics } from '@/hooks/useExecutiveAnalytics';

const ExecutiveAnalytics: React.FC = () => {
  const { data, isLoading, error } = useExecutiveAnalytics();

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
          <span className="ml-2 text-sm text-gray-500">/ 100</span>
        </div>
        <div className="mt-2">
          <span 
            className={`px-3 py-1 rounded text-sm font-medium 
              ${data.risk_band === 'green' ? 'bg-green-100 text-green-800' 
              : data.risk_band === 'amber' ? 'bg-yellow-100 text-yellow-800' 
              : 'bg-red-100 text-red-800'}`}
          >
            Risk Band: {data.risk_band.toUpperCase()}
          </span>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Optimization Quality</h3>
          <p className="text-2xl font-bold">{data.optimization_quality_avg}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Governance Blockers</h3>
          <p className="text-2xl font-bold">{data.governance_blocker_count}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Publication Ready</h3>
          <p className="text-2xl font-bold">{data.publication_ready_count}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Workload Balance</h3>
          <p className="text-2xl font-bold">{data.workload_balance_score}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Room Utilization</h3>
          <p className="text-2xl font-bold">{data.room_utilization_score}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-2">PDPA Alerts</h3>
          <p className="text-2xl font-bold">{data.pdpa_alert_count}</p>
        </div>
      </div>

      {/* Top Risks */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-4">Top Risks</h2>
        {data.top_risks.length === 0 ? (
          <p className="text-gray-500">No risks identified</p>
        ) : (
          <ul className="space-y-2">
            {data.top_risks.map((risk, index) => (
              <li key={index} className="flex justify-between items-start">
                <span className="flex-1">{risk.risk}</span>
                <span className={`px-2 py-1 rounded-text-xs 
                  ${risk.severity === 'high' ? 'bg-red-100 text-red-800' 
                  : risk.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' 
                  : 'bg-green-100 text-green-800'}`}
                >
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
        {data.recommended_actions.length === 0 ? (
          <p className="text-gray-500">No actions recommended</p>
        ) : (
          <ul className="space-y-2">
            {data.recommended_actions.map((action, index) => (
              <li key={index} className="flex justify-between items-start">
                <span className="flex-1">{action.action}</span>
                <span className="flex-none">
                  <span className={`px-2 py-1 rounded-text-xs 
                    ${action.priority === 'high' ? 'bg-red-100 text-red-800' 
                    : action.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' 
                    : 'bg-green-100 text-green-800'}`}
                  >
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