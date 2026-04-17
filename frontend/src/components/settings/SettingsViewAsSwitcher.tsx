import type { UserRole } from "@/types/api";
import { formatRole } from "@/utils/format";
import type { RoleTheme } from "@/theme/roleThemes";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

import type { ViewAsOption } from "@/hooks/useSettingsData";

interface SettingsViewAsSwitcherProps {
  activeRole: UserRole | null;
  activeTheme: RoleTheme;
  options: ViewAsOption[];
  onSelectRole: (role: UserRole) => void;
  onReset: () => void;
}

export function SettingsViewAsSwitcher({ activeRole, activeTheme, onReset, onSelectRole, options }: SettingsViewAsSwitcherProps) {
  return (
    <div style={{ display: "grid", gap: "16px" }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "16px",
          padding: "18px 20px",
          borderRadius: "20px",
          background: "var(--surface2)",
          border: "1px solid rgba(231, 226, 218, 0.72)",
        }}
      >
        <div style={{ display: "grid", gap: "6px" }}>
          <Badge variant="blue" size="sm">View-As Preview</Badge>
          <strong>{activeRole ? `Current preview: ${formatRole(activeRole)}` : "Viewing in default admin mode"}</strong>
          <span style={{ color: "var(--text-mid)", fontSize: "0.9rem" }}>
            Switching here uses the admin preview flow, so the theme and shell update together without changing the locked production role flow.
          </span>
        </div>
        <Button type="button" variant="ghost" onClick={onReset}>
          Reset Preview
        </Button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "14px" }}>
        {options.map((option) => (
          <article
            key={option.role}
            style={{
              borderRadius: "18px",
              border: `1px solid ${option.active ? option.theme.accent : "rgba(231, 226, 218, 0.9)"}`,
              background: option.active ? "var(--surface1)" : "var(--surface2)",
              padding: "16px",
              boxShadow: option.active ? `0 0 0 1px ${option.theme.accentSoft}` : "none",
            }}
          >
            <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "12px" }}>
              <div style={{ display: "grid", gap: "6px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                  <Badge variant={option.active ? "blue" : "gray"} size="sm">
                    {option.active ? "Active" : "Preview"}
                  </Badge>
                  <strong>{option.label}</strong>
                </div>
                <span style={{ color: "var(--text-mid)", fontSize: "0.88rem" }}>{option.description}</span>
              </div>
              <span
                aria-hidden="true"
                style={{
                  width: 14,
                  height: 14,
                  borderRadius: 999,
                  background: option.theme.accent,
                  boxShadow: `0 0 0 4px ${option.theme.accentSoft}`,
                  marginTop: 4,
                  flexShrink: 0,
                }}
              />
            </div>

            <div style={{ display: "grid", gap: "10px", marginTop: "14px" }}>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                <Badge variant="gray" size="sm">{option.theme.shellTitle}</Badge>
                <Badge variant="gray" size="sm">{option.theme.badgeLabel}</Badge>
              </div>
              <Button
                type="button"
                variant={option.active ? "ghost" : "outline"}
                onClick={() => onSelectRole(option.role)}
                fullWidth
              >
                {option.active ? "Currently selected" : `View as ${option.label}`}
              </Button>
            </div>
          </article>
        ))}
      </div>

      <div
        style={{
          display: "grid",
          gap: "12px",
          padding: "16px 18px",
          borderRadius: "18px",
          background: "linear-gradient(135deg, var(--role-accent-soft), rgba(255,255,255,0.7))",
          border: "1px solid rgba(231, 226, 218, 0.78)",
        }}
      >
        <strong style={{ color: activeTheme.accentText }}>Role theme preview</strong>
        <div style={{ display: "grid", gap: "6px", color: "var(--text-mid)" }}>
          <span>Accent: {activeTheme.accent}</span>
          <span>Sidebar: {activeTheme.sidebarBg}</span>
          <span>Canvas glow: {activeTheme.canvasGlow}</span>
        </div>
      </div>
    </div>
  );
}
