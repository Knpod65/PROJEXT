import type { ReactNode } from "react";

import { getPageDescription, getPageTitle, type AppPageConfig } from "@/config/navigation";
import { useI18n } from "@/i18n";
import { useAuth } from "@/store/auth.store";
import { getRoleTheme, getRoleThemeStyle } from "@/theme/roleThemes";
import { getEffectiveRole } from "@/utils/roles";

import { MobileBottomNav } from "./MobileBottomNav";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

interface AppShellProps {
  title: string;
  page?: AppPageConfig;
  children: ReactNode;
}

export function AppShell({ children, page, title }: AppShellProps) {
  const { t } = useI18n();
  const { user } = useAuth();
  const role = getEffectiveRole(user);
  const theme = getRoleTheme(role);
  const resolvedTitle = page ? getPageTitle(page) : title;
  const resolvedDescription = page ? getPageDescription(page) : undefined;

  return (
    <div
      className="app-shell"
      data-role={role ?? "guest"}
      style={getRoleThemeStyle(theme)}
    >
      <Sidebar />
      <div className="app-shell__main">
        <Topbar description={resolvedDescription} title={resolvedTitle || t("app.shell.controlCenter")} />
        <main className="app-shell__content">{children}</main>
      </div>
      <MobileBottomNav />
    </div>
  );
}
