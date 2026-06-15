import type { ReactNode } from "react";

import { Icon } from "./Icon";

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  headingLevel?: 1 | 2 | 3;
}

export function EmptyState({ action, description, headingLevel = 3, icon, title }: EmptyStateProps) {
  const Heading = `h${headingLevel}` as const;
  return (
    <div className="empty-state">
      <div className="empty-state__icon">{icon ?? <Icon name="info" />}</div>
      <Heading className="empty-state__title">{title}</Heading>
      {description ? <p className="empty-state__description">{description}</p> : null}
      {action ? <div className="empty-state__action">{action}</div> : null}
    </div>
  );
}
