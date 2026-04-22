import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { useI18n } from "@/i18n";
import type { ImportWizardIssue, ImportWizardRowDraft } from "@/hooks/useImportWizard";

interface ImportOverridePanelProps {
  rows: ImportWizardRowDraft[];
  issues: ImportWizardIssue[];
}

export function ImportOverridePanel({ issues, rows }: ImportOverridePanelProps) {
  const { t } = useI18n();
  const overrideCandidates = rows.filter((row) => row.status === "error" && row.can_override);
  const mappingRequired = rows.filter((row) => row.override_policy === "requires_mapping");

  return (
    <div className="dashboard-shell-grid">
      <Card title={t("import.v2.overrideCandidatesTitle")} subtitle={t("import.v2.overrideCandidatesSubtitle")}>
        {overrideCandidates.length === 0 ? (
          <p className="empty-state__description">{t("import.v2.noOverrideCandidates")}</p>
        ) : (
          <div className="page-stack">
            {overrideCandidates.map((row) => (
              <div key={row._row} className="signer-list__item">
                <div>
                  <strong>#{row._row}</strong>
                  <p>{row.override_reason ? t("import.v2.reasonProvided", { value: row.override_reason }) : t("import.v2.reasonPending")}</p>
                </div>
                <Badge variant={row.override_reason ? "green" : "gold"}>
                  {row.override_reason ? t("import.v2.ready") : t("import.v2.needsReason")}
                </Badge>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card title={t("import.v2.mappingRequiredTitle")} subtitle={t("import.v2.mappingRequiredSubtitle")}>
        {mappingRequired.length === 0 ? (
          <p className="empty-state__description">{t("import.v2.noMappingRequired")}</p>
        ) : (
          <div className="page-stack">
            {mappingRequired.map((row) => (
              <div key={row._row} className="signer-list__item">
                <div>
                  <strong>#{row._row}</strong>
                  <p>{row.errors[0] ?? t("import.v2.mappingRequiredFallback")}</p>
                </div>
                <Badge variant="orange">{t("status.requires_mapping")}</Badge>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card title={t("import.v2.overrideEnforcementTitle")} subtitle={t("import.v2.overrideEnforcementSubtitle")}>
        {issues.length === 0 ? (
          <p className="empty-state__description">{t("import.v2.overrideChecksPassed")}</p>
        ) : (
          <div className="page-stack">
            {issues.map((issue) => (
              <div key={`${issue.row}-${issue.message}`} className="signer-list__item">
                <div>
                  <strong>{issue.row > 0 ? `#${issue.row}` : t("import.v2.batchCheck")}</strong>
                  <p>{issue.message}</p>
                </div>
                <Badge variant="crimson">{t("import.v2.blocking")}</Badge>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
