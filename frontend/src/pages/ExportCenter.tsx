import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { PageHeader } from "@/components/ui/PageHeader";
import { useExportCenterPage } from "@/hooks/domain/useExportCenterPage";
import { useI18n } from "@/i18n";
import { type PaperDistributionAssignmentRow, type WorkloadSummaryRow } from "@/services/optimizer.service";
import { formatDate } from "@/utils/format";

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
  const {
    stats,
    exportCards,
    isAdmin,
    workloadLoading,
    workloadSummary,
    distributionLoading,
    distributionRows,
  } = useExportCenterPage();

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        className="page-hero--dashboard"
        eyebrow={t("navigation.pages.exports-center.title")}
        title={t("exportCenter.title")}
        description={t("exportCenter.subtitle")}
      />

      <Card title={t("exportCenter.title")} subtitle={t("exportCenter.subtitle")}>
        <div className="summary-grid">
          {stats.map((stat) => (
            <div key={stat.label} className="summary-box">
              <span>{stat.label}</span>
              <strong>{stat.value}</strong>
            </div>
          ))}
        </div>
      </Card>

      <Card title={t("exportCenter.channels.title")} subtitle={t("exportCenter.channels.subtitle")}>
        <div className="import-summary-grid">
          {exportCards.map((card) => (
            <ExportCard key={card.title} title={card.title} description={card.description} actions={card.actions} />
          ))}
        </div>
      </Card>

      <Card title={t("exportCenter.workload.title")} subtitle={t("exportCenter.workload.subtitle")}>
        {workloadLoading ? (
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
          loading={distributionLoading}
          rowKey={(row) => row.id}
          rows={distributionRows}
          scrollThreshold={5}
          tableLayout="fixed"
        />
      </Card>
    </div>
  );
}
