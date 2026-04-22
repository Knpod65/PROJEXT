import { useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { DataTable } from "@/components/ui/DataTable";
import { useI18n } from "@/i18n";
import type { UserOut, UserRole } from "@/types/api";
import { formatRole, formatTranslatedValue } from "@/utils/format";

interface UsersTableV2Props {
  rows: UserOut[];
  savingRoleId?: number | null;
  onDeactivate: (id: number) => void;
  onUpdateRole: (id: number, role: UserRole) => Promise<void>;
}

const roleOptions: UserRole[] = [
  "admin",
  "teacher",
  "staff",
  "dept_supervisor",
  "esq_head",
  "secretary",
  "print_shop",
  "student",
];

function roleVariant(role: UserOut["role"]) {
  if (role === "admin") {
    return "crimson" as const;
  }

  if (role === "teacher") {
    return "green" as const;
  }

  if (role === "staff" || role === "dept_supervisor") {
    return "blue" as const;
  }

  if (role === "print_shop") {
    return "navy" as const;
  }

  return "gray" as const;
}

export function UsersTableV2({
  onDeactivate,
  onUpdateRole,
  rows,
  savingRoleId = null,
}: UsersTableV2Props) {
  const { t } = useI18n();
  const [editingUserId, setEditingUserId] = useState<number | null>(null);
  const [draftRole, setDraftRole] = useState<UserRole>("staff");

  const beginRoleEdit = (row: UserOut) => {
    setEditingUserId(row.id);
    setDraftRole(row.role);
  };

  const resetRoleEdit = () => {
    if (savingRoleId !== null) {
      return;
    }

    setEditingUserId(null);
  };

  return (
    <DataTable<UserOut>
      columns={[
        {
          key: "identity",
          label: t("users.table.identity"),
          width: "280px",
          minWidth: "240px",
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
          width: "150px",
          minWidth: "140px",
          render: (row) => <Badge variant={roleVariant(row.role)}>{formatRole(row.role)}</Badge>,
        },
        {
          key: "department",
          label: t("users.table.department"),
          width: "160px",
          minWidth: "150px",
          render: (row) => <span>{row.department ?? row.dept_code ?? "-"}</span>,
        },
        {
          key: "status",
          label: t("users.table.status"),
          width: "120px",
          minWidth: "120px",
          align: "center",
          render: (row) => (
            <Badge variant={row.is_active ? "green" : "gray"}>
              {formatTranslatedValue("status", row.is_active ? "active" : "inactive")}
            </Badge>
          ),
        },
        {
          key: "actions",
          label: t("users.table.actions"),
          minWidth: "280px",
          render: (row) => {
            const isEditing = editingUserId === row.id;
            const isSaving = savingRoleId === row.id;

            if (isEditing) {
              return (
                <div className="user-row-actions">
                  <span className="user-role-editor">
                    <select
                      value={draftRole}
                      onChange={(event) => setDraftRole(event.currentTarget.value as UserRole)}
                      disabled={isSaving}
                      aria-label={t("users.table.editRole")}
                    >
                      {roleOptions.map((role) => (
                        <option key={role} value={role}>
                          {formatRole(role)}
                        </option>
                      ))}
                    </select>
                  </span>

                  <Button
                    size="sm"
                    type="button"
                    loading={isSaving}
                    onClick={async () => {
                      try {
                        await onUpdateRole(row.id, draftRole);
                        setEditingUserId(null);
                      } catch {
                        // Parent handler already surfaces the error.
                      }
                    }}
                  >
                    {t("common.save")}
                  </Button>

                  <Button size="sm" type="button" variant="outline" onClick={resetRoleEdit} disabled={isSaving}>
                    {t("common.cancel")}
                  </Button>
                </div>
              );
            }

            return (
              <div className="user-row-actions">
                <Button size="sm" type="button" variant="outline" onClick={() => beginRoleEdit(row)}>
                  {t("users.table.editRole")}
                </Button>
                {row.is_active ? (
                  <Button size="sm" type="button" variant="outline" onClick={() => onDeactivate(row.id)}>
                    {t("users.table.deactivate")}
                  </Button>
                ) : (
                  <span className="user-row-actions__muted">
                    {formatTranslatedValue("status", "inactive")}
                  </span>
                )}
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
      maxHeight={520}
      scrollThreshold={5}
      emptyTitle={t("users.table.noUsersTitle")}
      emptyDescription={t("users.table.noUsersDescription")}
    />
  );
}
