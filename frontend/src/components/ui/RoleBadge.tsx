import { Badge } from "@/components/ui/Badge";
import type { UserRole } from "@/types/api";
import { formatRole } from "@/utils/format";

interface RoleBadgeProps {
  role: UserRole;
  size?: "sm" | "md";
}

export function RoleBadge({ role, size = "md" }: RoleBadgeProps) {
  return (
    <Badge
      data-role={role}
      size={size}
      className="role-badge"
    >
      {formatRole(role)}
    </Badge>
  );
}
