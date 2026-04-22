import { useEffect, useState } from "react";

import { useI18n } from "@/i18n";
import { useAuth } from "@/store/auth.store";
import { usePeriod } from "@/store/period.store";
import { getRoleTheme } from "@/theme/roleThemes";
import { formatRole } from "@/utils/format";
import { getEffectiveRole } from "@/utils/roles";
import { LanguageToggle } from "../ui/LanguageToggle";
import { Icon } from "../ui/Icon";

interface TopbarProps {
  title: string;
  description?: string;
}

export function Topbar({ description, title }: TopbarProps) {
  const { locale, t } = useI18n();
  const { activePeriod } = usePeriod();
  const { user } = useAuth();
  const role = getEffectiveRole(user);
  const theme = getRoleTheme(role);
  const [currentTime, setCurrentTime] = useState(() => new Date());

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      setCurrentTime(new Date());
    }, 60_000);

    return () => window.clearInterval(intervalId);
  }, []);

  return (
    <header className="topbar">
      <div className="topbar__heading">
        <span className="topbar__eyebrow">{theme.badgeLabel}</span>
        <h1 className="topbar__title">{title}</h1>
        <p className="topbar__description">{description ?? activePeriod?.label ?? t("app.shell.workspaceDescription")}</p>
      </div>

      <div className="topbar__actions">
        <div className="topbar__status">
          <LanguageToggle />
          <div className="topbar__chip">
            <Icon name="schedule" />
            <span>{currentTime.toLocaleString(locale, { dateStyle: "medium", timeStyle: "short" })}</span>
          </div>
          <div className="topbar__chip topbar__chip--accent">
            <Icon filled name={theme.brandIcon} />
            <span>{formatRole(role)}</span>
          </div>
        </div>

        <div className="topbar__user">
          <strong>{user?.full_name ?? user?.username ?? t("common.guest")}</strong>
          <span>{user?.email ?? activePeriod?.label ?? t("topbar.userFallback")}</span>
        </div>
      </div>
    </header>
  );
}
