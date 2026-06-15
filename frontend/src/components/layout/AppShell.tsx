import type { ReactNode } from "react";

import { getPageDescription, getPageTitle, type AppPageConfig } from "@/config/navigation";
import { useEffectiveRole } from "@/hooks/useEffectiveRole";
import { useI18n } from "@/i18n";

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
  const role = useEffectiveRole();
  const resolvedTitle = page ? getPageTitle(page) : title;
  const resolvedDescription = page ? getPageDescription(page) : undefined;

  return (
    <div
      className="app-shell"
      data-density="comfortable"
      data-role={role ?? "guest"}
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
