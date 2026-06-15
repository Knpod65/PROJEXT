import type { ReactNode } from "react";

import type { AppPageConfig } from "@/config/navigation";
import { useEffectiveRole } from "@/hooks/useEffectiveRole";

import { MobileBottomNav } from "./MobileBottomNav";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

interface AppShellProps {
  title: string;
  page?: AppPageConfig;
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const role = useEffectiveRole();

  return (
    <div
      className="app-shell"
      data-density="comfortable"
      data-role={role ?? "guest"}
    >
      <Sidebar />
      <div className="app-shell__main">
        <Topbar />
        <main className="app-shell__content">{children}</main>
      </div>
      <MobileBottomNav />
    </div>
  );
}
