import { Icon } from "../ui/Icon";
import type { RoleEntryDefinition } from "./roleEntryConfig";

interface RoleSelectionCardProps {
  entry: RoleEntryDefinition;
  selected: boolean;
  onSelect: () => void;
}

export function RoleSelectionCard({ entry, onSelect, selected }: RoleSelectionCardProps) {
  return (
    <button
      aria-pressed={selected}
      className={selected ? "role-selection-card role-selection-card--selected" : "role-selection-card"}
      data-role={entry.accentRole}
      onClick={onSelect}
      type="button"
    >
      <div className="role-selection-card__icon">
        <Icon filled name={entry.icon} />
      </div>

      <div className="role-selection-card__copy">
        <span className="role-selection-card__eyebrow">{entry.eyebrow}</span>
        <strong className="role-selection-card__title">{entry.title}</strong>
        <p className="role-selection-card__description">{entry.description}</p>
      </div>
    </button>
  );
}
