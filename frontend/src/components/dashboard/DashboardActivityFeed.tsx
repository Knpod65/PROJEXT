import type { DashboardStats } from "@/types/api";
import { formatDateTime } from "@/utils/format";

interface DashboardActivityFeedProps {
  items: DashboardStats["recent_logs"];
}

export function DashboardActivityFeed({ items }: DashboardActivityFeedProps) {
  if (items.length === 0) {
    return <p className="dashboard-list__empty">No recent exam operations activity yet.</p>;
  }

  return (
    <div className="dashboard-list">
      {items.map((item) => (
        <div key={item.id} className="dashboard-list__item">
          <strong>{item.action}</strong>
          <span>{item.actor || "system"}</span>
          <time>{formatDateTime(item.timestamp)}</time>
        </div>
      ))}
    </div>
  );
}
