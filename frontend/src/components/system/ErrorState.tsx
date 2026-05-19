import { translate } from "@/i18n";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";

interface ErrorStateProps {
  title?: string;
  description?: string;
  retry?: () => void;
}

export function ErrorState({ title, description, retry }: ErrorStateProps) {
  return (
    <div className="flex items-center justify-center p-8">
      <EmptyState
        icon={<Icon name="error" />}
        title={title || translate("errors.generic")}
        description={description || translate("errors.tryAgain")}
        action={retry ? <button onClick={retry} className="btn-primary">{translate("common.retry")}</button> : undefined}
      />
    </div>
  );
}

export default ErrorState;