import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useSettingsPage } from "@/hooks/domain/useSettingsPage";
import { useI18n } from "@/i18n";

export function SettingsPage() {
  const { t } = useI18n();
  const {
    isLoading,
    sections,
    drafts,
    updateDraft,
    save,
    hasData,
  } = useSettingsPage();

  if (!hasData) return null;

  return (
    <div className="page-stack">
      {sections.map((section) => (
        <Card key={section.key} title={section.key} subtitle={section.description}>
          <div className="settings-row">
            <input
              onChange={(event) => updateDraft(section.key, event.target.value)}
              value={drafts[section.key] ?? ""}
            />
            <Button type="button" onClick={() => void save(section.key)} disabled={isLoading}>
              {t("common.save")}
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );
}
