import { useMemo, useState } from "react";

import { AlertBanner } from "@/components/ui/AlertBanner";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, type DataTableColumn } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { FormField } from "@/components/ui/FormField";
import { Icon } from "@/components/ui/Icon";
import { PageHeader } from "@/components/ui/PageHeader";
import { useOfficialPaymentDraftPreview } from "@/hooks/domain/useOfficialPaymentDraftPreview";
import { useI18n } from "@/i18n";
import type { OfficialPaymentDraftManualPaperRow, OfficialPaymentDraftRow } from "@/types/officialPaymentDraft";
import { formatCurrency } from "@/utils/format";

type EditablePaperRow = OfficialPaymentDraftManualPaperRow & { local_id: string };

function newPaperRow(): EditablePaperRow {
  return {
    local_id: crypto.randomUUID(),
    exam_date: "",
    exam_time: "",
    committee_count: 0,
    notes: "",
  };
}

function toRequestRow(row: EditablePaperRow): OfficialPaymentDraftManualPaperRow | null {
  if (!row.exam_date.trim()) return null;
  return {
    exam_date: row.exam_date.trim(),
    exam_time: row.exam_time?.trim() || null,
    start_time: row.start_time?.trim() || null,
    end_time: row.end_time?.trim() || null,
    committee_count: Number(row.committee_count) || 0,
    notes: row.notes?.trim() || null,
  };
}

export default function OfficialPaymentDocumentDraft() {
  const { t } = useI18n();
  const [periodId, setPeriodId] = useState("");
  const [academicYear, setAcademicYear] = useState("2568");
  const [semester, setSemester] = useState("2");
  const [examType, setExamType] = useState("final");
  const [paperRows, setPaperRows] = useState<EditablePaperRow[]>([newPaperRow()]);
  const { data, isError, isLoading, preview } = useOfficialPaymentDraftPreview();

  const draftColumns = useMemo<Array<DataTableColumn<OfficialPaymentDraftRow>>>(() => [
    {
      key: "examDate",
      label: t("paymentDraft.table.examDate"),
      minWidth: "150px",
      render: (row) => <strong>{row.exam_date}</strong>,
    },
    {
      key: "timeSlot",
      label: t("paymentDraft.table.timeSlot"),
      minWidth: "150px",
      render: (row) => row.time_slot,
    },
    {
      key: "dayType",
      label: t("paymentDraft.table.dayType"),
      width: "140px",
      render: (row) => <Badge variant={row.day_type === "WEEKEND" ? "gold" : "gray"}>{t(`advanceBatch.dayType.${row.day_type}`)}</Badge>,
    },
    {
      key: "invigilationCount",
      label: t("paymentDraft.table.invigilationCount"),
      width: "140px",
      align: "center",
      render: (row) => row.invigilation_committee_count,
    },
    {
      key: "invigilationAmount",
      label: t("paymentDraft.table.invigilationAmount"),
      width: "160px",
      align: "right",
      render: (row) => formatCurrency(row.invigilation_compensation_amount),
    },
    {
      key: "paperCount",
      label: t("paymentDraft.table.paperCount"),
      width: "150px",
      align: "center",
      render: (row) => row.paper_distribution_committee_count,
    },
    {
      key: "paperAmount",
      label: t("paymentDraft.table.paperAmount"),
      width: "170px",
      align: "right",
      render: (row) => formatCurrency(row.paper_distribution_compensation_amount),
    },
    {
      key: "total",
      label: t("paymentDraft.table.total"),
      width: "150px",
      align: "right",
      render: (row) => <strong>{formatCurrency(row.total_compensation_amount)}</strong>,
    },
    {
      key: "warnings",
      label: t("paymentDraft.table.warnings"),
      minWidth: "240px",
      render: (row) => row.warnings.join("; ") || "-",
    },
  ], [t]);

  const updatePaperRow = (localId: string, patch: Partial<EditablePaperRow>) => {
    setPaperRows((rows) => rows.map((row) => (row.local_id === localId ? { ...row, ...patch } : row)));
  };

  const submitPreview = async () => {
    const manualRows = paperRows.map(toRequestRow).filter((row): row is OfficialPaymentDraftManualPaperRow => Boolean(row));
    await preview({
      period_id: periodId ? Number(periodId) : null,
      academic_year: academicYear || null,
      semester: semester || null,
      exam_type: examType || null,
      paper_distribution_rows: manualRows,
    });
  };

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        className="page-hero--dashboard"
        eyebrow={t("paymentDraft.eyebrow")}
        title={t("paymentDraft.title")}
        description={t("paymentDraft.description")}
        status={<Badge variant="gold">DRAFT_NOT_AUTHORIZED</Badge>}
      />

      <AlertBanner
        variant="warning"
        title={t("paymentDraft.warning.title")}
        action={<Badge variant="gold">DRAFT_NOT_AUTHORIZED</Badge>}
      >
        {t("paymentDraft.warning.body")}
      </AlertBanner>

      <Card title={t("paymentDraft.filters.title")} subtitle={t("paymentDraft.filters.subtitle")}>
        <div className="form-grid">
          <FormField label={t("advanceBatch.filters.period")}>
            <input value={periodId} onChange={(event) => setPeriodId(event.target.value)} placeholder={t("advanceBatch.filters.periodPlaceholder")} />
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
      </Card>

      <Card
        title={t("paymentDraft.paper.title")}
        subtitle={t("paymentDraft.paper.subtitle")}
        actions={
          <Button type="button" variant="outline" iconLeft={<Icon name="add" />} onClick={() => setPaperRows((rows) => [...rows, newPaperRow()])}>
            {t("paymentDraft.paper.add")}
          </Button>
        }
      >
        <div className="page-stack">
          {paperRows.map((row) => (
            <div key={row.local_id} className="form-grid form-grid--paper">
              <FormField label={t("paymentDraft.table.examDate")}>
                <input value={row.exam_date} onChange={(event) => updatePaperRow(row.local_id, { exam_date: event.target.value })} placeholder={t("paymentDraft.paper.examDate")} />
              </FormField>
              <FormField label={t("paymentDraft.table.timeSlot")}>
                <input value={row.exam_time || ""} onChange={(event) => updatePaperRow(row.local_id, { exam_time: event.target.value })} placeholder={t("paymentDraft.paper.examTime")} />
              </FormField>
              <FormField label={t("paymentDraft.paper.count")}>
                <input min={0} type="number" value={row.committee_count} onChange={(event) => updatePaperRow(row.local_id, { committee_count: Number(event.target.value) })} />
              </FormField>
              <FormField label={t("paymentDraft.paper.notes")}>
                <input value={row.notes || ""} onChange={(event) => updatePaperRow(row.local_id, { notes: event.target.value })} placeholder={t("paymentDraft.paper.notes")} />
              </FormField>
              <Button type="button" variant="ghost" iconLeft={<Icon name="delete" />} onClick={() => setPaperRows((rows) => rows.filter((item) => item.local_id !== row.local_id))}>
                {t("common.delete")}
              </Button>
            </div>
          ))}
        </div>
        <div className="mt-4 flex flex-wrap gap-3">
          <Button type="button" iconLeft={<Icon name="calculate" />} loading={isLoading} onClick={submitPreview}>
            {t("paymentDraft.actions.preview")}
          </Button>
          <Button type="button" variant="outline" onClick={() => setPaperRows([newPaperRow()])}>
            {t("common.reset")}
          </Button>
        </div>
      </Card>

      {isError ? (
        <Card>
          <EmptyState icon={<Icon name="warning" />} title={t("paymentDraft.empty.errorTitle")} />
        </Card>
      ) : null}

      {data ? (
        <>
          <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            <Card title={t("paymentDraft.summary.invigilation")} subtitle={String(data.totals.invigilation_committee_count)}>
              <p className="metric-value">{formatCurrency(data.totals.invigilation_compensation_amount)}</p>
            </Card>
            <Card title={t("paymentDraft.summary.paper")} subtitle={String(data.totals.paper_distribution_committee_count)}>
              <p className="metric-value">{formatCurrency(data.totals.paper_distribution_compensation_amount)}</p>
            </Card>
            <Card title={t("paymentDraft.summary.grandTotal")} subtitle={t("paymentDraft.summary.notAuthorized")}>
              <p className="metric-value">{formatCurrency(data.totals.grand_total_amount)}</p>
            </Card>
            <Card title={t("paymentDraft.summary.review")} subtitle={data.metadata.term_label}>
              <Badge variant="gold">DRAFT_NOT_AUTHORIZED</Badge>
            </Card>
          </section>

          {data.rows.length === 0 ? (
            <Card>
              <EmptyState icon={<Icon name="info" />} title={t("paymentDraft.empty.noRowsTitle")} description={t("paymentDraft.empty.noRowsDescription")} />
            </Card>
          ) : (
            <Card title={t("paymentDraft.table.title")} subtitle={t("paymentDraft.table.subtitle")}>
              <DataTable columns={draftColumns} rows={data.rows} rowKey={(row) => `${row.normalized_exam_date || row.exam_date}:${row.time_slot}`} compact tableLayout="fixed" />
            </Card>
          )}

          <Card title={t("paymentDraft.warnings.title")} subtitle={t("paymentDraft.warnings.subtitle")}>
            <ul className="ui-list">
              {(data.warnings.length ? data.warnings : [t("paymentDraft.warnings.none")]).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </Card>
        </>
      ) : (
        <Card>
          <EmptyState icon={<Icon name="info" />} title={t("paymentDraft.empty.initialTitle")} description={t("paymentDraft.empty.initialDescription")} />
        </Card>
      )}
    </div>
  );
}
