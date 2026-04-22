import { Card } from "@/components/ui/Card";
import { useI18n } from "@/i18n";
import type { ImportV2ExecuteResponse } from "@/types/api";

interface ImportResultSummaryProps {
  result: ImportV2ExecuteResponse;
}

export function ImportResultSummary({ result }: ImportResultSummaryProps) {
  const { t } = useI18n();

  return (
    <div className="dashboard-shell-grid">
      <Card title={t("import.v2.resultSummaryTitle")} subtitle={t("import.v2.resultSummarySubtitle")}>
        <div className="import-summary-grid">
          <article className="import-summary-card">
            <span>{t("common.imported")}</span>
            <strong>{result.imported_count}</strong>
          </article>
          <article className="import-summary-card">
            <span>{t("import.v2.skipped")}</span>
            <strong>{result.skipped_count}</strong>
          </article>
          <article className="import-summary-card">
            <span>{t("import.v2.overridden")}</span>
            <strong>{result.override_count}</strong>
          </article>
          <article className="import-summary-card">
            <span>{t("import.v2.totalRows")}</span>
            <strong>{result.total_rows}</strong>
          </article>
        </div>
      </Card>

      <Card title={t("import.v2.importSessionTitle")} subtitle={t("import.v2.importSessionSubtitle")}>
        <div className="page-stack">
          <p>
            import_session_id: <strong>{result.import_session_id}</strong>
          </p>
          <a className="ui-button ui-button--outline ui-button--sm" href={`/exports/audit-logs?session_id=${result.import_session_id}`}>
            {t("import.v2.openFutureAudit")}
          </a>
        </div>
      </Card>
    </div>
  );
}
