import { useMemo, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, type DataTableColumn } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
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
      key: "slot",
      label: t("paymentDraft.table.slot"),
      minWidth: "190px",
      render: (row) => (
        <div className="data-table__content">
          <strong>{row.exam_date}</strong>
          <p>{row.time_slot}</p>
        </div>
      ),
    },
    {
      key: "dayType",
      label: t("paymentDraft.table.dayType"),
      width: "140px",
      render: (row) => <Badge variant={row.day_type === "WEEKEND" ? "gold" : "gray"}>{t(`advanceBatch.dayType.${row.day_type}`)}</Badge>,
    },
    {
      key: "rate",
      label: t("paymentDraft.table.rate"),
      width: "130px",
      render: (row) => formatCurrency(row.rate_amount),
    },
    {
      key: "invigilation",
      label: t("paymentDraft.table.invigilation"),
      minWidth: "190px",
      render: (row) => (
        <div className="data-table__content">
          <strong>{row.invigilation_committee_count}</strong>
          <p>{formatCurrency(row.invigilation_compensation_amount)}</p>
        </div>
      ),
    },
    {
      key: "paper",
      label: t("paymentDraft.table.paper"),
      minWidth: "190px",
      render: (row) => (
        <div className="data-table__content">
          <strong>{row.paper_distribution_committee_count}</strong>
          <p>{formatCurrency(row.paper_distribution_compensation_amount)}</p>
        </div>
      ),
    },
    {
      key: "total",
      label: t("paymentDraft.table.total"),
      width: "150px",
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
      <section className="page-hero page-hero--dashboard">
        <div>
          <span className="page-hero__eyebrow">{t("paymentDraft.eyebrow")}</span>
          <h2 className="page-hero__title">{t("paymentDraft.title")}</h2>
          <p className="page-hero__description">{t("paymentDraft.description")}</p>
        </div>
      </section>

      <Card
        title={t("paymentDraft.warning.title")}
        subtitle={t("paymentDraft.warning.body")}
        actions={<Badge variant="gold">DRAFT_NOT_AUTHORIZED</Badge>}
      />

      <Card title={t("paymentDraft.filters.title")} subtitle={t("paymentDraft.filters.subtitle")}>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("advanceBatch.filters.period")}</span>
            <input className="w-full rounded border px-3 py-2" value={periodId} onChange={(event) => setPeriodId(event.target.value)} placeholder={t("advanceBatch.filters.periodPlaceholder")} />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("advanceBatch.filters.academicYear")}</span>
            <input className="w-full rounded border px-3 py-2" value={academicYear} onChange={(event) => setAcademicYear(event.target.value)} />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("advanceBatch.filters.semester")}</span>
            <input className="w-full rounded border px-3 py-2" value={semester} onChange={(event) => setSemester(event.target.value)} />
          </label>
          <label className="space-y-1 text-sm">
            <span className="block text-gray-500">{t("advanceBatch.filters.examType")}</span>
            <input className="w-full rounded border px-3 py-2" value={examType} onChange={(event) => setExamType(event.target.value)} />
          </label>
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
        <div className="space-y-3">
          {paperRows.map((row) => (
            <div key={row.local_id} className="grid grid-cols-1 gap-3 md:grid-cols-[1fr_1fr_120px_1fr_auto]">
              <input className="rounded border px-3 py-2" value={row.exam_date} onChange={(event) => updatePaperRow(row.local_id, { exam_date: event.target.value })} placeholder={t("paymentDraft.paper.examDate")} />
              <input className="rounded border px-3 py-2" value={row.exam_time || ""} onChange={(event) => updatePaperRow(row.local_id, { exam_time: event.target.value })} placeholder={t("paymentDraft.paper.examTime")} />
              <input className="rounded border px-3 py-2" min={0} type="number" value={row.committee_count} onChange={(event) => updatePaperRow(row.local_id, { committee_count: Number(event.target.value) })} />
              <input className="rounded border px-3 py-2" value={row.notes || ""} onChange={(event) => updatePaperRow(row.local_id, { notes: event.target.value })} placeholder={t("paymentDraft.paper.notes")} />
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
              <div className="text-3xl font-bold">{formatCurrency(data.totals.invigilation_compensation_amount)}</div>
            </Card>
            <Card title={t("paymentDraft.summary.paper")} subtitle={String(data.totals.paper_distribution_committee_count)}>
              <div className="text-3xl font-bold">{formatCurrency(data.totals.paper_distribution_compensation_amount)}</div>
            </Card>
            <Card title={t("paymentDraft.summary.grandTotal")} subtitle={t("paymentDraft.summary.notAuthorized")}>
              <div className="text-3xl font-bold">{formatCurrency(data.totals.grand_total_amount)}</div>
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
            <ul className="space-y-2 text-sm text-gray-600">
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
