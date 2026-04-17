import type { ReactNode } from "react";

interface SettingsToggleProps {
  label: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  rightSlot?: ReactNode;
}

export function SettingsToggle({ checked, description, label, onChange, rightSlot }: SettingsToggleProps) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "16px",
        padding: "14px 16px",
        borderRadius: "16px",
        background: "var(--surface2)",
      }}
    >
      <div style={{ display: "grid", gap: "4px" }}>
        <strong>{label}</strong>
        <span style={{ color: "var(--text-mid)", fontSize: "0.88rem" }}>{description}</span>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        {rightSlot}
        <input
          aria-label={label}
          checked={checked}
          onChange={(event) => onChange(event.target.checked)}
          style={{ width: "18px", height: "18px", accentColor: "var(--role-accent)" }}
          type="checkbox"
        />
      </div>
    </div>
  );
}