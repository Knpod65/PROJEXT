import { useMemo } from "react";

import type { UserRole } from "@/types/api";
import { useAuth } from "@/store/auth.store";
import { usePeriod } from "@/store/period.store";
import { formatRole } from "@/utils/format";
import { canViewAs } from "@/utils/roles";

import { Button } from "../ui/Button";

interface TopbarProps {
  title: string;
}

const viewAsRoles: UserRole[] = ["staff", "teacher", "student"];

export function Topbar({ title }: TopbarProps) {
  const { activePeriod } = usePeriod();
  const { switchViewAs, user } = useAuth();

  const currentRole = useMemo(() => formatRole(user?.view_as_role ?? user?.effective_role ?? user?.role), [user]);

  return (
    <header className="topbar">
      <div>
        <h1 className="topbar__title">{title}</h1>
        <p className="topbar__period">{activePeriod?.label ?? "ยังไม่มีรอบสอบที่ active"}</p>
      </div>

      <div className="topbar__actions">
        {canViewAs(user) ? (
          <div className="topbar__viewas">
            {viewAsRoles.map((role) => (
              <Button key={role} size="sm" type="button" variant="ghost" onClick={() => void switchViewAs(role)}>
                {formatRole(role)}
              </Button>
            ))}
          </div>
        ) : null}

        <div className="topbar__user">
          <strong>{user?.full_name ?? user?.username ?? "Guest"}</strong>
          <span>{currentRole}</span>
        </div>
      </div>
    </header>
  );
}
