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
import { Skeleton } from "@/components/ui/Skeleton";
import { useAsyncData } from "@/hooks/useAsyncData";
import { getDashboardAnalytics, getDashboardStats } from "@/services/dashboard.service";
import { useAuth } from "@/store/auth.store";
import { formatCurrency, formatNumber, formatPercent, formatRole } from "@/utils/format";
import { getEffectiveRole } from "@/utils/roles";

function buildOverviewHighlights(
  roleLabel: string,
  stats: Awaited<ReturnType<typeof getDashboardStats>>,
): DashboardHighlightItem[] {
  const scheduledPercent = stats.total_sections ? (stats.scheduled_sections / stats.total_sections) * 100 : 0;

  return [
    {
      icon: "event_note",
      label: "Scheduled sections",
      value: formatNumber(stats.scheduled_sections),
      note: `${formatPercent(scheduledPercent)} of all sections are already placed.`,
    },
    {
      icon: "meeting_room",
      label: "Rooms in use",
      value: formatNumber(stats.rooms_in_use),
      note: `${roleLabel} workspace is tracking live room utilization.`,
    },
    {
      icon: "print",
      label: "Copy workload",
      value: formatNumber(stats.total_sheets),
      note: `${formatCurrency(stats.copy_cost)} total estimated print cost.`,
    },
  ];
}

export function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const role = getEffectiveRole(user);

  const statsLoader = useCallback(() => getDashboardStats(), []);
  const analyticsLoader = useCallback(() => (role === "admin" ? getDashboardAnalytics() : Promise.resolve(null)), [role]);

  const statsState = useAsyncData(statsLoader, [statsLoader]);
  const analyticsState = useAsyncData(analyticsLoader, [analyticsLoader]);

  if (statsState.loading) {
    return (
      <div className="page-stack">
        <div className="stitch-metric-grid">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="dashboard-skeleton" />
          ))}
        </div>
        <Skeleton className="dashboard-chart-skeleton" />
      </div>
    );
  }

  if (statsState.error || !statsState.data) {
    return (
      <EmptyState
        icon={<Icon name="warning" />}
        title="Dashboard data could not be loaded."
        description={statsState.error ?? undefined}
      />
    );
  }

  const stats = statsState.data;
  const analytics = analyticsState.data;
  const scheduledPercent = stats.total_sections ? (stats.scheduled_sections / stats.total_sections) * 100 : 0;
  const roleLabel = formatRole(role);
  const overviewHighlights = buildOverviewHighlights(roleLabel, stats);

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero page-hero--dashboard">
        <div>
          <span className="page-hero__eyebrow">Refined oversight console</span>
          <h2 className="page-hero__title">Exam operations at a glance</h2>
          <p className="page-hero__description">
            The chosen Stitch dashboard is now mapped onto live EMS data so each role gets a cleaner command view without losing the existing academic relationships.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button iconLeft={<Icon name="event_note" />} type="button" onClick={() => navigate("/schedule")}>
            Open master schedule
          </Button>
          <Button
            iconLeft={<Icon name="assignment_ind" />}
            type="button"
            variant="outline"
            onClick={() => navigate("/attendance")}
          >
            Room attendance
          </Button>
        </div>
      </section>

      <section className="stitch-metric-grid">
        <DashboardMetricCard
          hint={`${formatNumber(stats.scheduled_sections)} scheduled (${formatPercent(scheduledPercent)})`}
          icon="event_note"
          label="Total sections"
          value={formatNumber(stats.total_sections)}
        />
        <DashboardMetricCard
          hint={`${formatNumber(stats.total_teachers)} faculty records`}
          icon="school"
          label="Students covered"
          tone="neutral"
          value={formatNumber(stats.total_students)}
        />
        <DashboardMetricCard
          hint={`${formatCurrency(stats.copy_cost)} print estimate`}
          icon="print"
          label="Sheets required"
          tone="warning"
          value={formatNumber(stats.total_sheets)}
        />
        <DashboardMetricCard
          hint={`${formatNumber(stats.unscheduled_sections)} sections still open`}
          icon="meeting_room"
          label="Rooms in use"
          tone="success"
          value={formatNumber(stats.rooms_in_use)}
        />
      </section>

      <section className="dashboard-shell-grid">
        <Card subtitle={`${roleLabel} operations summary`} title="Command highlights">
          <DashboardHighlights items={overviewHighlights} />
        </Card>

        <Card subtitle="Most recent changes across the current period" title="Recent activity">
          <DashboardActivityFeed items={stats.recent_logs} />
        </Card>

        {role === "admin" && analytics ? (
          <>
            <Card subtitle="Submission queue across the institution" title="Submission status">
              <DonutChart
                centerLabel="Total"
                colors={["#6c757d", "#f59e0b", "#059669", "#dc2626", "#0d6efd"]}
                labels={Object.keys(analytics.submission_status)}
                values={Object.values(analytics.submission_status)}
              />
            </Card>

            <Card subtitle="Confirmed vs pending invigilation" title="Coverage confirmations">
              <DashboardHighlights
                items={[
                  {
                    icon: "verified",
                    label: "Confirmed",
                    value: formatNumber(analytics.supervision_stats.confirmed),
                    note: "Supervision slots that have already confirmed coverage.",
                  },
                  {
                    icon: "pending_actions",
                    label: "Pending",
                    value: formatNumber(analytics.supervision_stats.pending),
                    note: "Assignments still waiting for an explicit confirmation.",
                  },
                  {
                    icon: "swap_horiz",
                    label: "Swap requests",
                    value: formatNumber(
                      Object.values(analytics.swap_status).reduce((total, item) => total + item, 0),
                    ),
                    note: "Requests that may affect room readiness and duty balance.",
                  },
                ]}
              />
            </Card>

            <Card subtitle="Highest print load by room" title="Copy workload">
              <BarChart
                color="#0d6efd"
                labels={analytics.copy_per_room.slice(0, 5).map((item) => item.room)}
                values={analytics.copy_per_room.slice(0, 5).map((item) => item.sheets)}
              />
            </Card>

            <Card subtitle="Open vs resolved swap requests" title="Swap mix">
              <DonutChart
                centerLabel="Swaps"
                colors={["#f59e0b", "#059669", "#dc2626", "#6b7280"]}
                labels={Object.keys(analytics.swap_status)}
                values={Object.values(analytics.swap_status)}
              />
            </Card>
          </>
        ) : (
          <>
            <Card subtitle="Operational focus built from the chosen Stitch layout" title={`${roleLabel} focus`}>
              <DashboardHighlights
                items={[
                  {
                    icon: "fact_check",
                    label: "Scheduled progress",
                    value: formatPercent(scheduledPercent),
                    note: "Use this to judge how ready your current role view is for the period.",
                  },
                  {
                    icon: "groups",
                    label: "Teaching coverage",
                    value: formatNumber(stats.total_teachers),
                    note: "Faculty records currently linked into the exam period.",
                  },
                  {
                    icon: "assignment_ind",
                    label: "Next action",
                    value: stats.unscheduled_sections === 0 ? "Ready" : "Review",
                    note:
                      stats.unscheduled_sections === 0
                        ? "Scheduling looks complete from the current data snapshot."
                        : `${formatNumber(stats.unscheduled_sections)} sections still need follow-up.`,
                  },
                ]}
              />
            </Card>

            <Card subtitle="Quick route into the first reusable EMS page families" title="Jump to work">
              <div className="dashboard-quick-actions">
                <Button
                  iconLeft={<Icon name="description" />}
                  type="button"
                  variant="outline"
                  onClick={() => navigate("/submissions")}
                >
                  Review submissions
                </Button>
                <Button
                  iconLeft={<Icon name="how_to_reg" />}
                  type="button"
                  variant="outline"
                  onClick={() => navigate("/checkins")}
                >
                  Open check-ins
                </Button>
                <Button
                  iconLeft={<Icon name="event_note" />}
                  type="button"
                  variant="outline"
                  onClick={() => navigate("/schedule")}
                >
                  Review schedule
                </Button>
              </div>
            </Card>
          </>
        )}
      </section>
    </div>
  );
}
