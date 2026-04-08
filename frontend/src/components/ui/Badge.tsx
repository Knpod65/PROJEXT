import type { HTMLAttributes } from "react";

import { cx } from "@/utils/cx";

type BadgeVariant =
  | "navy"
  | "crimson"
  | "gold"
  | "green"
  | "gray"
  | "blue"
  | "orange";

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  size?: "sm" | "md";
}

export function Badge({
  children,
  className,
  size = "md",
  variant = "gray",
  ...props
}: BadgeProps) {
  return (
    <span className={cx("ui-badge", `ui-badge--${variant}`, `ui-badge--${size}`, className)} {...props}>
      {children}
    </span>
  );
}
