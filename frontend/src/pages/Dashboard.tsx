import { useCallback } from "react";

import { BarChart } from "@/components/charts/BarChart";
import { DonutChart } from "@/components/charts/DonutChart";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Skeleton } from "@/components/ui/Skeleton";
import { StatCard } from "@/components/ui/StatCard";
import { getDashboardAnalytics, getDashboardStats } from "@/services/dashboard.service";
import { useAuth } from "@/store/auth.store";
import { useAsyncData } from "@/hooks/useAsyncData";
import { formatCurrency, formatNumber, formatPercent } from "@/utils/format";
import { getEffectiveRole } from "@/utils/roles";

export function DashboardPage() {
  const { user } = useAuth();
  const role = getEffectiveRole(user);

  const statsLoader = useCallback(() => getDashboardStats(), []);
  const analyticsLoader = useCallback(() => (role === "admin" ? getDashboardAnalytics() : Promise.resolve(null)), [role]);

  const statsState = useAsyncData(statsLoader, [statsLoader]);
  const analyticsState = useAsyncData(analyticsLoader, [analyticsLoader]);

  if (statsState.loading) {
    return (
      <div className="page-stack">
        <div className="stats-grid">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="dashboard-skeleton" />
          ))}
        </div>
        <Skeleton className="dashboard-chart-skeleton" />
      </div>
    );
  }

  if (statsState.error || !statsState.data) {
    return <EmptyState icon="⚠️" title="โหลดแดชบอร์ดไม่สำเร็จ" description={statsState.error ?? undefined} />;
  }

  const stats = statsState.data;
  const analytics = analyticsState.data;
  const scheduledPercent = stats.total_sections
    ? (stats.scheduled_sections / stats.total_sections) * 100
    : 0;

  return (
    <div className="page-stack">
      <section className="stats-grid">
        <StatCard
          icon="📚"
          iconBackground="var(--crimson-lt)"
          label="Sections ทั้งหมด"
          value={formatNumber(stats.total_sections)}
          subLabel={`${formatNumber(stats.scheduled_sections)} จัดแล้ว (${formatPercent(scheduledPercent)})`}
          progress={scheduledPercent}
        />
        <StatCard
          icon="👨‍🎓"
          iconBackground="rgba(13,110,253,0.12)"
          label="นักศึกษาทั้งหมด"
          value={formatNumber(stats.total_students)}
          subLabel={`${formatNumber(stats.total_teachers)} อาจารย์`}
        />
        <StatCard
          icon="🖨️"
          iconBackground="var(--gold-lt)"
          label="แผ่นถ่ายเอกสารรวม"
          value={formatNumber(stats.total_sheets)}
          subLabel={formatCurrency(stats.copy_cost)}
        />
        <StatCard
          icon="🏫"
          iconBackground="var(--success-lt)"
          label="ห้องสอบที่ใช้"
          value={formatNumber(stats.rooms_in_use)}
          subLabel={`${formatNumber(stats.unscheduled_sections)} sections ยังไม่ได้จัด`}
        />
      </section>

      {role === "admin" && analytics ? (
        <section className="dashboard-charts">
          <Card title="📤 สถานะการส่งข้อสอบ">
            <DonutChart
              centerLabel="รวม"
              colors={["#6c757d", "#b8860b", "#198754", "#c41230", "#fd7e14"]}
              labels={Object.keys(analytics.submission_status)}
              values={Object.values(analytics.submission_status)}
            />
          </Card>
          <Card title="✅ การยืนยันกำกับสอบ">
            <DonutChart
              centerLabel="รวม"
              colors={["#198754", "#6c757d"]}
              labels={["confirmed", "pending"]}
              values={[
                analytics.supervision_stats.confirmed,
                analytics.supervision_stats.pending,
              ]}
            />
          </Card>
          <Card title="🔄 คำขอสลับกะ">
            <DonutChart
              centerLabel="รวม"
              colors={["#b8860b", "#198754", "#c41230", "#6c757d"]}
              labels={Object.keys(analytics.swap_status)}
              values={Object.values(analytics.swap_status)}
            />
          </Card>
          <Card title="🖨️ แผ่นต่อห้องสอบ">
            <BarChart
              color="#8b0000"
              labels={analytics.copy_per_room.map((item) => item.room)}
              values={analytics.copy_per_room.map((item) => item.sheets)}
            />
          </Card>
        </section>
      ) : null}

      <Card title="📋 ประวัติการใช้งานล่าสุด">
        {stats.recent_logs.length === 0 ? (
          <EmptyState icon="🧾" title="ยังไม่มีประวัติ" />
        ) : (
          <div className="activity-list">
            {stats.recent_logs.map((item) => (
              <div key={item.id} className="activity-list__item">
                <strong>{item.action}</strong>
                <span>{item.actor || "system"}</span>
                <time>{item.timestamp ? new Date(item.timestamp).toLocaleString("th-TH") : "-"}</time>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
