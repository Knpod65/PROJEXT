/** RoleDashboard — OPS-DASH: role-specific dashboard for non-admin roles. */

import type { RoleDashboardPayload } from "@/types/dashboardMetrics";
import { useRoleDashboard } from "@/hooks/domain/useRoleDashboard";
import { useAuth } from "@/store/auth.store";
import { translate, translateWithFallback } from "@/i18n";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Skeleton } from "@/components/ui/Skeleton";
import { presentMetricCard, presentMetricGroup } from "@/utils/presenters/dashboardMetricPresenter";

function MetricCardRow({ card }: { card: ReturnType<typeof presentMetricCard> }) {
  return (
    <div className="border rounded-lg p-3 space-y-1">
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-400 uppercase tracking-wide">{card.title}</span>
        {card.pdpaBadge && (
          <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">
            {card.pdpaBadge}
          </span>
        )}
      </div>
      <div className="flex items-end gap-2">
        <span className="text-2xl font-bold">{card.value}</span>
        {card.unit && (
          <span className="text-xs text-gray-400 pb-0.5">{card.unit}</span>
        )}
      </div>
      <div
        className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${card.severityColorClass}`}
      >
        {translateWithFallback(`severity.${card.severity}`, card.severity)}
      </div>
      {card.whyItMatters && (
        <p className="text-xs text-gray-500 line-clamp-2">{card.whyItMatters}</p>
      )}
    </div>
  );
}

export default function RoleDashboard() {
  const { user } = useAuth();
  const { data, isLoading, isError } = useRoleDashboard();

  if (isLoading) {
    return (
      <div className="page-stack page-stack--spacious">
        <div className="stitch-metric-grid">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="dashboard-skeleton" />
          ))}
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="page-stack page-stack--spacious">
        <EmptyState
          icon={<Icon name="warning" />}
          title={translate("dashboard.role.loadErrorTitle")}
        />
      </div>
    );
  }

  if (data.unauthorized) {
    return (
      <div className="page-stack page-stack--spacious">
        <EmptyState
          icon={<Icon name="block" />}
          title={translate("dashboard.role.unauthorizedTitle")}
          description={translate("dashboard.role.unauthorizedDescription")}
        />
      </div>
    );
  }

  const presentedGroups = data.groups.map(presentMetricGroup);

  return (
    <div className="p-6 space-y-6">
  <div>
    <h1 className="text-2xl font-bold">
      {translate(data.role_label_i18n_key)}
    </h1>
    {data.summary.last_updated && (
      <p className="text-sm text-gray-500 mt-1">
        {translate("dashboard.admin.lastUpdated")}:{" "}
        {new Date(data.summary.last_updated).toLocaleString()}
      </p>
    )}
  </div>

      {presentedGroups.map((group) => (
        <Card key={group.title} className="p-4 space-y-4">
          <div>
            <h2 className="text-lg font-semibold">{group.title}</h2>
            {group.description && (
              <p className="text-sm text-gray-500">{group.description}</p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {group.metricCards.map((card) => (
              <MetricCardRow key={card.title} card={card} />
            ))}
          </div>

          {group.actions.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {group.actions.map((action, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-gray-100 rounded text-sm text-gray-700"
                >
                  {action}
                </span>
              ))}
            </div>
          )}
        </Card>
      ))}

      {presentedGroups.length === 0 && (
        <EmptyState
          icon={<Icon name="info" />}
          title={translate("dashboard.role.noDataTitle")}
          description={translate("dashboard.role.noDataDescription")}
        />
      )}
    </div>
  );
}
