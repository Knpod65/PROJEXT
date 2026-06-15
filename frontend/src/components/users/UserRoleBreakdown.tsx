import { Card } from "@/components/ui/Card";
import { RoleBadge } from "@/components/ui/RoleBadge";
import { useI18n } from "@/i18n";
import type { UserRole } from "@/types/api";

interface UserRoleBreakdownProps {
  rows: Array<{ role: UserRole; count: number }>;
}

export function UserRoleBreakdown({ rows }: UserRoleBreakdownProps) {
  const { t } = useI18n();
  const total = rows.reduce((sum, row) => sum + row.count, 0);

  return (
    <Card title={t("users.distributionTitle")} subtitle={t("users.distributionSubtitle")}>
      <div className="role-distribution-list">
        {rows.map((row) => {
          const width = total > 0 ? `${(row.count / total) * 100}%` : "0%";

          return (
            <article key={row.role} className="role-distribution-item" data-role={row.role}>
              <div className="role-distribution-item__header">
                <RoleBadge role={row.role} size="sm" />
                <strong>{row.count}</strong>
              </div>
              <div className="role-distribution-item__track" aria-hidden="true">
                <span
                  className="role-distribution-item__fill"
                  style={{ width }}
                />
              </div>
            </article>
          );
        })}
      </div>
    </Card>
  );
}
