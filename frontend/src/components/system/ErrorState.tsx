import { translate } from "@/i18n";
import { EmptyState } from "@/components/ui/EmptyState";
import { Button } from "@/components/ui/Button";
import { Icon } from "@/components/ui/Icon";

interface ErrorStateProps {
  title?: string;
  description?: string;
  retry?: () => void;
}

export function ErrorState({ title, description, retry }: ErrorStateProps) {
  return (
    <div className="system-state">
      <EmptyState
        icon={<Icon name="error" />}
        title={title || translate("errors.generic")}
        description={description || translate("errors.tryAgain")}
        action={retry ? <Button onClick={retry}>{translate("common.retry")}</Button> : undefined}
      />
    </div>
  );
}

export default ErrorState;
