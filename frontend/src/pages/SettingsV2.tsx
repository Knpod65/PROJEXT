import { SettingsField } from "@/components/settings/SettingsField";
import { SettingsSection } from "@/components/settings/SettingsSection";
import { SettingsToggle } from "@/components/settings/SettingsToggle";
import { SettingsViewAsSwitcher } from "@/components/settings/SettingsViewAsSwitcher";
import { Button } from "@/components/ui/Button";
import { useSettingsData } from "@/hooks/useSettingsData";
import { useUi } from "@/store/ui.store";

export function SettingsV2Page() {
  const { toast } = useUi();
  const {
    accessSettings,
    activeRole,
    activeTheme,
    generalSettings,
    localizationSettings,
    resetViewAs,
    switchViewAs,
    updateAccessSetting,
    updateGeneralSetting,
    updateLocalizationSetting,
    viewAsOptions,
  } = useSettingsData();

  const handleSaveDraft = (label: string) => {
    toast(`${label} saved in preview mode.`, "success");
  };

  const handleSwitchViewAs = async (role: Parameters<typeof switchViewAs>[0]) => {
    try {
      await switchViewAs(role);
      toast(`Now viewing as ${role}.`, "info");
    } catch (error) {
      toast(error instanceof Error ? error.message : "Unable to switch view-as mode", "error");
    }
  };

  const handleResetViewAs = async () => {
    try {
      await resetViewAs();
      toast("Returned to the default admin preview.", "info");
    } catch (error) {
      toast(error instanceof Error ? error.message : "Unable to reset view-as mode", "error");
    }
  };

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">Settings and View-As V2</span>
          <h1 className="page-hero__title">System settings preview</h1>
          <p className="page-hero__description">
            Mock configuration panels for admin review, paired with the existing auth-backed view-as flow so theme changes stay in sync with the shell.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={handleResetViewAs}>
            Reset View-As
          </Button>
          <Button type="button" onClick={() => handleSaveDraft("Settings draft")}>
            Save Draft
          </Button>
        </div>
      </section>

      <SettingsSection
        title="View-As Mode"
        description="Use the existing switchViewAs flow to preview how the shell and theme behave for each role."
      >
        <SettingsViewAsSwitcher
          activeRole={activeRole}
          activeTheme={activeTheme}
          options={viewAsOptions}
          onReset={() => void handleResetViewAs()}
          onSelectRole={(role) => void handleSwitchViewAs(role)}
        />
      </SettingsSection>

      <div className="dashboard-shell-grid">
        <SettingsSection
          title="System Profile"
          description="High-level institution metadata used by the admin workspace preview."
          actions={
            <Button type="button" variant="ghost" onClick={() => handleSaveDraft("System profile")}>
              Save
            </Button>
          }
        >
          <div className="settings-row" style={{ alignItems: "flex-start" }}>
            <SettingsField label="System Name">
              <input value={generalSettings.systemName} onChange={(event) => updateGeneralSetting("systemName", event.target.value)} />
            </SettingsField>
            <SettingsField label="Primary Contact Email">
              <input
                value={generalSettings.primaryContactEmail}
                onChange={(event) => updateGeneralSetting("primaryContactEmail", event.target.value)}
              />
            </SettingsField>
            <SettingsField label="Support Phone">
              <input value={generalSettings.supportPhone} onChange={(event) => updateGeneralSetting("supportPhone", event.target.value)} />
            </SettingsField>
          </div>
        </SettingsSection>

        <SettingsSection
          title="Localization"
          description="Language, timezone, and date-format preferences for the admin preview."
          actions={
            <Button type="button" variant="ghost" onClick={() => handleSaveDraft("Localization")}>
              Save
            </Button>
          }
        >
          <div className="settings-row" style={{ alignItems: "flex-start" }}>
            <SettingsField label="Default Language">
              <select value={localizationSettings.language} onChange={(event) => updateLocalizationSetting("language", event.target.value)}>
                <option>Thai (Standard)</option>
                <option>English (United States)</option>
              </select>
            </SettingsField>
            <SettingsField label="Timezone">
              <select value={localizationSettings.timezone} onChange={(event) => updateLocalizationSetting("timezone", event.target.value)}>
                <option>(GMT+07:00) Bangkok, Hanoi, Jakarta</option>
                <option>(GMT+00:00) UTC</option>
              </select>
            </SettingsField>
            <SettingsField label="Date Format">
              <select value={localizationSettings.dateFormat} onChange={(event) => updateLocalizationSetting("dateFormat", event.target.value)}>
                <option>DD MMM YYYY</option>
                <option>YYYY-MM-DD</option>
              </select>
            </SettingsField>
          </div>
        </SettingsSection>

        <SettingsSection
          title="Security & Access"
          description="Preview-only access controls that mirror the institutional guardrail model."
          actions={
            <Button type="button" variant="ghost" onClick={() => handleSaveDraft("Security settings")}>
              Save
            </Button>
          }
        >
          <div style={{ display: "grid", gap: "12px" }}>
            <SettingsToggle
              checked={accessSettings.mfaEnabled}
              description="Require a second verification step for high-risk actions."
              label="Multi-factor authentication"
              onChange={(checked) => updateAccessSetting("mfaEnabled", checked)}
            />
            <SettingsToggle
              checked={accessSettings.allowPreviewNotifications}
              description="Show toast notices when preview mode actions are used."
              label="Preview notifications"
              onChange={(checked) => updateAccessSetting("allowPreviewNotifications", checked)}
            />
            <SettingsField label="Session timeout (minutes)">
              <input
                inputMode="numeric"
                min={15}
                step={5}
                type="number"
                value={accessSettings.sessionTimeoutMinutes}
                onChange={(event) => updateAccessSetting("sessionTimeoutMinutes", Number(event.target.value))}
              />
            </SettingsField>
          </div>
        </SettingsSection>

        <SettingsSection
          title="Theme Mapping"
          description="Quick reference for the roleTheme mapping that drives the shell visuals."
          actions={
            <Button type="button" variant="ghost" onClick={() => handleSaveDraft("Theme mapping")}>
              Save
            </Button>
          }
        >
          <div style={{ display: "grid", gap: "12px" }}>
            <p style={{ margin: 0, color: "var(--text-mid)" }}>
              The active theme is read from the same role-aware theme helper used by AppShell and Topbar, so view-as mode updates the chrome and accents together.
            </p>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
                gap: "12px",
              }}
            >
              <div style={{ padding: "14px", borderRadius: "16px", background: "var(--surface2)" }}>
                <span style={{ display: "block", color: "var(--text-mid)", fontSize: "0.78rem" }}>Active role</span>
                <strong>{activeRole ?? "admin"}</strong>
              </div>
              <div style={{ padding: "14px", borderRadius: "16px", background: "var(--surface2)" }}>
                <span style={{ display: "block", color: "var(--text-mid)", fontSize: "0.78rem" }}>Accent</span>
                <strong>{activeTheme.accent}</strong>
              </div>
              <div style={{ padding: "14px", borderRadius: "16px", background: "var(--surface2)" }}>
                <span style={{ display: "block", color: "var(--text-mid)", fontSize: "0.78rem" }}>Shell title</span>
                <strong>{activeTheme.shellTitle}</strong>
              </div>
            </div>
          </div>
        </SettingsSection>
      </div>
    </div>
  );
}