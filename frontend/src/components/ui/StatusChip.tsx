import type { HTMLAttributes, ReactNode } from "react";

import { cx } from "@/utils/cx";

export type StatusTone =
  | "success"
  | "information"
  | "warning"
  | "danger"
  | "neutral"
  | "blocked"
  | "draft"
  | "readOnly";

interface StatusChipProps extends HTMLAttributes<HTMLSpanElement> {
  children: ReactNode;
  tone?: StatusTone;
}

export function StatusChip({ children, className, tone = "neutral", ...props }: StatusChipProps) {
  return (
    <span className={cx("status-chip", `status-chip--${tone}`, className)} {...props}>
      {children}
    </span>
  );
}
