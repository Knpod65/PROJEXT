import { useMemo, useState } from "react";

import { AlertBanner } from "@/components/ui/AlertBanner";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { DataTable, type DataTableColumn } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { FormField } from "@/components/ui/FormField";
import { Icon } from "@/components/ui/Icon";
import { PageHeader } from "@/components/ui/PageHeader";
import { Skeleton } from "@/components/ui/Skeleton";
import { useI18n } from "@/i18n";
import { useAdvanceBatchPreview } from "@/hooks/domain/useAdvanceBatchPreview";
import type { AdvanceBatchRosterRow } from "@/types/invigilationAdvanceBatch";
import { formatCurrency } from "@/utils/format";

function SummaryCard({ label, value, hint }: { label: string; value: string | number; hint: string }) {
  return (
    <Card title={label} subtitle={hint}>
      <p className="metric-value">{value}</p>
    </Card>
  );
}

function inclusionVariant(value: string) {
  if (value.includes("BLOCKED")) return "crimson";
  if (value.includes("READY")) return "green";
  if (value.includes("PENDING")) return "gold";
  return "gray";
}

function amountVariant(value: string) {
  if (value.includes("PENDING")) return "gold";
  if (value.includes("READY") || value.includes("OK") || value.includes("PREVIEW")) return "green";
  if (value.includes("BLOCKED") || value.includes("ERR")) return "crimson";
  return "gray";
}

export default function AdvanceInvigilationBatchPreview() {
  const { t } = useI18n();
  const [periodId, setPeriodId] = useState("");
  const [academicYear, setAcademicYear] = useState("2568");
  const [semester, setSemester] = useState("2");
  const [examType, setExamType] = useState("final");

  const query = {
    period_id: periodId ? Number(periodId) : null,
    academic_year: academicYear || null,
    semester: semester || null,
    exam_type: examType || null,
  };
  const { data, isError, isLoading } = useAdvanceBatchPreview(query);

  const summaryCards = useMemo(() => {
    if (!data) return [];
    return [
      {
        label: t("advanceBatch.summary.previewTotal"),
        value: formatCurrency(data.summary.preview_total_amount),
        hint: t("advanceBatch.summary.previewTotalHint"),
      },
      {
        label: t("advanceBatch.summary.weekday"),
        value: data.summary.preview_weekday_count,
        hint: t("advanceBatch.summary.calculatedRows"),
      },
      {
        label: t("advanceBatch.summary.weekend"),
        value: data.summary.preview_weekend_count,
        hint: t("advanceBatch.summary.calculatedRows"),
      },
      {
        label: t("advanceBatch.summary.pendingBlocked"),
        value: data.summary.pending_rate_rule_count
          + data.summary.missing_exam_date_count
          + data.summary.invalid_exam_date_count
          + data.summary.blocked_roster_amount_count,
        hint: t("advanceBatch.summary.pendingBlockedHint"),
      },
    ];
  }, [data, t]);

  const rosterColumns = useMemo<Array<DataTableColumn<AdvanceBatchRosterRow>>>(() => [
    {
      key: "person",
      label: t("advanceBatch.table.person"),
      minWidth: "220px",
      render: (row) => (
        <div className="data-table__content">
          <strong>{row.person_name || t("advanceBatch.table.unknownPerson")}</strong>
          <p>{row.department || row.person_type || "-"}</p>
        </div>
      ),
    },
    {
      key: "role",
      label: t("advanceBatch.table.role"),
      width: "150px",
      render: (row) => row.duty_role,
    },
    {
      key: "exam",
      label: t("advanceBatch.table.exam"),
      minWidth: "220px",
      render: (row) => (
        <div className="data-table__content">
          <strong>{`${row.course_code || "-"} ${row.section ? `(${row.section})` : ""}`.trim()}</strong>
          <p>{`${row.exam_date || "-"} ${row.start_time || ""}${row.start_time || row.end_time ? "-" : ""}${row.end_time || ""}`.trim()}</p>
        </div>
      ),
    },
    {
      key: "room",
      label: t("advanceBatch.table.room"),
      width: "140px",
      render: (row) => row.room_name || "-",
    },
    {
      key: "inclusion",
      label: t("advanceBatch.table.inclusion"),
      width: "180px",
      render: (row) => (
        <Badge variant={inclusionVariant(row.advance_inclusion_status)} size="sm">
          {row.advance_inclusion_status}
        </Badge>
      ),
    },
    {
      key: "amount",
      label: t("advanceBatch.table.amount"),
      minWidth: "180px",
      render: (row) => (
        <div className="data-table__content">
          <Badge variant={amountVariant(row.amount_status)} size="sm">
            {row.amount_status}
          </Badge>
          <p>{row.amount_preview === null ? t("advanceBatch.table.noPreviewAmount") : formatCurrency(row.amount_preview)}</p>
          <p>{t(`advanceBatch.dayType.${row.rate_day_type}`)}</p>
        </div>
      ),
    },
    {
      key: "reconciliation",
      label: t("advanceBatch.table.reconciliation"),
      width: "160px",
      render: (row) => row.reconciliation_status,
    },
    {
      key: "warning",
      label: t("advanceBatch.table.warning"),
      minWidth: "220px",
      render: (row) => row.warnings.join("; ") || row.blocked_reason || "-",
    },
  ], [t]);

  if (isLoading) {
    return (
      <div className="page-stack page-stack--spacious">
        <div className="stitch-metric-grid">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="dashboard-skeleton" />
          ))}
        </div>
        <Skeleton className="dashboard-chart-skeleton" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="page-stack page-stack--spacious">
        <EmptyState icon={<Icon name="warning" />} title={t("advanceBatch.empty.errorTitle")} />
      </div>
    );
  }

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        className="page-hero--dashboard"
        eyebrow={t("advanceBatch.eyebrow")}
        title={t("advanceBatch.title")}
        description={t("advanceBatch.description")}
        status={<Badge variant="gold">{t("advanceBatch.eyebrow")}</Badge>}
      />

      <AlertBanner
        variant="warning"
        title={t("advanceBatch.warning.title")}
        action={<Badge variant="gold">PREVIEW_ONLY</Badge>}
      >
        {t("advanceBatch.warning.body")}
      </AlertBanner>

      <Card title={t("advanceBatch.eyebrow")} subtitle={t("advanceBatch.description")}>
        <div className="form-grid">
          <FormField label={t("advanceBatch.filters.period")}>
            <input
              value={periodId}
              onChange={(event) => setPeriodId(event.target.value)}
              placeholder={t("advanceBatch.filters.periodPlaceholder")}
            />
          </FormField>
          <FormField label={t("advanceBatch.filters.academicYear")}>
            <input value={academicYear} onChange={(event) => setAcademicYear(event.target.value)} />
          </FormField>
          <FormField label={t("advanceBatch.filters.semester")}>
            <input value={semester} onChange={(event) => setSemester(event.target.value)} />
          </FormField>
          <FormField label={t("advanceBatch.filters.examType")}>
            <input value={examType} onChange={(event) => setExamType(event.target.value)} />
          </FormField>
        </div>
        <div className="mt-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setPeriodId("");
              setAcademicYear("2568");
              setSemester("2");
              setExamType("final");
            }}
          >
            {t("common.reset")}
          </Button>
        </div>
      </Card>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        {summaryCards.map((card) => (
          <SummaryCard key={card.label} {...card} />
        ))}
      </section>

      {data.roster_rows.length === 0 ? (
        <Card>
          <EmptyState
            icon={<Icon name="info" />}
            title={t("advanceBatch.empty.noRowsTitle")}
            description={t("advanceBatch.empty.noRowsDescription")}
          />
        </Card>
      ) : (
        <Card title={t("advanceBatch.roster.title")} subtitle={t("advanceBatch.roster.subtitle")}>
          <DataTable
            columns={rosterColumns}
            rows={data.roster_rows}
            rowKey={(row) => row.source_record_ref}
            compact
            tableLayout="fixed"
          />
        </Card>
      )}

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <Card title={t("advanceBatch.blockers.title")} subtitle={t("advanceBatch.blockers.subtitle")}>
          <ul className="ui-list">
            {(data.blockers.length ? data.blockers : [t("advanceBatch.blockers.none")]).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </Card>
        <Card title={t("advanceBatch.warnings.title")} subtitle={t("advanceBatch.warnings.subtitle")}>
          <ul className="ui-list">
            {(data.warnings.length ? data.warnings : [t("advanceBatch.warnings.none")]).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </Card>
        <Card title={t("advanceBatch.ruleGaps.title")} subtitle={t("advanceBatch.ruleGaps.subtitle")}>
          <ul className="ui-list">
            {data.rule_gaps.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </Card>
      </section>
    </div>
  );
}
