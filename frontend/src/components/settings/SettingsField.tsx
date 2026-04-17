import type { LabelHTMLAttributes, ReactNode } from "react";

import { cx } from "@/utils/cx";

interface SettingsFieldProps extends LabelHTMLAttributes<HTMLLabelElement> {
  label: string;
  helper?: string;
  children: ReactNode;
}

export function SettingsField({ children, className, helper, label, ...props }: SettingsFieldProps) {
  return (
    <label className={cx("form-field", className)} {...props}>
      <span>{label}</span>
      {children}
      {helper ? <small style={{ color: "var(--text-mid)" }}>{helper}</small> : null}
    </label>
  );
}