import type { ReactNode } from "react";

import { cx } from "@/utils/cx";

type AlertBannerVariant = "info" | "warning" | "success" | "danger";

interface AlertBannerProps {
  action?: ReactNode;
  children?: ReactNode;
  className?: string;
  title: ReactNode;
  variant?: AlertBannerVariant;
}

export function AlertBanner({
  action,
  children,
  className,
  title,
  variant = "info",
}: AlertBannerProps) {
  return (
    <section className={cx("alert-banner", `alert-banner--${variant}`, className)}>
      <div>
        <strong>{title}</strong>
        {children ? <p>{children}</p> : null}
      </div>
      {action ? <div className="alert-banner__action">{action}</div> : null}
    </section>
  );
}
