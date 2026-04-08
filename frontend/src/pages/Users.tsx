import { useCallback } from "react";

import { Badge } from "@/components/ui/Badge";
import { DataTable } from "@/components/ui/DataTable";
import { deactivateUser, listUsers } from "@/services/users.service";
import { useAsyncData } from "@/hooks/useAsyncData";
import type { UserOut } from "@/types/api";
import { useUi } from "@/store/ui.store";

export function UsersPage() {
  const { toast } = useUi();
  const loader = useCallback(() => listUsers(), []);
  const state = useAsyncData(loader, [loader]);

  const handleDeactivate = async (userId: number) => {
    try {
      await deactivateUser(userId);
      toast("ปิดการใช้งานผู้ใช้แล้ว", "success");
      await state.reload();
    } catch (err) {
      toast(err instanceof Error ? err.message : "ปิดการใช้งานไม่สำเร็จ", "error");
    }
  };

  return (
    <DataTable<UserOut>
      columns={[
        { key: "full_name", label: "ชื่อ-สกุล" },
        { key: "username", label: "Username" },
        { key: "email", label: "Email" },
        {
          key: "role",
          label: "Role",
          render: (row) => <Badge variant="navy">{row.role}</Badge>,
        },
        {
          key: "is_active",
          label: "สถานะ",
          render: (row) => <Badge variant={row.is_active ? "green" : "gray"}>{row.is_active ? "active" : "inactive"}</Badge>,
        },
        {
          key: "actions",
          label: "",
          render: (row) =>
            row.is_active ? (
              <button className="table-action" onClick={() => void handleDeactivate(row.id)} type="button">
                ปิดใช้งาน
              </button>
            ) : null,
        },
      ]}
      emptyDescription="ยังไม่มีผู้ใช้ในระบบ"
      loading={state.loading}
      rowKey={(row) => row.id}
      rows={state.data ?? []}
    />
  );
}
