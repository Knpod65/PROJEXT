import type { ReactNode } from "react";

import { cx } from "@/utils/cx";

interface FormFieldProps {
  children: ReactNode;
  className?: string;
  error?: ReactNode;
  helper?: ReactNode;
  label: ReactNode;
}

export function FormField({ children, className, error, helper, label }: FormFieldProps) {
  return (
    <label className={cx("form-field", className)}>
      <span>{label}</span>
      {children}
      {helper ? <small className="form-hint">{helper}</small> : null}
      {error ? <p className="form-error">{error}</p> : null}
    </label>
  );
}
