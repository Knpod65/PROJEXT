import type { ReactNode } from "react";

import { cx } from "@/utils/cx";

interface FilterBarProps {
  children: ReactNode;
  actions?: ReactNode;
  className?: string;
}

export function FilterBar({ actions, children, className }: FilterBarProps) {
  return (
    <div className={cx("filter-bar", className)}>
      <div className="filter-bar__fields">{children}</div>
      {actions ? <div className="filter-bar__actions">{actions}</div> : null}
    </div>
  );
}
