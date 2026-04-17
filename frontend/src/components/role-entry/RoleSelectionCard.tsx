import type { CSSProperties } from "react";

import { getRoleTheme } from "@/theme/roleThemes";

import { Icon } from "../ui/Icon";
import type { RoleEntryDefinition } from "./roleEntryConfig";

interface RoleSelectionCardProps {
  entry: RoleEntryDefinition;
  selected: boolean;
  onSelect: () => void;
}

export function RoleSelectionCard({ entry, onSelect, selected }: RoleSelectionCardProps) {
  const theme = getRoleTheme(entry.accentRole);
  const style = {
    "--entry-accent": theme.accent,
    "--entry-accent-soft": theme.accentSoft,
    "--entry-accent-text": theme.accentText,
  } as CSSProperties;

  return (
    <button
      aria-pressed={selected}
      className={selected ? "role-selection-card role-selection-card--selected" : "role-selection-card"}
      onClick={onSelect}
      style={style}
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
