import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { useI18n } from "@/i18n";
import type { UserRole } from "@/types/api";
import { formatRole } from "@/utils/format";

interface UserRoleBreakdownProps {
  rows: Array<{ role: UserRole; count: number }>;
}

export function UserRoleBreakdown({ rows }: UserRoleBreakdownProps) {
  const { t } = useI18n();

  return (
    <Card title={t("users.distributionTitle")} subtitle={t("users.distributionSubtitle")}>
      <div className="page-stack">
        {rows.map((row) => (
          <div key={row.role} className="signer-list__item">
            <strong>{formatRole(row.role)}</strong>
            <Badge variant="navy">{row.count}</Badge>
          </div>
        ))}
      </div>
    </Card>
  );
}
