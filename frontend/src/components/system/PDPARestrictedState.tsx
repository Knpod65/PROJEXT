import { translate } from "@/i18n";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";

interface PDPARestrictedStateProps {
  reason?: string;
}

export function PDPARestrictedState({ reason }: PDPARestrictedStateProps) {
  return (
    <div className="system-state">
      <EmptyState
        icon={<Icon name="shield" />}
        title={translate("pdpa.restricted.title")}
        description={reason || translate("pdpa.restricted.description")}
      />
    </div>
  );
}

export default PDPARestrictedState;
