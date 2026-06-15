import type {
  AdminIntelligenceDashboard,
  DashboardMetric,
  DashboardMetricGroup,
} from "@/types/dashboardMetrics";
import type { TranslationParams } from "@/i18n";

export type AdminDisplayState =
  | "healthy"
  | "informational"
  | "warning"
  | "critical"
  | "notMeasured"
  | "unavailable";

export type AdminDetailTab = "scheduling" | "governance" | "people" | "delivery" | "system";

type Translator = (key: string, params?: TranslationParams) => string;

export interface AdminMetricDisplay {
  actionHref: string | null;
  actionLabel: string;
  description: string;
  groupCode: string;
  groupTitle: string;
  metricCode: string;
  numericValue: number | null;
  progress: number | null;
  restricted: boolean;
  state: AdminDisplayState;
  stateLabel: string;
  title: string;
  unit: string;
  value: string;
  whyItMatters: string;
}

export interface AdminDashboardDisplay {
  detailGroups: Array<{
    description: string;
    groupCode: string;
    metrics: AdminMetricDisplay[];
    tab: AdminDetailTab;
    title: string;
  }>;
  metrics: AdminMetricDisplay[];
  priorities: AdminMetricDisplay[];
  score: number | null;
  scoreState: AdminDisplayState;
}

const PLACEHOLDER_METRICS = new Set(["print_queue_size", "qr_redeems_24h"]);

const ACTION_ROUTES: Record<string, string> = {
  unscheduled_sections: "/schedule",
  scheduled_sections: "/schedule",
  rooms_in_use: "/rooms-v2",
  optimization_quality_avg: "/optimizer-trace",
  blocker_count: "/governance",
  pending_approvals: "/governance",
  staff_imbalance_score: "/workload-duty-analytics",
  room_utilization_score: "/rooms-v2",
  submission_rate: "/submissions",
  print_queue_size: "/printreview",
  pdpa_alert_count_24h: "/audit-explorer",
  api_uptime_pct: "/operational-health",
  db_ok: "/operational-health",
  storage_usage_pct: "/operational-health",
};

const GROUP_TABS: Record<string, AdminDetailTab> = {
  examOperations: "scheduling",
  optimizationQuality: "scheduling",
  roomCapacity: "scheduling",
  governanceApproval: "governance",
  pdpaSecurity: "governance",
  staffWorkload: "people",
  teacherSubmission: "people",
  printExport: "delivery",
  qrPickup: "delivery",
  systemOperations: "system",
};

const STATE_PRIORITY: Record<AdminDisplayState, number> = {
  critical: 0,
  warning: 1,
  unavailable: 2,
  informational: 3,
  notMeasured: 4,
  healthy: 5,
};

function numeric(value: DashboardMetric["value"]): number | null {
  const result = Number(value);
  return Number.isFinite(result) ? result : null;
}

function classifyMetric(metric: DashboardMetric): AdminDisplayState {
  const value = numeric(metric.value);
  if (value === null) return "unavailable";
  if (PLACEHOLDER_METRICS.has(metric.metric_code)) return "notMeasured";

  switch (metric.metric_code) {
    case "api_uptime_pct":
      return value >= 99.5 ? "healthy" : value >= 99 ? "warning" : "critical";
    case "db_ok":
      return value >= 1 ? "healthy" : "critical";
    case "storage_usage_pct":
      return value >= 90 ? "critical" : value >= 80 ? "warning" : "healthy";
    case "optimization_quality_avg":
      return value === 0 ? "notMeasured" : value >= 80 ? "healthy" : value >= 60 ? "informational" : value >= 40 ? "warning" : "critical";
    case "room_utilization_score":
      return value === 0 ? "notMeasured" : value >= 60 && value <= 80 ? "healthy" : value > 90 ? "warning" : "informational";
    case "submission_rate":
      return value === 0 ? "notMeasured" : value >= 95 ? "healthy" : value >= 80 ? "informational" : value >= 60 ? "warning" : "critical";
    case "unscheduled_sections":
      return value === 0 ? "healthy" : value <= 10 ? "warning" : "critical";
    case "blocker_count":
    case "pdpa_alert_count_24h":
      return value === 0 ? "healthy" : value < 5 ? "warning" : "critical";
    case "staff_imbalance_score":
      return value <= 0.3 ? "healthy" : value <= 0.5 ? "warning" : "critical";
    case "pending_approvals":
      return value === 0 ? "healthy" : "informational";
    default:
      if (metric.severity === "critical") return "critical";
      if (metric.severity === "warning") return "warning";
      if (metric.severity === "good") return "healthy";
      return "informational";
  }
}

function unitKey(unit: string): string | null {
  const normalized = unit.trim().toLowerCase();
  if (!normalized || normalized === "%" || normalized === "boolean" || normalized === "score") return null;
  const supported = new Set(["sections", "rooms", "blockers", "approvals", "items", "scans", "alerts"]);
  return supported.has(normalized) ? `dashboard.admin.units.${normalized}` : null;
}

function formatValue(metric: DashboardMetric, state: AdminDisplayState, t: Translator): { unit: string; value: string } {
  if (state === "notMeasured") return { unit: "", value: t("dashboard.admin.status.notMeasured") };
  if (state === "unavailable") return { unit: "", value: t("dashboard.admin.status.unavailable") };

  const value = numeric(metric.value);
  if (value === null) return { unit: "", value: t("dashboard.admin.status.unavailable") };
  if (metric.metric_code === "db_ok") {
    return { unit: "", value: t(value >= 1 ? "dashboard.admin.status.connected" : "dashboard.admin.status.disconnected") };
  }
  if (metric.unit === "%") return { unit: "", value: `${value.toLocaleString()}%` };
  if (metric.unit === "score") return { unit: t("dashboard.admin.units.points"), value: value.toLocaleString() };

  const key = unitKey(metric.unit);
  return { unit: key ? t(key) : "", value: value.toLocaleString() };
}

function progressFor(metric: DashboardMetric, state: AdminDisplayState): number | null {
  if (state === "notMeasured" || state === "unavailable") return null;
  const value = numeric(metric.value);
  if (value === null) return null;
  if (metric.unit === "%" || metric.unit === "score") return Math.max(0, Math.min(100, value));
  return null;
}

function presentMetric(metric: DashboardMetric, group: DashboardMetricGroup, t: Translator): AdminMetricDisplay {
  const state = classifyMetric(metric);
  const formatted = formatValue(metric, state, t);
  const actionHref = ACTION_ROUTES[metric.metric_code] ?? metric.drilldown_route;
  const actionable = state === "warning" || state === "critical" || state === "unavailable";
  return {
    actionHref: actionable ? actionHref : null,
    actionLabel: actionable ? t("dashboard.admin.action.review") : "",
    description: t(metric.description_i18n_key),
    groupCode: group.group_code,
    groupTitle: t(group.title_i18n_key),
    metricCode: metric.metric_code,
    numericValue: numeric(metric.value),
    progress: progressFor(metric, state),
    restricted: metric.pdpa_level === "restricted" || metric.pdpa_level === "confidential",
    state,
    stateLabel: t(`dashboard.admin.status.${state}`),
    title: t(metric.title_i18n_key),
    unit: formatted.unit,
    value: formatted.value,
    whyItMatters: t(metric.why_it_matters_i18n_key),
  };
}

export function presentAdminDashboard(data: AdminIntelligenceDashboard, t: Translator): AdminDashboardDisplay {
  const metrics = data.groups.flatMap((group) => group.metrics.map((metric) => presentMetric(metric, group, t)));
  const priorities = metrics
    .filter((metric) => metric.state === "critical" || metric.state === "warning" || metric.state === "unavailable")
    .sort((a, b) => STATE_PRIORITY[a.state] - STATE_PRIORITY[b.state] || a.title.localeCompare(b.title))
    .slice(0, 5);
  const score = data.overall_health_score;
  const scoreState: AdminDisplayState =
    score === null ? "notMeasured" : score >= 75 ? "healthy" : score >= 50 ? "warning" : "critical";

  return {
    detailGroups: data.groups.map((group) => ({
      description: t(group.description_i18n_key),
      groupCode: group.group_code,
      metrics: group.metrics.map((metric) => presentMetric(metric, group, t)),
      tab: GROUP_TABS[group.group_code] ?? "system",
      title: t(group.title_i18n_key),
    })),
    metrics,
    priorities,
    score,
    scoreState,
  };
}

export function metricByCode(display: AdminDashboardDisplay, code: string): AdminMetricDisplay | undefined {
  return display.metrics.find((metric) => metric.metricCode === code);
}
