import type { ReactNode } from "react";

import { Card } from "@/components/ui/Card";

interface SettingsSectionProps {
  title: string;
  description: string;
  actions?: ReactNode;
  children: ReactNode;
}

export function SettingsSection({ actions, children, description, title }: SettingsSectionProps) {
  return (
    <Card title={title} subtitle={description} actions={actions}>
      {children}
    </Card>
  );
}