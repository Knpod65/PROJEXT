import type { UserRole } from "@/types/api";
import { formatRole } from "@/utils/format";

import { Button } from "../ui/Button";

interface ViewAsBannerProps {
  role: UserRole;
  onReset: () => void;
}

export function ViewAsBanner({ onReset, role }: ViewAsBannerProps) {
  return (
    <div className="view-as-banner">
      <span>Viewing as: {formatRole(role)}</span>
      <Button size="sm" type="button" variant="ghost" onClick={onReset}>
        Return to my role
      </Button>
    </div>
  );
}
