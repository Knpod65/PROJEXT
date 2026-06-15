import { useCallback } from "react";
import { useNavigate } from "react-router-dom";

import { BarChart } from "@/components/charts/BarChart";
import { DonutChart } from "@/components/charts/DonutChart";
import { DashboardActivityFeed } from "@/components/dashboard/DashboardActivityFeed";
import { DashboardHighlights, type DashboardHighlightItem } from "@/components/dashboard/DashboardHighlights";
import { DashboardMetricCard } from "@/components/dashboard/DashboardMetricCard";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageSkeleton } from "@/components/ui/PageSkeleton";
import { useAsyncData } from "@/hooks/useAsyncData";
import { useI18n } from "@/i18n";
import { getDashboardAnalytics, getDashboardStats } from "@/services/dashboard.service";
import { useAuth } from "@/store/auth.store";
import { useEffectiveRole } from "@/hooks/useEffectiveRole";
import { formatCurrency, formatNumber, formatPercent, formatRole } from "@/utils/format";
import { canManageUsers } from "@/utils/permissions";

function buildOverviewHighlights(
  roleLabel: string,
  stats: Awaited<ReturnType<typeof getDashboardStats>>,
  t: ReturnType<typeof useI18n>["t"],
): DashboardHighlightItem[] {
  const scheduledPercent = stats.total_sections ? (stats.scheduled_sections / stats.total_sections) * 100 : 0;

  return [
    {
      icon: "event_note",
      label: t("dashboard.scheduledSections"),
      value: formatNumber(stats.scheduled_sections),
      note: t("dashboard.scheduledSectionsNote", { percent: formatPercent(scheduledPercent) }),
    },
    {
      icon: "meeting_room",
      label: t("dashboard.roomsInUse"),
      value: formatNumber(stats.rooms_in_use),
      note: t("dashboard.roomUtilizationNote", { role: roleLabel }),
    },
    {
      icon: "print",
      label: t("dashboard.copyWorkload"),
      value: formatNumber(stats.total_sheets),
      note: t("dashboard.copyWorkloadNote", { cost: formatCurrency(stats.copy_cost) }),
    },
  ];
}

export function DashboardPage() {
  const navigate = useNavigate();
  const { t } = useI18n();
  const { user } = useAuth();
  const role = useEffectiveRole();

  const statsLoader = useCallback(() => getDashboardStats(), []);
  const analyticsLoader = useCallback(() => (canManageUsers(user) ? getDashboardAnalytics() : Promise.resolve(null)), [user]);

  const statsState = useAsyncData(statsLoader, [statsLoader]);
  const analyticsState = useAsyncData(analyticsLoader, [analyticsLoader]);

  if (statsState.loading) {
    return <PageSkeleton cards={4} rows={3} />;
  }

  if (statsState.error || !statsState.data) {
    return (
      <EmptyState
        icon={<Icon name="warning" />}
        title={t("dashboard.loadErrorTitle")}
        description={statsState.error ?? undefined}
      />
    );
  }

  const stats = statsState.data;
  const analytics = analyticsState.data;
  const scheduledPercent = stats.total_sections ? (stats.scheduled_sections / stats.total_sections) * 100 : 0;
  const roleLabel = formatRole(role);
  const overviewHighlights = buildOverviewHighlights(roleLabel, stats, t);

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        className="page-hero--dashboard"
        eyebrow={t("dashboard.eyebrow")}
        title={t("dashboard.title")}
        description={t("dashboard.description")}
        actions={
          <>
            <Button iconLeft={<Icon name="event_note" />} type="button" onClick={() => navigate("/schedule")}>
              {t("dashboard.openMasterSchedule")}
            </Button>
            <Button
              iconLeft={<Icon name="assignment_ind" />}
              type="button"
              variant="outline"
              onClick={() => navigate("/attendance")}
            >
              {t("dashboard.roomAttendance")}
            </Button>
          </>
        }
      />

      <section className="stitch-metric-grid">
        <DashboardMetricCard
          hint={`${formatNumber(stats.scheduled_sections)} (${formatPercent(scheduledPercent)})`}
          icon="event_note"
          label={t("dashboard.totalSections")}
          value={formatNumber(stats.total_sections)}
        />
        <DashboardMetricCard
          hint={t("dashboard.facultyRecordsHint", { count: formatNumber(stats.total_teachers) })}
          icon="school"
          label={t("dashboard.studentsCovered")}
          tone="neutral"
          value={formatNumber(stats.total_students)}
        />
        <DashboardMetricCard
          hint={t("dashboard.printEstimateHint", { cost: formatCurrency(stats.copy_cost) })}
          icon="print"
          label={t("dashboard.sheetsRequired")}
          tone="warning"
          value={formatNumber(stats.total_sheets)}
        />
        <DashboardMetricCard
          hint={t("dashboard.unscheduledHint", { count: formatNumber(stats.unscheduled_sections) })}
          icon="meeting_room"
          label={t("dashboard.roomsInUse")}
          tone="success"
          value={formatNumber(stats.rooms_in_use)}
        />
      </section>

      {canManageUsers(user) && analytics ? (
        <>
          <section className="stitch-metric-grid">
            <DashboardMetricCard
              icon="swap_horiz"
              label={t("dashboard.pendingSwaps")}
              value={formatNumber(analytics.swap_status["pending"] ?? 0)}
              hint={t("dashboard.pendingSwapsHint")}
              tone={(analytics.swap_status["pending"] ?? 0) > 0 ? "warning" : "success"}
              onClick={() => navigate("/swaps")}
            />
            <DashboardMetricCard
              icon="description"
              label={t("dashboard.submissionsNeeded")}
              value={formatNumber(analytics.teacher_stats.not_submitted)}
              hint={t("dashboard.submissionsNeededHint", {
                submitted: formatNumber(analytics.teacher_stats.submitted),
                total: formatNumber(analytics.teacher_stats.submitted + analytics.teacher_stats.not_submitted),
              })}
              tone={analytics.teacher_stats.not_submitted > 0 ? "warning" : "success"}
              onClick={() => navigate("/submissions")}
            />
            <DashboardMetricCard
              icon="pending_actions"
              label={t("dashboard.unconfirmedInvigilators")}
              value={formatNumber(analytics.supervision_stats.pending)}
              hint={t("dashboard.unconfirmedInvigilatorsHint", {
                count: formatNumber(analytics.supervision_stats.confirmed),
              })}
              tone={analytics.supervision_stats.pending > 0 ? "warning" : "success"}
              onClick={() => navigate("/checkins")}
            />
            <DashboardMetricCard
              icon="event_busy"
              label={t("dashboard.unscheduledSections")}
              value={formatNumber(stats.unscheduled_sections)}
              hint={stats.unscheduled_sections === 0 ? t("dashboard.unscheduledSectionsReady") : t("dashboard.unscheduledSectionsReview")}
              tone={stats.unscheduled_sections > 0 ? "warning" : "success"}
              onClick={() => navigate("/optimizer")}
            />
          </section>

          <section className="dashboard-shell-grid">
            <Card subtitle={t("dashboard.submissionStatusSubtitle")} title={t("dashboard.submissionStatus")}>
              <DonutChart
                centerLabel={t("dashboard.total")}
                colors={["#6c757d", "#f59e0b", "#059669", "#dc2626", "#0d6efd"]}
                labels={Object.keys(analytics.submission_status)}
                values={Object.values(analytics.submission_status)}
              />
            </Card>

            <Card subtitle={t("dashboard.copyWorkload")} title={t("dashboard.copyWorkload")}>
              <BarChart
                color="#0d6efd"
                labels={analytics.copy_per_room.slice(0, 5).map((item) => item.room)}
                values={analytics.copy_per_room.slice(0, 5).map((item) => item.sheets)}
              />
            </Card>

            <Card subtitle={t("dashboard.swapMixSubtitle")} title={t("dashboard.swapMix")}>
              <DonutChart
                centerLabel={t("dashboard.swaps")}
                colors={["#f59e0b", "#059669", "#dc2626", "#6b7280"]}
                labels={Object.keys(analytics.swap_status)}
                values={Object.values(analytics.swap_status)}
              />
            </Card>

            <div className="dashboard-activity-wrapper">
              <Card subtitle={t("dashboard.recentActivitySubtitleAdmin")} title={t("dashboard.recentActivity")}>
                <DashboardActivityFeed items={stats.recent_logs} maxItems={8} />
              </Card>
              <Button
                iconLeft={<Icon name="manage_search" />}
                type="button"
                variant="outline"
                onClick={() => navigate("/import-audit")}
              >
                {t("dashboard.fullAuditLog")}
              </Button>
            </div>
          </section>
        </>
      ) : (
        <section className="dashboard-shell-grid">
          <Card subtitle={t("dashboard.commandHighlightsSubtitle", { role: roleLabel })} title={t("dashboard.commandHighlights")}>
            <DashboardHighlights items={overviewHighlights} />
          </Card>

          <div className="dashboard-activity-wrapper">
            <Card subtitle={t("dashboard.recentActivitySubtitle")} title={t("dashboard.recentActivity")}>
              <DashboardActivityFeed items={stats.recent_logs} maxItems={8} />
            </Card>
          </div>

          <Card subtitle={t("dashboard.operationalFocus")} title={t("dashboard.roleFocus", { role: roleLabel })}>
            <DashboardHighlights
              items={[
                {
                  icon: "fact_check",
                  label: t("dashboard.scheduledProgress"),
                  value: formatPercent(scheduledPercent),
                  note: t("dashboard.scheduledProgressNote"),
                },
                {
                  icon: "groups",
                  label: t("dashboard.teachingCoverage"),
                  value: formatNumber(stats.total_teachers),
                  note: t("dashboard.teachingCoverageNote"),
                },
                {
                  icon: "assignment_ind",
                  label: t("dashboard.nextAction"),
                  value: stats.unscheduled_sections === 0 ? t("dashboard.nextActionReady") : t("dashboard.nextActionReview"),
                  note:
                    stats.unscheduled_sections === 0
                      ? t("dashboard.nextActionReadyNote")
                      : t("dashboard.nextActionReviewNote", { count: formatNumber(stats.unscheduled_sections) }),
                },
              ]}
            />
          </Card>

          <Card subtitle={t("dashboard.jumpToWorkSubtitle")} title={t("dashboard.jumpToWork")}>
            <div className="dashboard-quick-actions">
              <Button
                iconLeft={<Icon name="description" />}
                type="button"
                variant="outline"
                onClick={() => navigate("/submissions")}
              >
                {t("dashboard.reviewSubmissions")}
              </Button>
              <Button
                iconLeft={<Icon name="how_to_reg" />}
                type="button"
                variant="outline"
                onClick={() => navigate("/checkins")}
              >
                {t("dashboard.openCheckins")}
              </Button>
              <Button
                iconLeft={<Icon name="event_note" />}
                type="button"
                variant="outline"
                onClick={() => navigate("/schedule")}
              >
                {t("dashboard.reviewSchedule")}
              </Button>
            </div>
          </Card>
        </section>
      )}
    </div>
  );
}
