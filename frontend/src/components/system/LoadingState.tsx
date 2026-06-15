import { translate } from "@/i18n";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message }: LoadingStateProps) {
  return (
    <div className="system-state">
      <EmptyState
        icon={<Icon name="progress_activity" className="animate-spin" />}
        title={message || translate("common.loading")}
      />
    </div>
  );
}

export default LoadingState;
