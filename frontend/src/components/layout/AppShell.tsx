import type { ReactNode } from "react";

import { useAuth } from "@/store/auth.store";

import { MobileBottomNav } from "./MobileBottomNav";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { ViewAsBanner } from "./ViewAsBanner";

interface AppShellProps {
  title: string;
  children: ReactNode;
}

export function AppShell({ children, title }: AppShellProps) {
  const { switchViewAs, user } = useAuth();

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-shell__main">
        <Topbar title={title} />
        {user?.view_as_role ? <ViewAsBanner role={user.view_as_role} onReset={() => void switchViewAs(null)} /> : null}
        <main className="app-shell__content">{children}</main>
      </div>
      <MobileBottomNav />
    </div>
  );
}
