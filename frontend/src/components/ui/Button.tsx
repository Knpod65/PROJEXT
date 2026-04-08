import type { ButtonHTMLAttributes, ReactNode } from "react";

import { cx } from "@/utils/cx";

type ButtonVariant = "primary" | "navy" | "gold" | "outline" | "danger" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  fullWidth?: boolean;
  iconLeft?: ReactNode;
  iconRight?: ReactNode;
}

export function Button({
  children,
  className,
  disabled,
  fullWidth,
  iconLeft,
  iconRight,
  loading,
  size = "md",
  variant = "primary",
  ...props
}: ButtonProps) {
  return (
    <button
      className={cx(
        "ui-button",
        `ui-button--${variant}`,
        `ui-button--${size}`,
        fullWidth && "ui-button--full",
        className,
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? <span className="ui-button__spinner" aria-hidden="true" /> : iconLeft}
      <span>{children}</span>
      {!loading ? iconRight : null}
    </button>
  );
}
