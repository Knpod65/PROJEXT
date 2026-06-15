import { AlertBanner } from "@/components/ui/AlertBanner";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageSkeleton } from "@/components/ui/PageSkeleton";
import { StatusChip } from "@/components/ui/StatusChip";
import { useExecutiveAnalyticsPage } from "@/hooks/domain/useExecutiveAnalyticsPage";
import { useI18n } from "@/i18n";
import { formatNumber } from "@/utils/format";
import { statusLabel, statusTone } from "@/utils/statusPresentation";

export default function ExecutiveAnalytics() {
  const { t } = useI18n();
  const { data, error, isLoading, kpiGrid, recommendedActions, scoreSuffix, topRisks } = useExecutiveAnalyticsPage();

  if (isLoading) return <PageSkeleton cards={4} rows={4} />;
  if (error || !data) {
    return <EmptyState icon={<Icon name="warning" />} title={t("analytics.loadError")} description={error instanceof Error ? error.message : t("analytics.noData")} />;
  }

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        className="page-hero--dashboard"
        eyebrow={t("analytics.eyebrow")}
        title={t("analytics.title")}
        description={t("analytics.description")}
        status={<StatusChip tone={statusTone(data.risk_band)}>{statusLabel(data.risk_band)}</StatusChip>}
      />

      <section className="executive-summary">
        <Card title={t("analytics.overallHealthScore")} subtitle={t("analytics.healthExplanation")}>
          <div className="executive-health-score">
            <strong>{formatNumber(data.overall_health_score)}</strong>
            <span>{scoreSuffix}</span>
          </div>
        </Card>
        <div className="stitch-metric-grid executive-kpi-grid">
          {kpiGrid.filter((kpi) => kpi.key !== "health").map((kpi) => (
            <article className="executive-kpi" key={kpi.key}>
              <span>{kpi.label}</span>
              <strong>{formatNumber(kpi.value)}</strong>
            </article>
          ))}
        </div>
      </section>

      {topRisks.length > 0 ? (
        <AlertBanner variant="warning" title={t("analytics.risksTitle")}>
          {t("analytics.risksDescription", { count: topRisks.length })}
        </AlertBanner>
      ) : (
        <AlertBanner variant="success" title={t("analytics.noRisks")}>{t("analytics.noRisksDescription")}</AlertBanner>
      )}

      <section className="executive-detail-grid">
        <Card title={t("analytics.risksTitle")} subtitle={t("analytics.risksSubtitle")}>
          {topRisks.length ? (
            <div className="executive-list">
              {topRisks.map((risk, index) => (
                <article className="executive-list__item" key={`${risk.risk}-${index}`}>
                  <div><strong>{risk.risk}</strong><span>{risk.category}</span></div>
                  <StatusChip tone={statusTone(risk.severity)}>{statusLabel(risk.severity)}</StatusChip>
                </article>
              ))}
            </div>
          ) : <EmptyState title={t("analytics.noRisks")} />}
        </Card>

        <Card title={t("analytics.actionsTitle")} subtitle={t("analytics.actionsSubtitle")}>
          {recommendedActions.length ? (
            <div className="executive-list">
              {recommendedActions.map((action, index) => (
                <article className="executive-list__item" key={`${action.action}-${index}`}>
                  <div><strong>{action.action}</strong><span>{t("analytics.owner", { owner: action.owner })}</span></div>
                  <StatusChip tone={statusTone(action.priority)}>{statusLabel(action.priority)}</StatusChip>
                </article>
              ))}
            </div>
          ) : <EmptyState title={t("analytics.noActions")} />}
        </Card>
      </section>
    </div>
  );
}
