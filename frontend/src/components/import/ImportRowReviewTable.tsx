import { Badge } from "@/components/ui/Badge";
import { useI18n } from "@/i18n";
import type { ImportWizardRowDraft } from "@/hooks/useImportWizard";
import { cx } from "@/utils/cx";
import { formatTranslatedValue } from "@/utils/format";

interface ImportRowReviewTableProps {
  rows: ImportWizardRowDraft[];
  onSelectRow: (rowNumber: number, selected: boolean) => void;
  onToggleOverride: (rowNumber: number, enabled: boolean) => void;
  onUpdateOverrideReason: (rowNumber: number, reason: string) => void;
  onUpdateMappingValue: (rowNumber: number, value: string) => void;
  onUpdateMappingNote: (rowNumber: number, value: string) => void;
}

function statusBadgeVariant(status: ImportWizardRowDraft["status"]) {
  if (status === "valid") {
    return "green" as const;
  }

  if (status === "warning") {
    return "gold" as const;
  }

  return "crimson" as const;
}

function policyBadgeVariant(policy: ImportWizardRowDraft["override_policy"]) {
  if (policy === "allowed") {
    return "green" as const;
  }

  if (policy === "requires_mapping") {
    return "orange" as const;
  }

  return "gray" as const;
}

export function ImportRowReviewTable({
  onSelectRow,
  onToggleOverride,
  onUpdateMappingNote,
  onUpdateMappingValue,
  onUpdateOverrideReason,
  rows,
}: ImportRowReviewTableProps) {
  const { t } = useI18n();
  const shouldScroll = rows.length > 5;

  return (
    <div
      className={cx(
        "table-wrap",
        shouldScroll && "table-wrap--scrollable",
        shouldScroll && "table-wrap--sticky",
      )}
      style={shouldScroll ? { maxHeight: "420px" } : undefined}
    >
      <table className="data-table import-review-table">
        <thead>
          <tr>
            <th>{t("import.v2.table.select")}</th>
            <th>{t("import.v2.table.row")}</th>
            <th>{t("common.status")}</th>
            <th>{t("import.v2.table.messages")}</th>
            <th>{t("import.v2.table.override")}</th>
            <th>{t("import.v2.table.mapping")}</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const isError = row.status === "error";
            const mappingRequired = row.override_policy === "requires_mapping";
            const canUseOverride = isError && row.can_override && row.override_policy === "allowed";
            const canSelect = !isError || canUseOverride;

            return (
              <tr key={row._row} className={cx(row.selected && "import-row--selected", isError && "import-row--error")}>
                <td>
                  <input
                    type="checkbox"
                    checked={row.selected}
                    disabled={!canSelect}
                    onChange={(event) => onSelectRow(row._row, event.currentTarget.checked)}
                  />
                </td>
                <td>
                  <strong>#{row._row}</strong>
                </td>
                <td>
                  <div className="page-stack" style={{ gap: "8px" }}>
                    <Badge variant={statusBadgeVariant(row.status)}>{formatTranslatedValue("status", row.status)}</Badge>
                    <Badge variant={policyBadgeVariant(row.override_policy)}>{formatTranslatedValue("status", row.override_policy)}</Badge>
                  </div>
                </td>
                <td>
                  <div className="page-stack" style={{ gap: "8px" }}>
                    {row.errors.map((message, index) => (
                      <p key={`error-${row._row}-${index}`} className="import-issue import-issue--error">
                        {message}
                      </p>
                    ))}
                    {row.warnings.map((message, index) => (
                      <p key={`warning-${row._row}-${index}`} className="import-issue import-issue--warning">
                        {message}
                      </p>
                    ))}
                    {row.errors.length === 0 && row.warnings.length === 0 ? (
                      <p className="import-issue">{t("import.v2.noIssues")}</p>
                    ) : null}
                  </div>
                </td>
                <td>
                  {isError ? (
                    <div className="page-stack" style={{ gap: "8px" }}>
                      <label className="import-inline-toggle">
                        <input
                          type="checkbox"
                          checked={row.override_enabled}
                          disabled={!canUseOverride}
                          onChange={(event) => onToggleOverride(row._row, event.currentTarget.checked)}
                        />
                        <span>{t("import.v2.enableOverride")}</span>
                      </label>
                      <textarea
                        value={row.override_reason ?? ""}
                        onChange={(event) => onUpdateOverrideReason(row._row, event.currentTarget.value)}
                        disabled={!row.override_enabled || !canUseOverride}
                        placeholder={t("import.v2.overrideReasonPlaceholder")}
                      />
                    </div>
                  ) : (
                    <Badge variant="gray">{t("import.v2.overrideNotRequired")}</Badge>
                  )}
                </td>
                <td>
                  {mappingRequired ? (
                    <div className="page-stack" style={{ gap: "8px" }}>
                      <input
                        value={row.mapping_value}
                        onChange={(event) => onUpdateMappingValue(row._row, event.currentTarget.value)}
                        placeholder={t("import.v2.mappingTarget")}
                      />
                      <input
                        value={row.mapping_note}
                        onChange={(event) => onUpdateMappingNote(row._row, event.currentTarget.value)}
                        placeholder={t("import.v2.mappingNote")}
                      />
                      <p className="import-issue import-issue--warning">
                        {t("import.v2.mappingSkipped")}
                      </p>
                    </div>
                  ) : (
                    <Badge variant="gray">{t("common.notAvailable")}</Badge>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
