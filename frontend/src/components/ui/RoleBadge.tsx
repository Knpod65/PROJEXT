import { Badge } from "@/components/ui/Badge";
import { getRoleTheme } from "@/theme/roleThemes";
import type { UserRole } from "@/types/api";
import { formatRole } from "@/utils/format";

interface RoleBadgeProps {
  role: UserRole;
  size?: "sm" | "md";
}

export function RoleBadge({ role, size = "md" }: RoleBadgeProps) {
  const theme = getRoleTheme(role);

  return (
    <Badge
      size={size}
      className="role-badge"
      style={{
        background: theme.accentSoft,
        color: theme.accentText,
        border: `1px solid ${theme.accent}`,
      }}
    >
      {formatRole(role)}
    </Badge>
  );
}
