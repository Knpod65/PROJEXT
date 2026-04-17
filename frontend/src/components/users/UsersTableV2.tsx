import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { DataTable } from "@/components/ui/DataTable";
import type { UserOut } from "@/types/api";
import { formatRole } from "@/utils/format";

interface UsersTableV2Props {
  rows: UserOut[];
  onDeactivate: (id: number) => void;
}

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

export function UsersTableV2({ onDeactivate, rows }: UsersTableV2Props) {
  return (
    <DataTable<UserOut>
      columns={[
        {
          key: "identity",
          label: "Name and Identity",
          render: (row) => (
            <div>
              <strong>{row.full_name ?? "Unnamed user"}</strong>
              <p>{row.username}</p>
              <p>{row.email}</p>
            </div>
          ),
        },
        {
          key: "role",
          label: "Role",
          render: (row) => <Badge variant={roleVariant(row.role)}>{formatRole(row.role)}</Badge>,
        },
        {
          key: "department",
          label: "Department",
          render: (row) => <span>{row.department ?? row.dept_code ?? "-"}</span>,
        },
        {
          key: "status",
          label: "Status",
          render: (row) => <Badge variant={row.is_active ? "green" : "gray"}>{row.is_active ? "active" : "inactive"}</Badge>,
        },
        {
          key: "actions",
          label: "Actions",
          render: (row) =>
            row.is_active ? (
              <Button size="sm" type="button" variant="outline" onClick={() => onDeactivate(row.id)}>
                Deactivate
              </Button>
            ) : (
              <span>-</span>
            ),
        },
      ]}
      rows={rows}
      rowKey={(row) => row.id}
      emptyTitle="No users matched"
      emptyDescription="Try adjusting role/status filters or search text."
    />
  );
}
