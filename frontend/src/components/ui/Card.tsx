import type { HTMLAttributes, ReactNode } from "react";

import { cx } from "@/utils/cx";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: ReactNode;
  subtitle?: ReactNode;
  actions?: ReactNode;
}

export function Card({ actions, children, className, subtitle, title, ...props }: CardProps) {
  return (
    <section className={cx("ui-card", className)} {...props}>
      {title || subtitle || actions ? (
        <header className="ui-card__header">
          <div>
            {title ? <h3 className="ui-card__title">{title}</h3> : null}
            {subtitle ? <p className="ui-card__subtitle">{subtitle}</p> : null}
          </div>
          {actions ? <div className="ui-card__actions">{actions}</div> : null}
        </header>
      ) : null}
      <div className="ui-card__body">{children}</div>
    </section>
  );
}
