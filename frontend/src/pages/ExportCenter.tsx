import { useCallback } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { useAsyncData } from "@/hooks/useAsyncData";
import { useI18n } from "@/i18n";
import { buildDocumentExportUrl } from "@/services/documents.service";
import {
  getPaperDistributionAssignments,
  getStaffWorkloadReport,
  type PaperDistributionAssignmentRow,
  type WorkloadSummaryRow,
} from "@/services/optimizer.service";
import { useAuth } from "@/store/auth.store";
import { formatDate, formatNumber } from "@/utils/format";
import { getEffectiveRole } from "@/utils/roles";

function openExport(url: string) {
  window.open(url, "_blank", "noopener,noreferrer");
}

function ExportCard({
  title,
  description,
  actions,
}: {
  title: string;
  description: string;
  actions: Array<{ label: string; onClick: () => void }>;
}) {
  return (
    <div className="import-summary-card export-center-card">
      <strong>{title}</strong>
      <span>{description}</span>
      <div className="inline-actions">
        {actions.map((action) => (
          <Button key={action.label} type="button" size="sm" variant="outline" onClick={action.onClick}>
            {action.label}
          </Button>
        ))}
      </div>
    </div>
  );
}

export function ExportCenterPage() {
  const { t } = useI18n();
  const { user } = useAuth();
  const effectiveRole = getEffectiveRole(user);
  const isAdmin = effectiveRole === "admin";

  const workloadLoader = useCallback(() => getStaffWorkloadReport(), []);
  const distributionLoader = useCallback(() => getPaperDistributionAssignments(), []);

  const workloadState = useAsyncData(workloadLoader, [workloadLoader]);
  const distributionState = useAsyncData(distributionLoader, [distributionLoader]);

  const workloadSummary = workloadState.data?.summary ?? [];
  const distributionRows = distributionState.data?.rows ?? [];

  return (
    <div className="page-stack">
      <Card title={t("exportCenter.title")} subtitle={t("exportCenter.subtitle")}>
        <div className="summary-grid">
          <div className="summary-box">
            <span>{t("exportCenter.stats.staffWorkloadRows")}</span>
            <strong>{formatNumber(workloadSummary.length)}</strong>
          </div>
          <div className="summary-box">
            <span>{t("exportCenter.stats.paperDistributionSlots")}</span>
            <strong>{formatNumber(distributionRows.length)}</strong>
          </div>
          <div className="summary-box">
            <span>{t("exportCenter.stats.totalDutyAssignments")}</span>
            <strong>{formatNumber(workloadState.data?.total_assignments ?? 0)}</strong>
          </div>
          <div className="summary-box">
            <span>{t("exportCenter.stats.fairnessSnapshot")}</span>
            <strong>{workloadState.data?.fairness_score ?? 0}</strong>
          </div>
        </div>
      </Card>

      <Card title={t("exportCenter.channels.title")} subtitle={t("exportCenter.channels.subtitle")}>
        <div className="import-summary-grid">
          <ExportCard
            title={t("exportCenter.cards.examDocuments.title")}
            description={t("exportCenter.cards.examDocuments.description")}
            actions={[
              { label: t("exportCenter.actions.allDocuments"), onClick: () => openExport(buildDocumentExportUrl({ document_type: "all" })) },
              { label: t("exportCenter.actions.participantCodes"), onClick: () => openExport(buildDocumentExportUrl({ document_type: "participant_codes" })) },
              { label: t("exportCenter.actions.signatureSheets"), onClick: () => openExport(buildDocumentExportUrl({ document_type: "signature_sheet" })) },
              { label: t("exportCenter.actions.coverSheets"), onClick: () => openExport(buildDocumentExportUrl({ document_type: "envelope_cover" })) },
            ]}
          />
          <ExportCard
            title={t("exportCenter.cards.optimizationResults.title")}
            description={t("exportCenter.cards.optimizationResults.description")}
            actions={[
              { label: t("exportCenter.actions.schedulePdf"), onClick: () => openExport("/api/exports/schedule") },
              { label: t("exportCenter.actions.scheduleExcel"), onClick: () => openExport("/api/exports/schedule-excel") },
              { label: t("exportCenter.actions.paperDistributionPdf"), onClick: () => openExport("/api/exports/paper-distribution-pdf") },
              { label: t("exportCenter.actions.paperDistributionExcel"), onClick: () => openExport("/api/exports/paper-distribution-excel") },
            ]}
          />
          <ExportCard
            title={t("exportCenter.cards.staffWorkload.title")}
            description={t("exportCenter.cards.staffWorkload.description")}
            actions={[
              { label: t("exportCenter.actions.summaryPdf"), onClick: () => openExport("/api/exports/workload-summary-pdf") },
              { label: t("exportCenter.actions.workloadSummary"), onClick: () => openExport("/api/exports/workload-summary-excel") },
              { label: t("exportCenter.actions.dutyDetail"), onClick: () => openExport("/api/exports/workload-detail-excel") },
              { label: t("exportCenter.actions.fairnessSheet"), onClick: () => openExport("/api/exports/workload-summary-excel") },
            ]}
          />
          <ExportCard
            title={t("exportCenter.cards.copyReports.title")}
            description={t("exportCenter.cards.copyReports.description")}
            actions={[
              { label: t("exportCenter.actions.openCopyCount"), onClick: () => { window.location.href = "/copy"; } },
            ]}
          />
          {isAdmin ? (
            <>
              <ExportCard
                title={t("exportCenter.cards.workflowReports.title")}
                description={t("exportCenter.cards.workflowReports.description")}
                actions={[
                  { label: t("exportCenter.actions.openWorkflow"), onClick: () => { window.location.href = "/workflow"; } },
                ]}
              />
              <ExportCard
                title={t("exportCenter.cards.externalExams.title")}
                description={t("exportCenter.cards.externalExams.description")}
                actions={[
                  { label: t("exportCenter.actions.openExternalExams"), onClick: () => { window.location.href = "/external"; } },
                ]}
              />
              <ExportCard
                title="Historical schedule review"
                description="Open the imported final-adjusted and optimized-baseline 2/2568 snapshots, compare differences, and export historical workload CSV files."
                actions={[
                  { label: "Open historical review", onClick: () => { window.location.href = "/historical-schedules"; } },
                ]}
              />
            </>
          ) : null}
        </div>
      </Card>

      <Card title={t("exportCenter.workload.title")} subtitle={t("exportCenter.workload.subtitle")}>
        {workloadState.loading ? (
          <div className="page-stack">
            <div className="dashboard-skeleton" />
          </div>
        ) : workloadSummary.length === 0 ? (
          <EmptyState
            icon={<Icon name="groups" />}
            title={t("exportCenter.workload.emptyTitle")}
            description={t("exportCenter.workload.emptyDescription")}
          />
        ) : (
          <DataTable<WorkloadSummaryRow>
            columns={[
              {
                key: "staff_name",
                label: t("common.staff"),
                width: "28%",
                render: (row) => (
                  <div className="data-table__content data-table__content--clamp">
                    <strong>{row.staff_name}</strong>
                    <p>{row.department || t("exportCenter.table.noDepartment")}</p>
                  </div>
                ),
              },
              { key: "invigilation_count", label: t("exportCenter.table.invigilation"), width: "12%" },
              { key: "paper_distribution_count", label: t("exportCenter.table.paperDistribution"), width: "16%" },
              { key: "external_exam_count", label: t("exportCenter.table.external"), width: "12%" },
              { key: "total_workload", label: t("exportCenter.table.currentTotal"), width: "12%" },
              { key: "historical_total_workload", label: t("exportCenter.table.historicalTotal"), width: "20%" },
            ]}
            emptyTitle={t("exportCenter.workload.emptyTitle")}
            emptyDescription={t("exportCenter.workload.tableEmptyDescription")}
            loading={false}
            rowKey={(row) => row.user_id}
            rows={workloadSummary}
            scrollThreshold={5}
            tableLayout="fixed"
          />
        )}
      </Card>

      <Card title={t("exportCenter.paperDistribution.title")} subtitle={t("exportCenter.paperDistribution.subtitle")}>
        <DataTable<PaperDistributionAssignmentRow>
          columns={[
            {
              key: "staff_name",
              label: t("common.staff"),
              width: "18%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <strong>{row.staff_name}</strong>
                  <p>{row.department || t("exportCenter.table.noDepartment")}</p>
                </div>
              ),
            },
            {
              key: "exam_date",
              label: t("exportCenter.table.slot"),
              width: "16%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <strong>{formatDate(row.exam_date)}</strong>
                  <p>{row.exam_time}</p>
                </div>
              ),
            },
            {
              key: "covered_courses",
              label: t("exportCenter.table.coursesCovered"),
              width: "28%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <p>{row.covered_courses.join(", ") || t("exportCenter.table.slotWideCoverage")}</p>
                </div>
              ),
            },
            {
              key: "covered_rooms",
              label: t("common.room"),
              width: "16%",
              render: (row) => <span>{row.covered_rooms.join(", ") || "-"}</span>,
            },
            { key: "covered_schedule_count", label: t("exportCenter.table.schedules"), width: "10%" },
            { key: "workload_count", label: t("exportCenter.table.load"), width: "12%" },
          ]}
          emptyTitle={t("exportCenter.paperDistribution.emptyTitle")}
          emptyDescription={t("exportCenter.paperDistribution.emptyDescription")}
          loading={distributionState.loading}
          rowKey={(row) => row.id}
          rows={distributionRows}
          scrollThreshold={5}
          tableLayout="fixed"
        />
      </Card>
    </div>
  );
}
