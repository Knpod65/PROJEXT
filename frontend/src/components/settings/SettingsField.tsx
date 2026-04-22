import type React from "react";

import { cx } from "@/utils/cx";

interface SettingsFieldProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  label: string;
  helper?: string;
  children: React.ReactNode;
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
