/** dashboardMetricPresenter — shape raw OPS-DASH metrics for UI rendering. */

import { translateWithFallback } from "@/i18n";
import type {
  DashboardMetric,
  DashboardMetricGroup,
} from "@/types/dashboardMetrics";

export interface MetricCardDisplay {
  title: string;
  description: string;
  value: string;
  unit: string;
  severity: "good" | "info" | "warning" | "critical";
  severityColorClass: string;
  trendLabel: string;
  whyItMatters: string;
  recommendedAction: string;
  updatedAt: string | null;
  drilldownHref: string | null;
  pdpaBadge: string | null;
}

export function presentMetricCard(metric: DashboardMetric): MetricCardDisplay {
  const title = translateWithFallback(metric.title_i18n_key, metric.metric_code);
  const description = translateWithFallback(metric.description_i18n_key, "");
  const why = translateWithFallback(metric.why_it_matters_i18n_key, "");
  const action = translateWithFallback(metric.recommended_action_i18n_key, "");
  const trendLabel = translateWithFallback(metric.trend_label_i18n_key, metric.trend);
  const severity = metric.severity || "info";
  const { colorClass } = getSeverityDisplay(metric.severity);
  return {
    title,
    description,
    value: presentMetricValue(metric.value),
    unit: safeString(metric.unit, ""),
    severity,
    severityColorClass: colorClass,
    trendLabel,
    whyItMatters: safeString(why, ""),
    recommendedAction: safeString(action, ""),
    updatedAt: metric.updated_at || null,
    drilldownHref: metric.drilldown_route || null,
    pdpaBadge: metric.pdpa_level !== "public" ? metric.pdpa_level : null,
  };
}

export function presentMetricGroup(
  group: DashboardMetricGroup,
) {
  return {
    title: translateWithFallback(group.title_i18n_key, group.group_code),
    description: translateWithFallback(group.description_i18n_key, ""),
    metricCards: group.metrics.map(presentMetricCard),
    alerts: group.alerts,
    actions: group.recommended_actions.map((action) => translateWithFallback(action, action)),
  };
}

function safeString(value: any, fallback = ""): string {
  return value != null ? String(value) : fallback;
}

function presentMetricValue(value: DashboardMetric["value"] | null | undefined): string {
  if (value === null || value === undefined) {
    return "";
  }

  return String(value);
}

function getSeverityDisplay(
  severity: string,
): { colorClass: string; icon: string } {
  switch (severity) {
    case "critical":
      return { colorClass: "bg-red-50 text-red-700 border-red-200", icon: "error" };
    case "warning":
      return { colorClass: "bg-amber-50 text-amber-700 border-amber-200", icon: "warning" };
    case "good":
      return { colorClass: "bg-green-50 text-green-700 border-green-200", icon: "check_circle" };
    default:
      return { colorClass: "bg-blue-50 text-blue-700 border-blue-200", icon: "info" };
  }
}
