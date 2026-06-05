import type { ReactNode } from "react";

import { cx } from "@/utils/cx";

interface PageHeaderProps {
  actions?: ReactNode;
  className?: string;
  description?: ReactNode;
  eyebrow: ReactNode;
  status?: ReactNode;
  title: ReactNode;
}

export function PageHeader({ actions, className, description, eyebrow, status, title }: PageHeaderProps) {
  return (
    <section className={cx("page-hero", className)}>
      <div>
        <span className="page-hero__eyebrow">{eyebrow}</span>
        <h2 className="page-hero__title">{title}</h2>
        {description ? <p className="page-hero__description">{description}</p> : null}
      </div>
      {actions || status ? (
        <div className="page-hero__actions">
          {status}
          {actions}
        </div>
      ) : null}
    </section>
  );
}
