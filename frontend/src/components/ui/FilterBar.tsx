import type { ReactNode } from "react";

import { cx } from "@/utils/cx";

interface FilterBarProps {
  children: ReactNode;
  actions?: ReactNode;
  className?: string;
  layout?: "wrap" | "grid";
}

export function FilterBar({ actions, children, className, layout = "wrap" }: FilterBarProps) {
  return (
    <div className={cx("filter-bar", layout === "grid" && "filter-bar--grid", className)}>
      <div className="filter-bar__fields">{children}</div>
      {actions ? <div className="filter-bar__actions">{actions}</div> : null}
    </div>
  );
}
