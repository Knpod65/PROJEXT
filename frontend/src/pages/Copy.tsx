import { useCallback } from "react";

import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { PageHeader } from "@/components/ui/PageHeader";
import { useAsyncData } from "@/hooks/useAsyncData";
import { useI18n } from "@/i18n";
import { getCopyCount } from "@/services/schedule.service";
import type { CopyCountSummary } from "@/types/api";
import { formatCurrency, formatNumber } from "@/utils/format";

type CopyRow = CopyCountSummary["rows"][number];

function formatStapleLabel(t: ReturnType<typeof useI18n>["t"], row: CopyRow) {
  switch (row.print_staple) {
    case "corner_left":
      return t("copy.print.stapleCorner");
    case "side_left":
      return t("copy.print.stapleSide");
    case "custom":
      return row.print_staple_page
        ? t("copy.print.splitAtPage", { page: row.print_staple_page })
        : t("copy.print.customStaple");
    default:
      return t("copy.print.noStaple");
  }
}

function formatAnswerFormats(t: ReturnType<typeof useI18n>["t"], row: CopyRow) {
  if (!row.answer_formats || row.answer_formats.length === 0) {
    return t("copy.print.notSpecified");
  }
  return row.answer_formats.join(", ");
}

export function CopyPage() {
  const { t } = useI18n();
  const loader = useCallback(() => getCopyCount(), []);
  const { data, loading } = useAsyncData(loader, [loader]);

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow={t("navigation.groups.operations")}
        title={t("navigation.pages.copy.title")}
        description={t("navigation.pages.copy.description")}
      />
      <Card title={t("copy.title")} subtitle={t("copy.subtitle")}>
        <div className="summary-grid">
          <div className="summary-box">
            <span>{t("copy.stats.examSheetsTotal")}</span>
            <strong>{formatNumber(data?.grand_total ?? 0)}</strong>
          </div>
          <div className="summary-box">
            <span>{t("copy.stats.totalCopyCost")}</span>
            <strong>{formatCurrency(data?.cost ?? 0)}</strong>
          </div>
          <div className="summary-box">
            <span>{t("copy.stats.fraudFormsReserve")}</span>
            <strong>{formatNumber(data?.fraud_forms ?? 0)}</strong>
          </div>
          <div className="summary-box">
            <span>{t("copy.stats.sections")}</span>
            <strong>{formatNumber(data?.sections_count ?? 0)}</strong>
          </div>
        </div>
      </Card>

      <DataTable<CopyRow>
        columns={[
          {
            key: "course_id",
            label: t("common.course"),
            width: "18%",
            render: (row) => (
              <div className="data-table__content data-table__content--clamp">
                <strong>{row.course_id}</strong>
                <p>{row.course_name_th}</p>
                <p>{t("copy.table.sectionLabel", { section: row.section_no })}</p>
              </div>
            ),
          },
          {
            key: "exam_date",
            label: t("copy.table.examSlot"),
            width: "16%",
            render: (row) => (
              <div className="data-table__content data-table__content--clamp">
                <strong>{row.exam_date || "-"}</strong>
                <p>{row.exam_time || t("copy.table.timePending")}</p>
                <p>{row.room || t("copy.table.roomPending")}</p>
              </div>
            ),
          },
          {
            key: "num_students",
            label: t("copy.table.volume"),
            width: "12%",
            render: (row) => (
              <div className="data-table__content data-table__content--clamp">
                <strong>{t("copy.table.sheetCount", { count: formatNumber(row.total_sheets) })}</strong>
                <p>{t("copy.table.studentCount", { count: formatNumber(row.num_students) })}</p>
                <p>{t("copy.table.pageCount", { count: formatNumber(row.num_pages) })}</p>
              </div>
            ),
          },
          {
            key: "print_duplex",
            label: t("copy.table.printSetup"),
            width: "22%",
            render: (row) => {
              const lines = [
                row.print_duplex ? t("copy.print.doubleSided") : t("copy.print.singleSided"),
                formatStapleLabel(t, row),
                row.a4_pages_count > 0 ? t("copy.print.extraA4Pages", { count: formatNumber(row.a4_pages_count) }) : null,
                t("copy.print.answerFormat", { value: formatAnswerFormats(t, row) }),
              ].filter(Boolean);

              return (
                <div className="data-table__content data-table__content--clamp">
                  {lines.map((line) => (
                    <p key={line}>{line}</p>
                  ))}
                </div>
              );
            },
          },
          {
            key: "answer_paper_sheets",
            label: t("copy.table.answerMaterials"),
            width: "18%",
            render: (row) => {
              const lines = [
                row.answer_paper_sheets > 0 ? t("copy.materials.answerSheetsPerStudent", { count: row.answer_paper_sheets }) : null,
                row.answer_paper_staple ? t("copy.materials.answerSheetsStapled") : null,
                row.answer_booklet_count > 0 ? t("copy.materials.bookletsPerStudent", { count: row.answer_booklet_count }) : null,
                row.omr_sheet_count > 0 ? t("copy.materials.omrSheetsPerStudent", { count: row.omr_sheet_count }) : null,
                row.scratch_paper_sheets > 0 ? t("copy.materials.scratchSheetsPerStudent", { count: row.scratch_paper_sheets }) : null,
              ].filter(Boolean);

              return lines.length > 0 ? (
                <div className="data-table__content data-table__content--clamp">
                  {lines.map((line) => (
                    <p key={line}>{line}</p>
                  ))}
                </div>
              ) : (
                <span className="text-muted">{t("copy.materials.none")}</span>
              );
            },
          },
          {
            key: "print_note",
            label: t("common.notes"),
            width: "14%",
            render: (row) => (
              <div className="data-table__content data-table__content--clamp">
                <p>{row.print_note || t("copy.notes.noPrintNote")}</p>
                <p>{row.special_note || t("copy.notes.noMaterialNote")}</p>
              </div>
            ),
          },
        ]}
        emptyTitle={t("copy.emptyTitle")}
        emptyDescription={t("copy.emptyDescription")}
        loading={loading}
        rowKey={(row) => `${row.course_id}-${row.section_no}-${row.exam_date ?? "na"}-${row.exam_time ?? "na"}`}
        rows={data?.rows ?? []}
        scrollThreshold={5}
        tableLayout="fixed"
      />
    </div>
  );
}
