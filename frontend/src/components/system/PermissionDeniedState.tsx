import { translate } from "@/i18n";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";

interface PermissionDeniedStateProps {
  message?: string;
}

export function PermissionDeniedState({ message }: PermissionDeniedStateProps) {
  return (
    <div className="flex items-center justify-center p-8">
      <EmptyState
        icon={<Icon name="shield" />}
        title={message || translate("app.unauthorized.title")}
        description={translate("app.unauthorized.description")}
      />
    </div>
  );
}

export default PermissionDeniedState;