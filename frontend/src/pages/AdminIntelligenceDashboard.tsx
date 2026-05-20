/** AdminIntelligenceDashboard — OPS-DASH: Admin 10-group significant metrics dashboard. */

import { Link } from "react-router-dom";
import type { AdminIntelligenceDashboard } from "@/types/dashboardMetrics";
import { useAdminIntelligenceDashboard } from "@/hooks/domain/useAdminIntelligenceDashboard";
import { usePermission } from "@/hooks/usePermission";
import { translate } from "@/i18n";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Skeleton } from "@/components/ui/Skeleton";
import { PermissionDeniedState } from "@/components/system/PermissionDeniedState";
import { presentMetricCard, presentMetricGroup } from "@/utils/presenters/dashboardMetricPresenter";

const GROUP_ORDER = [
  "examOperations",
  "optimizationQuality",
  "governanceApproval",
  "staffWorkload",
  "roomCapacity",
  "teacherSubmission",
  "printExport",
  "qrPickup",
  "pdpaSecurity",
  "systemOperations",
];

function riskChipClass(band: string | null | undefined): string {
  if (band === "red") return "bg-red-100 text-red-800";
  if (band === "amber") return "bg-amber-100 text-amber-800";
  return "bg-green-100 text-green-800";
}

function scoreToBand(score: number): string {
  if (score >= 75) return "green";
  if (score >= 50) return "amber";
  return "red";
}

export default function AdminIntelligenceDashboard() {
  const { canManageUsers } = usePermission();
  const { data, isLoading, isError } = useAdminIntelligenceDashboard();

  if (!canManageUsers) {
    return <PermissionDeniedState />;
  }

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-6">
        <EmptyState
          icon={<Icon name="warning" />}
          title={translate("dashboard.admin.loadErrorTitle")}
        />
      </div>
    );
  }

  const score = data.overall_health_score ?? 0;
  const band = data.overall_risk_band ?? scoreToBand(score);

  // Collect critical alerts across all groups
  const criticalAlerts = data.groups.flatMap((g) =>
    g.metrics
      .filter((m) => m.severity === "critical")
      .map((m) => ({
        code: m.metric_code,
        titleKey: m.title_i18n_key,
        whyKey: m.why_it_matters_i18n_key,
      })),
  );

  // Sort groups by defined order
  const orderedGroups = [...data.groups].sort(
    (a, b) => GROUP_ORDER.indexOf(a.group_code) - GROUP_ORDER.indexOf(b.group_code),
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">
          {translate("dashboard.admin.title")}
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          {translate("dashboard.admin.lastUpdated")}:{" "}
          {data.last_computed_at
            ? new Date(data.last_computed_at).toLocaleString()
            : "—"}
        </p>
      </div>

      {/* Health Banner */}
      <Card className="p-4 flex flex-wrap items-center gap-4">
        <div className={`px-3 py-1 rounded-full text-sm font-semibold ${riskChipClass(band)}`}>
          {translate("dashboard.admin.riskBand")}: {translate(`dashboard.band.${band}`)}
        </div>
        <span className="text-sm">
          {translate("dashboard.admin.overallHealth")}:{" "}
          <strong>{score.toFixed(1)}</strong>
          <span className="text-gray-400"> / 100</span>
        </span>
      </Card>

      {/* Critical Alerts */}
      {criticalAlerts.length > 0 && (
        <Card className="p-4 border-2 border-red-200 bg-red-50">
          <h2 className="text-base font-semibold text-red-800 mb-3">
            {translate("dashboard.admin.criticalAlerts")}
          </h2>
          <ul className="space-y-1">
            {criticalAlerts.slice(0, 5).map((a) => (
              <li key={a.code} className="text-sm text-red-700">
                {translate(a.titleKey)}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Metric Groups */}
      {orderedGroups.map((group) => {
        const presented = presentMetricGroup(group);
        return (
          <Card key={group.group_code} className="p-4 space-y-4">
            <div>
              <h2 className="text-lg font-semibold">{presented.title}</h2>
              {presented.description && (
                <p className="text-sm text-gray-500">{presented.description}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {presented.metricCards.map((m) => (
                <div
                  key={m.drilldownHref || m.title}
                  className="border rounded-lg p-3 space-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-400 uppercase tracking-wide">
                      {m.title}
                    </span>
                    {m.pdpaBadge && (
                      <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">
                        {m.pdpaBadge}
                      </span>
                    )}
                  </div>
                  <div className="flex items-end gap-2">
                    <span className="text-2xl font-bold">{m.value}</span>
                    {m.unit && (
                      <span className="text-xs text-gray-400 pb-0.5">{m.unit}</span>
                    )}
                  </div>
                  <div
                    className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${m.severityColorClass}`}
                  >
                    {m.severity}
                  </div>
                  {m.whyItMatters && (
                    <p className="text-xs text-gray-500 line-clamp-2">{m.whyItMatters}</p>
                  )}
                  {m.recommendedAction && (
                    <p className="text-xs text-blue-600">{m.recommendedAction}</p>
                  )}
                </div>
              ))}
            </div>

            {presented.actions.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {presented.actions.map((action, idx) => (
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
        );
      })}
    </div>
  );
}
