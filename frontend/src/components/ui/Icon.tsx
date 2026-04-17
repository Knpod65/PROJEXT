import type { HTMLAttributes } from "react";

import { cx } from "@/utils/cx";

interface IconProps extends HTMLAttributes<HTMLSpanElement> {
  name: string;
  filled?: boolean;
}

export function Icon({ className, filled = false, name, ...props }: IconProps) {
  return (
    <span
      aria-hidden="true"
      className={cx("app-icon", filled && "app-icon--filled", className)}
      {...props}
    >
      {name}
    </span>
  );
}
