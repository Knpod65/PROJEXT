import { SettingsField } from "@/components/settings/SettingsField";
import { SettingsRetentionPolicyPanel } from "@/components/settings/SettingsRetentionPolicyPanel";
import { SettingsSection } from "@/components/settings/SettingsSection";
import { SettingsTermPreviewPanel } from "@/components/settings/SettingsTermPreviewPanel";
import { SettingsToggle } from "@/components/settings/SettingsToggle";
import { SettingsViewAsSwitcher } from "@/components/settings/SettingsViewAsSwitcher";
import { Button } from "@/components/ui/Button";
import { useSettingsData } from "@/hooks/useSettingsData";
import { useI18n } from "@/i18n";
import { useUi } from "@/store/ui.store";
import { formatRole } from "@/utils/format";

export function SettingsV2Page() {
  const { t } = useI18n();
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
    toast(t("settings.toastSaved", { label }), "success");
  };

  const handleSwitchViewAs = async (role: Parameters<typeof switchViewAs>[0]) => {
    try {
      await switchViewAs(role);
      toast(t("settings.viewAsSwitched", { role: formatRole(role) }), "info");
    } catch (error) {
      toast(error instanceof Error ? error.message : t("errors.switchViewAs"), "error");
    }
  };

  const handleResetViewAs = async () => {
    try {
      await resetViewAs();
      toast(t("settings.viewAsReset"), "info");
    } catch (error) {
      toast(error instanceof Error ? error.message : t("errors.resetViewAs"), "error");
    }
  };

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">{t("settings.heroEyebrow")}</span>
          <h1 className="page-hero__title">{t("settings.heroTitle")}</h1>
          <p className="page-hero__description">{t("settings.heroDescription")}</p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={handleResetViewAs}>
            {t("settings.resetViewAs")}
          </Button>
          <Button type="button" onClick={() => handleSaveDraft(t("settings.saveDraft"))}>
            {t("settings.saveDraft")}
          </Button>
        </div>
      </section>

      <SettingsSection
        title={t("settings.sections.viewAs.title")}
        description={t("settings.sections.viewAs.description")}
      >
        <SettingsViewAsSwitcher
          activeRole={activeRole}
          activeTheme={activeTheme}
          options={viewAsOptions}
          onReset={() => void handleResetViewAs()}
          onSelectRole={(role) => void handleSwitchViewAs(role)}
        />
      </SettingsSection>

      <SettingsSection
        title={t("settings.sections.termPreview.title")}
        description={t("settings.sections.termPreview.description")}
      >
        <SettingsTermPreviewPanel />
      </SettingsSection>

      <SettingsSection
        title={t("settings.sections.retention.title")}
        description={t("settings.sections.retention.description")}
      >
        <SettingsRetentionPolicyPanel />
      </SettingsSection>

      <div className="dashboard-shell-grid">
        <SettingsSection
          title={t("settings.sections.systemProfile.title")}
          description={t("settings.sections.systemProfile.description")}
          actions={
            <Button type="button" variant="ghost" onClick={() => handleSaveDraft(t("settings.sections.systemProfile.title"))}>
              {t("common.save")}
            </Button>
          }
        >
          <div className="settings-row" style={{ alignItems: "flex-start" }}>
            <SettingsField label={t("settings.systemName")}>
              <input value={generalSettings.systemName} onChange={(event) => updateGeneralSetting("systemName", event.target.value)} />
            </SettingsField>
            <SettingsField label={t("settings.primaryContactEmail")}>
              <input
                value={generalSettings.primaryContactEmail}
                onChange={(event) => updateGeneralSetting("primaryContactEmail", event.target.value)}
              />
            </SettingsField>
            <SettingsField label={t("settings.supportPhone")}>
              <input value={generalSettings.supportPhone} onChange={(event) => updateGeneralSetting("supportPhone", event.target.value)} />
            </SettingsField>
          </div>
        </SettingsSection>

        <SettingsSection
          title={t("settings.sections.localization.title")}
          description={t("settings.sections.localization.description")}
          actions={
            <Button type="button" variant="ghost" onClick={() => handleSaveDraft(t("settings.sections.localization.title"))}>
              {t("common.save")}
            </Button>
          }
        >
          <div className="settings-row" style={{ alignItems: "flex-start" }}>
            <SettingsField label={t("settings.defaultLanguage")}>
              <select
                value={localizationSettings.language}
                onChange={(event) => updateLocalizationSetting("language", event.target.value as "th" | "en")}
              >
                <option value="th">{t("language.thai")}</option>
                <option value="en">{t("language.english")}</option>
              </select>
            </SettingsField>
            <SettingsField label={t("settings.timezone")}>
              <select
                value={localizationSettings.timezone}
                onChange={(event) => updateLocalizationSetting("timezone", event.target.value as "bangkok" | "utc")}
              >
                <option value="bangkok">{t("settings.localization.timezone.bangkok")}</option>
                <option value="utc">{t("settings.localization.timezone.utc")}</option>
              </select>
            </SettingsField>
            <SettingsField label={t("settings.dateFormat")}>
              <select
                value={localizationSettings.dateFormat}
                onChange={(event) => updateLocalizationSetting("dateFormat", event.target.value as "compact" | "iso")}
              >
                <option value="compact">{t("settings.localization.dateFormat.compact")}</option>
                <option value="iso">{t("settings.localization.dateFormat.iso")}</option>
              </select>
            </SettingsField>
          </div>
        </SettingsSection>

        <SettingsSection
          title={t("settings.sections.security.title")}
          description={t("settings.sections.security.description")}
          actions={
            <Button type="button" variant="ghost" onClick={() => handleSaveDraft(t("settings.sections.security.title"))}>
              {t("common.save")}
            </Button>
          }
        >
          <div style={{ display: "grid", gap: "12px" }}>
            <SettingsToggle
              checked={accessSettings.mfaEnabled}
              description={t("settings.security.mfaDescription")}
              label={t("settings.security.mfa")}
              onChange={(checked) => updateAccessSetting("mfaEnabled", checked)}
            />
            <SettingsToggle
              checked={accessSettings.allowPreviewNotifications}
              description={t("settings.security.previewNotificationsDescription")}
              label={t("settings.security.previewNotifications")}
              onChange={(checked) => updateAccessSetting("allowPreviewNotifications", checked)}
            />
            <SettingsField label={t("settings.security.sessionTimeout")}>
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
          title={t("settings.sections.theme.title")}
          description={t("settings.sections.theme.description")}
          actions={
            <Button type="button" variant="ghost" onClick={() => handleSaveDraft(t("settings.sections.theme.title"))}>
              {t("common.save")}
            </Button>
          }
        >
          <div style={{ display: "grid", gap: "12px" }}>
            <p style={{ margin: 0, color: "var(--text-mid)" }}>{t("settings.theme.note")}</p>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
                gap: "12px",
              }}
            >
              <div style={{ padding: "14px", borderRadius: "16px", background: "var(--surface2)" }}>
                <span style={{ display: "block", color: "var(--text-mid)", fontSize: "0.78rem" }}>{t("settings.theme.activeRole")}</span>
                <strong>{activeRole ? formatRole(activeRole) : formatRole("admin")}</strong>
              </div>
              <div style={{ padding: "14px", borderRadius: "16px", background: "var(--surface2)" }}>
                <span style={{ display: "block", color: "var(--text-mid)", fontSize: "0.78rem" }}>{t("settings.theme.accent")}</span>
                <strong>{activeTheme.accent}</strong>
              </div>
              <div style={{ padding: "14px", borderRadius: "16px", background: "var(--surface2)" }}>
                <span style={{ display: "block", color: "var(--text-mid)", fontSize: "0.78rem" }}>{t("settings.theme.shellTitle")}</span>
                <strong>{activeTheme.shellTitle}</strong>
              </div>
            </div>
          </div>
        </SettingsSection>
      </div>
    </div>
  );
}
