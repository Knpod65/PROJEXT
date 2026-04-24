import { useCallback } from "react";

import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Button } from "@/components/ui/Button";
import { useAsyncData } from "@/hooks/useAsyncData";
import { buildDocumentExportUrl } from "@/services/documents.service";
import {
  getPaperDistributionAssignments,
  getStaffWorkloadReport,
  type PaperDistributionAssignmentRow,
  type WorkloadSummaryRow,
} from "@/services/optimizer.service";
import { useAuth } from "@/store/auth.store";
import { formatDate, formatNumber } from "@/utils/format";

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
  const { user } = useAuth();
  const effectiveRole = user?.effective_role ?? user?.active_role ?? user?.role ?? null;
  const isAdmin = effectiveRole === "admin";

  const workloadLoader = useCallback(() => getStaffWorkloadReport(), []);
  const distributionLoader = useCallback(() => getPaperDistributionAssignments(), []);

  const workloadState = useAsyncData(workloadLoader, [workloadLoader]);
  const distributionState = useAsyncData(distributionLoader, [distributionLoader]);

  const workloadSummary = workloadState.data?.summary ?? [];
  const distributionRows = distributionState.data?.rows ?? [];

  return (
    <div className="page-stack">
      <Card
        title="Export Center"
        subtitle="Centralize operational exports for schedules, documents, workload, and staffing assignments."
      >
        <div className="summary-grid">
          <div className="summary-box">
            <span>Staff workload rows</span>
            <strong>{formatNumber(workloadSummary.length)}</strong>
          </div>
          <div className="summary-box">
            <span>Paper distribution slots</span>
            <strong>{formatNumber(distributionRows.length)}</strong>
          </div>
          <div className="summary-box">
            <span>Total duty assignments</span>
            <strong>{formatNumber(workloadState.data?.total_assignments ?? 0)}</strong>
          </div>
          <div className="summary-box">
            <span>Fairness snapshot</span>
            <strong>{workloadState.data?.fairness_score ?? 0}</strong>
          </div>
        </div>
      </Card>

      <Card title="Export channels" subtitle="Choose the report family, then export directly from this hub.">
        <div className="import-summary-grid">
          <ExportCard
            title="Exam documents"
            description="Participant codes, signature sheets, and envelope cover sheets from confirmed exam schedules."
            actions={[
              { label: "All documents", onClick: () => openExport(buildDocumentExportUrl({ document_type: "all" })) },
              { label: "Participant codes", onClick: () => openExport(buildDocumentExportUrl({ document_type: "participant_codes" })) },
              { label: "Signature sheets", onClick: () => openExport(buildDocumentExportUrl({ document_type: "signature_sheet" })) },
              { label: "Cover sheets", onClick: () => openExport(buildDocumentExportUrl({ document_type: "envelope_cover" })) },
            ]}
          />
          <ExportCard
            title="Optimization results"
            description="Master exam schedule and room/invigilator allocations."
            actions={[
              { label: "Schedule PDF", onClick: () => openExport("/api/exports/schedule") },
              { label: "Schedule Excel", onClick: () => openExport("/api/exports/schedule-excel") },
              { label: "Paper distribution PDF", onClick: () => openExport("/api/exports/paper-distribution-pdf") },
              { label: "Paper distribution Excel", onClick: () => openExport("/api/exports/paper-distribution-excel") },
            ]}
          />
          <ExportCard
            title="Staff workload reports"
            description="Duty counts by type, detail by slot, and fairness-aware workload exports."
            actions={[
              { label: "Summary PDF", onClick: () => openExport("/api/exports/workload-summary-pdf") },
              { label: "Workload summary", onClick: () => openExport("/api/exports/workload-summary-excel") },
              { label: "Duty detail", onClick: () => openExport("/api/exports/workload-detail-excel") },
              { label: "Fairness sheet", onClick: () => openExport("/api/exports/workload-summary-excel") },
            ]}
          />
          <ExportCard
            title="Copy / print reports"
            description="Use the print-operations page for live copy count and teacher print details."
            actions={[
              { label: "Open Copy Count", onClick: () => { window.location.href = "/copy"; } },
            ]}
          />
          {isAdmin ? (
            <>
              <ExportCard
                title="Workflow reports"
                description="Approval status and issue review remain available in the workflow checkpoint."
                actions={[
                  { label: "Open Workflow", onClick: () => { window.location.href = "/workflow"; } },
                ]}
              />
              <ExportCard
                title="External exams"
                description="Staff-only external exam operations remain available from the External Exams module."
                actions={[
                  { label: "Open External Exams", onClick: () => { window.location.href = "/external"; } },
                ]}
              />
            </>
          ) : null}
        </div>
      </Card>

      <Card title="Staff workload summary" subtitle="Combined invigilation, paper distribution, and external duty counts for the active period.">
        {workloadState.loading ? (
          <div className="page-stack">
            <div className="dashboard-skeleton" />
          </div>
        ) : workloadSummary.length === 0 ? (
          <EmptyState
            icon={<Icon name="groups" />}
            title="No workload data yet"
            description="Run optimization or assign operational duties first, then export from this center."
          />
        ) : (
          <DataTable<WorkloadSummaryRow>
            columns={[
              {
                key: "staff_name",
                label: "Staff",
                width: "28%",
                render: (row) => (
                  <div className="data-table__content data-table__content--clamp">
                    <strong>{row.staff_name}</strong>
                    <p>{row.department || "No department"}</p>
                  </div>
                ),
              },
              { key: "invigilation_count", label: "Invigilation", width: "12%" },
              { key: "paper_distribution_count", label: "Paper distribution", width: "16%" },
              { key: "external_exam_count", label: "External", width: "12%" },
              { key: "total_workload", label: "Current total", width: "12%" },
              { key: "historical_total_workload", label: "Historical total", width: "20%" },
            ]}
            emptyTitle="No workload data"
            emptyDescription="Assignments will appear here after optimization or manual staffing."
            loading={false}
            rowKey={(row) => row.user_id}
            rows={workloadSummary}
            scrollThreshold={5}
            tableLayout="fixed"
          />
        )}
      </Card>

      <Card title="Paper distribution assignments" subtitle="Slot-wide exam-paper distribution duty counts as one workload unit per slot.">
        <DataTable<PaperDistributionAssignmentRow>
          columns={[
            {
              key: "staff_name",
              label: "Staff",
              width: "18%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <strong>{row.staff_name}</strong>
                  <p>{row.department || "No department"}</p>
                </div>
              ),
            },
            {
              key: "exam_date",
              label: "Slot",
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
              label: "Courses covered",
              width: "28%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <p>{row.covered_courses.join(", ") || "Slot-wide coverage"}</p>
                </div>
              ),
            },
            {
              key: "covered_rooms",
              label: "Rooms",
              width: "16%",
              render: (row) => <span>{row.covered_rooms.join(", ") || "-"}</span>,
            },
            { key: "covered_schedule_count", label: "Schedules", width: "10%" },
            { key: "workload_count", label: "Load", width: "12%" },
          ]}
          emptyTitle="No paper-distribution assignments yet"
          emptyDescription="Run the optimizer to generate slot-based paper distribution assignments."
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
