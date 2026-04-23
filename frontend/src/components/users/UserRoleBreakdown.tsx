import { Card } from "@/components/ui/Card";
import { RoleBadge } from "@/components/ui/RoleBadge";
import { useI18n } from "@/i18n";
import { getRoleTheme } from "@/theme/roleThemes";
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
          const theme = getRoleTheme(row.role);
          const width = total > 0 ? `${(row.count / total) * 100}%` : "0%";

          return (
            <article key={row.role} className="role-distribution-item">
              <div className="role-distribution-item__header">
                <RoleBadge role={row.role} size="sm" />
                <strong>{row.count}</strong>
              </div>
              <div className="role-distribution-item__track" aria-hidden="true">
                <span
                  className="role-distribution-item__fill"
                  style={{
                    width,
                    background: `linear-gradient(90deg, ${theme.accent}, ${theme.accentStrong})`,
                    boxShadow: `0 10px 18px ${theme.canvasGlow}`,
                  }}
                />
              </div>
            </article>
          );
        })}
      </div>
    </Card>
  );
}
