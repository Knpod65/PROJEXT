import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { BarChart } from "@/components/charts/BarChart";
import { DonutChart } from "@/components/charts/DonutChart";
import { PermissionDeniedState } from "@/components/system/PermissionDeniedState";
import { AlertBanner } from "@/components/ui/AlertBanner";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton } from "@/components/ui/Skeleton";
import { Tabs } from "@/components/ui/Tabs";
import { useAdminIntelligenceDashboard } from "@/hooks/domain/useAdminIntelligenceDashboard";
import { usePermission } from "@/hooks/usePermission";
import { useI18n } from "@/i18n";
import { usePeriod } from "@/store/period.store";
import {
  metricByCode,
  presentAdminDashboard,
  type AdminDetailTab,
  type AdminDisplayState,
  type AdminMetricDisplay,
} from "@/utils/presenters/adminDashboardPresenter";

const DETAIL_TABS: AdminDetailTab[] = ["scheduling", "governance", "people", "delivery", "system"];

const STATE_BADGE: Record<AdminDisplayState, "green" | "blue" | "gold" | "crimson" | "gray" | "orange"> = {
  healthy: "green",
  informational: "blue",
  warning: "gold",
  critical: "crimson",
  notMeasured: "gray",
  unavailable: "orange",
};

const STATE_ICON: Record<AdminDisplayState, string> = {
  healthy: "check_circle",
  informational: "info",
  warning: "warning",
  critical: "error",
  notMeasured: "pending",
  unavailable: "cloud_off",
};

function MetricValue({ metric }: { metric: AdminMetricDisplay }) {
  return (
    <div className="admin-command-metric__value">
      <strong>{metric.value}</strong>
      {metric.unit ? <span>{metric.unit}</span> : null}
    </div>
  );
}

function SummaryCard({
  action,
  actionLabel,
  icon,
  label,
  metric,
  progress,
  state,
  stateLabel,
  value,
}: {
  action?: () => void;
  actionLabel?: string;
  icon: string;
  label: string;
  metric?: AdminMetricDisplay;
  progress?: number | null;
  state: AdminDisplayState;
  stateLabel?: string;
  value: string;
}) {
  return (
    <article className={`admin-command-summary admin-command-summary--${state}`}>
      <div className="admin-command-summary__top">
        <div className="admin-command-summary__icon"><Icon name={icon} /></div>
        <Badge size="sm" variant={STATE_BADGE[state]}>{stateLabel ?? metric?.stateLabel}</Badge>
      </div>
      <span className="admin-command-summary__label">{label}</span>
      <strong className="admin-command-summary__value">{value}</strong>
      {progress !== null && progress !== undefined ? (
        <div className="admin-command-summary__progress" aria-hidden="true">
          <span style={{ width: `${Math.max(0, Math.min(100, progress))}%` }} />
        </div>
      ) : null}
      {action ? (
        <Button size="sm" type="button" variant="ghost" onClick={action} iconRight={<Icon name="arrow_forward" />}>
          {actionLabel ?? metric?.actionLabel}
        </Button>
      ) : null}
    </article>
  );
}

export default function AdminIntelligenceDashboard() {
  const navigate = useNavigate();
  const { locale, t } = useI18n();
  const { activePeriod } = usePeriod();
  const { canManageUsers } = usePermission();
  const { data, isLoading, isError } = useAdminIntelligenceDashboard();
  const [activeTab, setActiveTab] = useState<AdminDetailTab>("scheduling");

  const display = useMemo(() => (data ? presentAdminDashboard(data, t) : null), [data, t]);

  if (!canManageUsers) return <PermissionDeniedState />;
  if (isLoading) {
    return (
      <div className="page-stack page-stack--spacious">
        <Skeleton className="page-loading__hero" />
        <div className="admin-command-summary-grid">{Array.from({ length: 5 }).map((_, index) => <Skeleton key={index} className="dashboard-skeleton" />)}</div>
        <Skeleton className="dashboard-chart-skeleton" />
      </div>
    );
  }
  if (isError || !data || !display) {
    return <EmptyState icon={<Icon name="warning" />} title={t("dashboard.admin.loadErrorTitle")} />;
  }

  const scheduled = metricByCode(display, "scheduled_sections");
  const unscheduled = metricByCode(display, "unscheduled_sections");
  const blockers = metricByCode(display, "blocker_count");
  const api = metricByCode(display, "api_uptime_pct");
  const database = metricByCode(display, "db_ok");
  const storage = metricByCode(display, "storage_usage_pct");
  const totalSections = (scheduled?.numericValue ?? 0) + (unscheduled?.numericValue ?? 0);
  const scheduledPercent = totalSections > 0 ? ((scheduled?.numericValue ?? 0) / totalSections) * 100 : null;
  const scheduledState: AdminDisplayState = scheduledPercent === null ? "notMeasured" : scheduledPercent >= 95 ? "healthy" : scheduledPercent >= 80 ? "warning" : "critical";
  const systemStates = [api, database, storage].filter(Boolean) as AdminMetricDisplay[];
  const systemState = systemStates.some((metric) => metric.state === "critical")
    ? "critical"
    : systemStates.some((metric) => metric.state === "warning")
      ? "warning"
      : systemStates.some((metric) => metric.state === "unavailable")
        ? "unavailable"
        : "healthy";
  const visibleGroups = display.detailGroups.filter((group) => group.tab === activeTab);
  const percentageMetrics = display.metrics.filter(
    (metric) => metric.progress !== null && ["optimization_quality_avg", "room_utilization_score", "submission_rate", "api_uptime_pct", "storage_usage_pct"].includes(metric.metricCode),
  );

  return (
    <div className="page-stack page-stack--spacious admin-command">
      <PageHeader
        className="page-hero--dashboard"
        eyebrow={t("dashboard.admin.eyebrow")}
        title={t("dashboard.admin.title")}
        description={t("dashboard.admin.description")}
        status={
          <div className="admin-command__header-status">
            <Badge variant={STATE_BADGE[display.scoreState]}>{t(`dashboard.admin.status.${display.scoreState}`)}</Badge>
            <span>{activePeriod?.label ?? t("common.noActiveExamPeriod")}</span>
            <span>{t("dashboard.admin.lastUpdated")}: {data.last_computed_at ? new Date(data.last_computed_at).toLocaleString(locale) : t("dashboard.admin.status.unavailable")}</span>
          </div>
        }
      />

      <section className="admin-command-summary-grid" aria-label={t("dashboard.admin.primarySummary")}>
        <SummaryCard icon="speed" label={t("dashboard.admin.summary.readiness")} state={display.scoreState} stateLabel={t(`dashboard.admin.status.${display.scoreState}`)} value={display.score === null ? t("dashboard.admin.status.notMeasured") : `${display.score.toFixed(1)} / 100`} progress={display.score} />
        <SummaryCard icon="event_available" label={t("dashboard.admin.summary.scheduled")} state={scheduledState} stateLabel={t(`dashboard.admin.status.${scheduledState}`)} value={totalSections > 0 ? t("dashboard.admin.summary.scheduledValue", { scheduled: scheduled?.numericValue ?? 0, total: totalSections }) : t("dashboard.admin.status.notMeasured")} progress={scheduledPercent} />
        <SummaryCard icon="event_busy" label={t("dashboard.admin.summary.unscheduled")} state={unscheduled?.state ?? "unavailable"} value={unscheduled ? `${unscheduled.value}${unscheduled.unit ? ` ${unscheduled.unit}` : ""}` : t("dashboard.admin.status.unavailable")} metric={unscheduled} action={unscheduled?.actionHref ? () => navigate(unscheduled.actionHref!) : undefined} />
        <SummaryCard icon="gavel" label={t("dashboard.admin.summary.blockers")} state={blockers?.state ?? "unavailable"} value={blockers ? `${blockers.value}${blockers.unit ? ` ${blockers.unit}` : ""}` : t("dashboard.admin.status.unavailable")} metric={blockers} action={blockers?.actionHref ? () => navigate(blockers.actionHref!) : undefined} />
        <SummaryCard icon="dns" label={t("dashboard.admin.summary.availability")} state={systemState} stateLabel={t(`dashboard.admin.status.${systemState}`)} value={t(`dashboard.admin.status.${systemState}`)} actionLabel={t("dashboard.admin.action.review")} action={systemState === "healthy" ? undefined : () => navigate("/operational-health")} />
      </section>

      {display.priorities.length > 0 ? (
        <AlertBanner variant={display.priorities.some((metric) => metric.state === "critical") ? "danger" : "warning"} title={t("dashboard.admin.priority.title")}>
          {t("dashboard.admin.priority.description", { count: display.priorities.length })}
        </AlertBanner>
      ) : (
        <AlertBanner variant="success" title={t("dashboard.admin.priority.clearTitle")}>{t("dashboard.admin.priority.clearDescription")}</AlertBanner>
      )}

      <section className="admin-command-analysis">
        <Card title={t("dashboard.admin.analysis.scheduleTitle")} subtitle={t("dashboard.admin.analysis.scheduleDescription")}>
          <DonutChart
            centerLabel={t("dashboard.admin.units.sections")}
            colors={["#059669", "#dc2626"]}
            labels={[t("dashboard.admin.summary.scheduled"), t("dashboard.admin.summary.unscheduled")]}
            values={[scheduled?.numericValue ?? 0, unscheduled?.numericValue ?? 0]}
          />
        </Card>
        <Card title={t("dashboard.admin.analysis.indicatorsTitle")} subtitle={t("dashboard.admin.analysis.indicatorsDescription")}>
          <BarChart color="var(--role-accent)" labels={percentageMetrics.map((metric) => metric.title)} values={percentageMetrics.map((metric) => metric.progress ?? 0)} />
        </Card>
      </section>

      <Card title={t("dashboard.admin.priority.title")} subtitle={t("dashboard.admin.priority.listDescription")}>
        {display.priorities.length > 0 ? (
          <div className="admin-command-priorities">
            {display.priorities.map((metric) => (
              <article className="admin-command-priority" key={metric.metricCode}>
                <div className={`admin-command-priority__icon admin-command-priority__icon--${metric.state}`}><Icon name={STATE_ICON[metric.state]} /></div>
                <div className="admin-command-priority__copy">
                  <div><Badge size="sm" variant={STATE_BADGE[metric.state]}>{metric.stateLabel}</Badge>{metric.restricted ? <Badge size="sm" variant="navy">{t("dashboard.admin.restricted")}</Badge> : null}</div>
                  <strong>{metric.title}</strong>
                  <p>{metric.whyItMatters}</p>
                </div>
                {metric.actionHref ? <Button size="sm" variant="outline" type="button" onClick={() => navigate(metric.actionHref!)}>{metric.actionLabel}</Button> : null}
              </article>
            ))}
          </div>
        ) : <EmptyState icon={<Icon name="check_circle" />} title={t("dashboard.admin.priority.clearTitle")} description={t("dashboard.admin.priority.clearDescription")} />}
      </Card>

      <Card title={t("dashboard.admin.details.title")} subtitle={t("dashboard.admin.details.description")}>
        <Tabs activeKey={activeTab} onChange={(key) => setActiveTab(key as AdminDetailTab)} items={DETAIL_TABS.map((key) => ({ key, label: t(`dashboard.admin.tabs.${key}`), badge: display.detailGroups.filter((group) => group.tab === key).reduce((sum, group) => sum + group.metrics.length, 0) }))} />
        <div className="admin-command-detail-groups">
          {visibleGroups.map((group) => (
            <section className="admin-command-detail-group" key={group.groupCode}>
              <header><h3>{group.title}</h3><p>{group.description}</p></header>
              <div className="admin-command-detail-list">
                {group.metrics.map((metric) => (
                  <article className="admin-command-metric" key={metric.metricCode}>
                    <div className="admin-command-metric__heading">
                      <div><strong>{metric.title}</strong>{metric.restricted ? <Badge size="sm" variant="navy">{t("dashboard.admin.restricted")}</Badge> : null}</div>
                      <Badge size="sm" variant={STATE_BADGE[metric.state]}>{metric.stateLabel}</Badge>
                    </div>
                    <MetricValue metric={metric} />
                    {metric.progress !== null ? <div className="admin-command-metric__progress"><span style={{ width: `${metric.progress}%` }} /></div> : null}
                    <p>{metric.description}</p>
                    {metric.actionHref ? <Button size="sm" variant="ghost" type="button" onClick={() => navigate(metric.actionHref!)} iconRight={<Icon name="arrow_forward" />}>{metric.actionLabel}</Button> : null}
                  </article>
                ))}
              </div>
            </section>
          ))}
        </div>
      </Card>
    </div>
  );
}
