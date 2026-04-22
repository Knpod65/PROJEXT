import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { useI18n } from "@/i18n";
import type { UserStats } from "@/hooks/useUsersData";

interface UserStatsCardsProps {
  stats: UserStats;
}

export function UserStatsCards({ stats }: UserStatsCardsProps) {
  const { t } = useI18n();

  return (
    <div className="summary-grid">
      <Card title={t("users.stats.total")} actions={<Badge variant="blue">{stats.total}</Badge>}>
        <p>{t("users.stats.totalDescription")}</p>
      </Card>
      <Card title={t("users.stats.active")} actions={<Badge variant="green">{stats.active}</Badge>}>
        <p>{t("users.stats.activeDescription")}</p>
      </Card>
      <Card title={t("users.stats.inactive")} actions={<Badge variant="gray">{stats.inactive}</Badge>}>
        <p>{t("users.stats.inactiveDescription")}</p>
      </Card>
      <Card title={t("users.stats.faculty")} actions={<Badge variant="gold">{stats.teachers}</Badge>}>
        <p>{t("users.stats.facultyDescription")}</p>
      </Card>
      <Card title={t("users.stats.admins")} actions={<Badge variant="navy">{stats.admins}</Badge>}>
        <p>{t("users.stats.adminsDescription")}</p>
      </Card>
      <Card title={t("users.stats.queue")} actions={<Badge variant="orange">{stats.pendingApprovals}</Badge>}>
        <p>{t("users.stats.queueDescription")}</p>
      </Card>
    </div>
  );
}
