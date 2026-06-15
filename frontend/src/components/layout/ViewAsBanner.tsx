import type { UserRole } from "@/types/api";
import { useI18n } from "@/i18n";
import { formatRole } from "@/utils/format";

import { Button } from "../ui/Button";

interface ViewAsBannerProps {
  role: UserRole;
  onReset: () => void;
}

export function ViewAsBanner({ onReset, role }: ViewAsBannerProps) {
  const { t } = useI18n();
  return (
    <div className="view-as-banner">
      <span>{t("layout.viewAs.current", { role: formatRole(role) })}</span>
      <Button size="sm" type="button" variant="ghost" onClick={onReset}>
        {t("layout.viewAs.return")}
      </Button>
    </div>
  );
}
