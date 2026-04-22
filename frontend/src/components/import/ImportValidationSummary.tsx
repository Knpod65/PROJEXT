import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { useI18n } from "@/i18n";
import type { ImportV2IssueSummaryItem } from "@/types/api";

interface ImportValidationSummaryProps {
  totalRows: number;
  validCount: number;
  warningCount: number;
  errorCount: number;
  errorSummary: ImportV2IssueSummaryItem[];
  warningSummary: ImportV2IssueSummaryItem[];
}

export function ImportValidationSummary({
  errorCount,
  errorSummary,
  totalRows,
  validCount,
  warningCount,
  warningSummary,
}: ImportValidationSummaryProps) {
  const { t } = useI18n();

  return (
    <div className="page-stack">
      <div className="import-summary-grid" role="list" aria-label={t("import.v2.validationTotalsAria")}>
        <article className="import-summary-card" role="listitem">
          <span>{t("import.v2.totalRows")}</span>
          <strong>{totalRows}</strong>
        </article>
        <article className="import-summary-card" role="listitem">
          <span>{t("import.v2.valid")}</span>
          <strong>{validCount}</strong>
        </article>
        <article className="import-summary-card" role="listitem">
          <span>{t("import.v2.warnings")}</span>
          <strong>{warningCount}</strong>
        </article>
        <article className="import-summary-card" role="listitem">
          <span>{t("import.v2.errors")}</span>
          <strong>{errorCount}</strong>
        </article>
      </div>

      <div className="dashboard-shell-grid">
        <Card title={t("import.v2.errorSummaryTitle")} subtitle={t("import.v2.errorSummarySubtitle")}>
          {errorSummary.length === 0 ? (
            <p className="empty-state__description">{t("import.v2.noBlockingErrors")}</p>
          ) : (
            <div className="page-stack">
              {errorSummary.map((item) => (
                <div key={`${item.code}-${item.message}`} className="signer-list__item">
                  <div>
                    <strong>{item.code}</strong>
                    <p>{item.message}</p>
                  </div>
                  <Badge variant="crimson">{item.count}</Badge>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card title={t("import.v2.warningSummaryTitle")} subtitle={t("import.v2.warningSummarySubtitle")}>
          {warningSummary.length === 0 ? (
            <p className="empty-state__description">{t("import.v2.noWarnings")}</p>
          ) : (
            <div className="page-stack">
              {warningSummary.map((item) => (
                <div key={`${item.code}-${item.message}`} className="signer-list__item">
                  <div>
                    <strong>{item.code}</strong>
                    <p>{item.message}</p>
                  </div>
                  <Badge variant="gold">{item.count}</Badge>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
