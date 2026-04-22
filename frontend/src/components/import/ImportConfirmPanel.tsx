import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { useI18n } from "@/i18n";
import type { ImportV2ConfirmCheckResponse, ImportV2PrepareResponse } from "@/types/api";

interface ImportConfirmPanelProps {
  prepareResult: ImportV2PrepareResponse | null;
  confirmCheck: ImportV2ConfirmCheckResponse | null;
}

export function ImportConfirmPanel({ confirmCheck, prepareResult }: ImportConfirmPanelProps) {
  const { t } = useI18n();
  const importable = confirmCheck?.importable_count ?? 0;
  const skipped = prepareResult?.skipped_count ?? 0;
  const overridden = confirmCheck?.override_count ?? 0;

  return (
    <div className="dashboard-shell-grid">
      <Card title={t("import.v2.finalBatchCounts")} subtitle={t("import.v2.finalBatchCountsSubtitle")}>
        <div className="import-summary-grid">
          <article className="import-summary-card">
            <span>{t("import.v2.importable")}</span>
            <strong>{importable}</strong>
          </article>
          <article className="import-summary-card">
            <span>{t("import.v2.skipped")}</span>
            <strong>{skipped}</strong>
          </article>
          <article className="import-summary-card">
            <span>{t("import.v2.overridden")}</span>
            <strong>{overridden}</strong>
          </article>
        </div>
      </Card>

      <Card title={t("import.v2.executionWarning")} subtitle={t("import.v2.executionWarningSubtitle")}>
        <div className="page-stack">
          <p className="import-issue import-issue--warning">{t("import.v2.executionWriteWarning")}</p>
          <p className="import-issue import-issue--error">{t("import.v2.executionUndoWarning")}</p>
          <div className="signer-list__item">
            <strong>{t("import.v2.executionReadiness")}</strong>
            <Badge variant={confirmCheck?.ready_for_execution ? "green" : "crimson"}>
              {confirmCheck?.ready_for_execution ? t("import.v2.ready") : t("import.v2.blocking")}
            </Badge>
          </div>
        </div>
      </Card>

      <Card title={t("import.v2.blockingReasons")} subtitle={t("import.v2.blockingReasonsSubtitle")}>
        {!confirmCheck || confirmCheck.blocking_reasons.length === 0 ? (
          <p className="empty-state__description">{t("import.v2.noBlockingReasons")}</p>
        ) : (
          <div className="page-stack">
            {confirmCheck.blocking_reasons.map((reason) => (
              <div key={`${reason.code}-${reason.message}`} className="signer-list__item">
                <div>
                  <strong>{reason.code}</strong>
                  <p>{reason.message}</p>
                </div>
                <Badge variant="crimson">{reason.count}</Badge>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
