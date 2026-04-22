import { useI18n } from "@/i18n";
import type { DashboardStats } from "@/types/api";
import { cx } from "@/utils/cx";
import { formatDateTime } from "@/utils/format";

interface DashboardActivityFeedProps {
  items: DashboardStats["recent_logs"];
  maxItems?: number;
}

export function DashboardActivityFeed({ items, maxItems }: DashboardActivityFeedProps) {
  const { t } = useI18n();
  const visible = maxItems ? items.slice(0, maxItems) : items;

  if (visible.length === 0) {
    return <p className="dashboard-list__empty">{t("dashboard.noActivity")}</p>;
  }

  return (
    <div className={cx("dashboard-list", visible.length > 5 && "dashboard-list--scroll")}>
      {visible.map((item) => (
        <div key={item.id} className="dashboard-list__item">
          <strong>{item.action}</strong>
          <span>{item.actor || t("common.system")}</span>
          <time>{formatDateTime(item.timestamp)}</time>
        </div>
      ))}
    </div>
  );
}
