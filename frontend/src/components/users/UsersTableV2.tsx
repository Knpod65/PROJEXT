import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { DataTable } from "@/components/ui/DataTable";
import { RoleBadge } from "@/components/ui/RoleBadge";
import { useI18n } from "@/i18n";
import type { UserOut } from "@/types/api";
import { formatDateTime, formatTranslatedValue } from "@/utils/format";

interface UsersTableV2Props {
  rows: UserOut[];
  busyUserId?: number | null;
  onEdit: (user: UserOut) => void;
  onToggleStatus: (user: UserOut) => void;
  onDelete: (user: UserOut) => void;
}

export function UsersTableV2({
  busyUserId = null,
  onDelete,
  onEdit,
  onToggleStatus,
  rows,
}: UsersTableV2Props) {
  const { t } = useI18n();

  return (
    <DataTable<UserOut>
      columns={[
        {
          key: "identity",
          label: t("users.table.identity"),
          width: "290px",
          minWidth: "250px",
          render: (row) => (
            <div>
              <strong>{row.full_name ?? t("users.table.unnamed")}</strong>
              <p>{row.username}</p>
              <p>{row.email}</p>
            </div>
          ),
        },
        {
          key: "role",
          label: t("users.table.role"),
          width: "170px",
          minWidth: "160px",
          render: (row) => <RoleBadge role={row.role} />,
        },
        {
          key: "department",
          label: t("users.table.department"),
          width: "170px",
          minWidth: "150px",
          render: (row) => <span>{row.department ?? row.dept_code ?? "-"}</span>,
        },
        {
          key: "status",
          label: t("users.table.status"),
          width: "130px",
          minWidth: "120px",
          align: "center",
          render: (row) => (
            <Badge variant={row.is_active ? "green" : "gray"}>
              {formatTranslatedValue("status", row.is_active ? "active" : "inactive")}
            </Badge>
          ),
        },
        {
          key: "created_at",
          label: t("users.table.updated"),
          width: "160px",
          minWidth: "150px",
          render: (row) => <span>{formatDateTime(row.created_at)}</span>,
        },
        {
          key: "actions",
          label: t("users.table.actions"),
          minWidth: "320px",
          render: (row) => {
            const isBusy = busyUserId === row.id;

            return (
              <div className="user-row-actions">
                <Button size="sm" type="button" variant="outline" onClick={() => onEdit(row)} disabled={isBusy}>
                  {t("common.edit")}
                </Button>
                <Button size="sm" type="button" variant="outline" onClick={() => onToggleStatus(row)} disabled={isBusy}>
                  {row.is_active ? t("users.table.deactivate") : t("users.table.activate")}
                </Button>
                <Button size="sm" type="button" variant="danger" onClick={() => onDelete(row)} disabled={isBusy}>
                  {t("users.table.delete")}
                </Button>
              </div>
            );
          },
        },
      ]}
      rows={rows}
      rowKey={(row) => row.id}
      rowClassName={(row) => (!row.is_active ? "row-inactive" : undefined)}
      compact
      tableLayout="fixed"
      scrollThreshold={5}
      maxHeight={520}
      emptyTitle={t("users.table.noUsersTitle")}
      emptyDescription={t("users.table.noUsersDescription")}
    />
  );
}
