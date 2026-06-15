import type { ReactNode } from "react";

import { Icon } from "./Icon";

interface InlineErrorProps {
  action?: ReactNode;
  message: ReactNode;
}

export function InlineError({ action, message }: InlineErrorProps) {
  return (
    <div className="inline-error" role="alert">
      <Icon name="error" />
      <span>{message}</span>
      {action ? <div className="inline-error__action">{action}</div> : null}
    </div>
  );
}
