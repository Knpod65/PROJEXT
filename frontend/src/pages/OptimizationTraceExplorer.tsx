import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { DashboardMetricCard } from "@/components/dashboard/DashboardMetricCard";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, type DataTableColumn } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { FormField } from "@/components/ui/FormField";
import { Icon } from "@/components/ui/Icon";
import { InlineError } from "@/components/ui/InlineError";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageSkeleton } from "@/components/ui/PageSkeleton";
import { StatusChip } from "@/components/ui/StatusChip";
import { Tabs } from "@/components/ui/Tabs";
import { useOptimizationTraceExplorer } from "@/hooks/domain/useOptimizationTraceExplorer";
import { useI18n } from "@/i18n";
import type { RecheckIssueItem, TraceCandidate, TraceConstraintHit } from "@/types/optimizationTrace";
import {
  getTraceDisplayState,
  getTraceGovernance,
  traceConstraintTone,
  traceSeverityTone,
} from "@/utils/presenters/optimizationTracePresenter";

type DetailTab = "candidates" | "constraints" | "recheck";

export default function OptimizationTraceExplorer() {
  const navigate = useNavigate();
  const { locale, t } = useI18n();
  const {
    isLoading,
    error,
    refresh,
    trace,
    traceSummary,
    timelineItems,
    constraintItems,
    selectedSessionId,
    setSelectedSessionId,
    mockSessions,
  } = useOptimizationTraceExplorer();
  const [activeTab, setActiveTab] = useState<DetailTab>("candidates");

  const displayState = getTraceDisplayState(trace, error);
  const governance = trace ? getTraceGovernance(trace) : null;
  const selectedCount = trace?.candidates.filter((candidate) => candidate.selected).length ?? 0;

  const candidateColumns = useMemo<Array<DataTableColumn<TraceCandidate>>>(() => [
    { key: "room_code", label: t("trace.room") },
    { key: "timeslot", label: t("trace.timeslot") },
    { key: "staff_id", label: t("trace.staff") },
    { key: "score", label: t("trace.score"), align: "right" },
    {
      key: "selected",
      label: t("trace.status"),
      render: (row) => (
        <StatusChip tone={row.selected ? "success" : "neutral"}>
          {t(row.selected ? "trace.candidate.selected" : "trace.candidate.alternative")}
        </StatusChip>
      ),
    },
    {
      key: "rejection_reasons",
      label: t("trace.rejectionReasons"),
      render: (row) => row.rejection_reasons.length > 0 ? row.rejection_reasons.join(", ") : t("common.none"),
    },
  ], [t]);

  const constraintColumns = useMemo<Array<DataTableColumn<TraceConstraintHit>>>(() => [
    {
      key: "constraint_type",
      label: t("trace.constraint"),
      render: (row) => t(`trace.constraintType.${row.constraint_type}`),
    },
    { key: "detail", label: t("common.details") },
    {
      key: "severity",
      label: t("trace.severity"),
      render: (row) => <StatusChip tone={traceSeverityTone(row.severity)}>{t(`trace.constraintSeverity.${row.severity}`)}</StatusChip>,
    },
    {
      key: "passed",
      label: t("trace.status"),
      render: (row) => <StatusChip tone={traceConstraintTone(row)}>{t(row.passed ? "trace.constraint.passed" : "trace.constraint.failed")}</StatusChip>,
    },
  ], [t]);

  const recheckColumns = useMemo<Array<DataTableColumn<RecheckIssueItem>>>(() => [
    { key: "issue", label: t("trace.recheckIssue") },
    {
      key: "severity",
      label: t("trace.severity"),
      render: (row) => <StatusChip tone={traceSeverityTone(row.severity)}>{t(`severity.${row.severity}`)}</StatusChip>,
    },
  ], [t]);

  if (isLoading) return <PageSkeleton cards={4} rows={4} />;

  const sessionControl = (
    <FormField label={t("trace.sessionLabel")}>
      <select value={selectedSessionId} onChange={(event) => setSelectedSessionId(Number(event.target.value))}>
        {mockSessions.map((session) => <option key={session.id} value={session.id}>{session.label}</option>)}
      </select>
    </FormField>
  );

  if (displayState === "queryError" || displayState === "missingSession") {
    return (
      <div className="page-stack page-stack--spacious">
        <PageHeader
          eyebrow={t("trace.eyebrow")}
          title={t("trace.pageTitle")}
          description={t("trace.description")}
          actions={sessionControl}
        />
        {displayState === "queryError" ? (
          <InlineError
            message={t("trace.loadErrorExplanation")}
            action={<Button type="button" variant="outline" onClick={refresh}>{t("common.retry")}</Button>}
          />
        ) : null}
        <Card>
          <EmptyState
            icon={<Icon name="search_off" />}
            title={t(displayState === "queryError" ? "trace.loadError" : "trace.missingSession.title")}
            description={t(displayState === "queryError" ? "trace.loadErrorExplanation" : "trace.missingSession.description")}
            action={(
              <div className="inline-actions">
                <Button type="button" variant="outline" onClick={refresh}>{t("common.retry")}</Button>
                <Button type="button" onClick={() => navigate("/optimizer")}>{t("trace.backToOptimizer")}</Button>
              </div>
            )}
          />
        </Card>
      </div>
    );
  }

  if (!trace || !governance) return null;

  const detailTabs = [
    { key: "candidates", label: t("trace.candidates"), badge: trace.candidates.length },
    { key: "constraints", label: t("trace.constraints"), badge: constraintItems.length },
    { key: "recheck", label: t("trace.recheckIssues"), badge: trace.recheck_issues.length },
  ];

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        eyebrow={t("trace.eyebrow")}
        title={t("trace.pageTitle")}
        description={t("trace.description")}
        status={<StatusChip tone={governance.tone}>{t(`trace.governance.${governance.key}`)}</StatusChip>}
        actions={sessionControl}
      />

      <Card className="context-strip">
        <div className="context-strip__item">
          <span>{t("trace.sessionLabel")}</span>
          <strong>{mockSessions.find((session) => session.id === selectedSessionId)?.label}</strong>
        </div>
        <div className="context-strip__item">
          <span>{t("trace.generatedAt")}</span>
          <strong>{new Date(trace.generated_at).toLocaleString(locale)}</strong>
        </div>
        <div className="context-strip__item">
          <span>{t("trace.traceState")}</span>
          <StatusChip tone={displayState === "limited" ? "warning" : "success"}>
            {t(`trace.state.${displayState}`)}
          </StatusChip>
        </div>
      </Card>

      <section className="summary-grid" aria-label={t("trace.summary")}>
        <DashboardMetricCard icon="speed" label={t("trace.completeness")} value={`${traceSummary.traceabilityCompletenessScore} / 100`} hint={t("trace.completenessHint")} tone="accent" />
        <DashboardMetricCard icon="account_tree" label={t("trace.optionCount")} value={String(trace.candidates.length)} hint={t("trace.optionCountHint")} tone="neutral" />
        <DashboardMetricCard icon="task_alt" label={t("trace.selectedCount")} value={String(selectedCount)} hint={t("trace.selectedCountHint")} tone={selectedCount > 0 ? "success" : "neutral"} />
        <DashboardMetricCard icon="gavel" label={t("trace.governanceStatus")} value={t(`trace.governance.${governance.key}`)} hint={t("trace.governanceHint")} tone={governance.tone === "danger" ? "warning" : governance.tone === "success" ? "success" : "neutral"} />
      </section>

      <Card title={t("trace.events")} subtitle={t("trace.eventsDescription")}>
        {timelineItems.length > 0 ? (
          <div className="trace-timeline">
            {timelineItems.map((event) => (
              <article className="trace-timeline__item" key={event.id}>
                <div className="trace-timeline__marker"><Icon name="timeline" /></div>
                <div className="trace-timeline__content">
                  <strong>{event.detail}</strong>
                  <span>{t(`trace.eventType.${event.event_type}`)} · {t(`trace.stage.${event.stage}`)}</span>
                </div>
                <div className="trace-timeline__meta">
                  <time>{new Date(event.timestamp).toLocaleString(locale)}</time>
                  <StatusChip tone={traceSeverityTone(event.severity)}>{t(`severity.${event.severity}`)}</StatusChip>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <EmptyState title={t("trace.noEvents")} description={t("trace.noEventsDescription")} />
        )}
      </Card>

      <Card title={t("trace.detailsTitle")} subtitle={t("trace.detailsDescription")}>
        <Tabs activeKey={activeTab} items={detailTabs} onChange={(key) => setActiveTab(key as DetailTab)} />
        <div className="tab-panel">
          {activeTab === "candidates" ? <DataTable columns={candidateColumns} rows={trace.candidates} rowKey={(row) => row.candidate_id} compact emptyTitle={t("trace.noCandidates")} /> : null}
          {activeTab === "constraints" ? <DataTable columns={constraintColumns} rows={constraintItems} rowKey={(row) => `${row.constraint_type}:${row.detail}`} compact emptyTitle={t("trace.noConstraints")} /> : null}
          {activeTab === "recheck" ? <DataTable columns={recheckColumns} rows={trace.recheck_issues} rowKey={(row) => `${row.severity}:${row.issue}`} compact emptyTitle={t("trace.noRecheckIssues")} /> : null}
        </div>
      </Card>
    </div>
  );
}
