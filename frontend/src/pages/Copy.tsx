import { useCallback } from "react";

import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { useAsyncData } from "@/hooks/useAsyncData";
import { getCopyCount } from "@/services/schedule.service";
import type { CopyCountSummary } from "@/types/api";
import { formatCurrency, formatNumber } from "@/utils/format";

type CopyRow = CopyCountSummary["rows"][number];

function formatStapleLabel(row: CopyRow) {
  switch (row.print_staple) {
    case "corner_left":
      return "Staple corner";
    case "side_left":
      return "Staple side";
    case "custom":
      return row.print_staple_page ? `Split at page ${row.print_staple_page}` : "Custom staple";
    default:
      return "No staple";
  }
}

function formatAnswerFormats(row: CopyRow) {
  if (!row.answer_formats || row.answer_formats.length === 0) {
    return "Not specified";
  }
  return row.answer_formats.join(", ");
}

function renderPrintInstructions(row: CopyRow) {
  const lines = [
    row.print_duplex ? "Double-sided" : "Single-sided",
    formatStapleLabel(row),
    row.a4_pages_count > 0 ? `Extra A4 pages: ${formatNumber(row.a4_pages_count)}` : null,
    `Answer format: ${formatAnswerFormats(row)}`,
  ].filter(Boolean);

  return (
    <div className="data-table__content data-table__content--clamp">
      {lines.map((line) => (
        <p key={line}>{line}</p>
      ))}
    </div>
  );
}

function renderMaterials(row: CopyRow) {
  const lines = [
    row.answer_paper_sheets > 0 ? `Answer sheets/student: ${row.answer_paper_sheets}` : null,
    row.answer_paper_staple ? "Answer sheets stapled" : null,
    row.answer_booklet_count > 0 ? `Booklets/student: ${row.answer_booklet_count}` : null,
    row.omr_sheet_count > 0 ? `OMR sheets/student: ${row.omr_sheet_count}` : null,
    row.scratch_paper_sheets > 0 ? `Scratch sheets/student: ${row.scratch_paper_sheets}` : null,
  ].filter(Boolean);

  return lines.length > 0 ? (
    <div className="data-table__content data-table__content--clamp">
      {lines.map((line) => (
        <p key={line}>{line}</p>
      ))}
    </div>
  ) : (
    <span className="text-muted">No extra materials</span>
  );
}

export function CopyPage() {
  const loader = useCallback(() => getCopyCount(), []);
  const { data, loading } = useAsyncData(loader, [loader]);

  return (
    <div className="page-stack">
      <Card title="Copy Count" subtitle="Print volume and teacher-provided print instructions for the active exam set">
        <div className="summary-grid">
          <div className="summary-box">
            <span>Exam sheets total</span>
            <strong>{formatNumber(data?.grand_total ?? 0)}</strong>
          </div>
          <div className="summary-box">
            <span>Total copy cost</span>
            <strong>{formatCurrency(data?.cost ?? 0)}</strong>
          </div>
          <div className="summary-box">
            <span>Fraud forms reserve</span>
            <strong>{formatNumber(data?.fraud_forms ?? 0)}</strong>
          </div>
          <div className="summary-box">
            <span>Sections</span>
            <strong>{formatNumber(data?.sections_count ?? 0)}</strong>
          </div>
        </div>
      </Card>

      <DataTable<CopyRow>
        columns={[
          {
            key: "course_id",
            label: "Course",
            width: "18%",
            render: (row) => (
              <div className="data-table__content data-table__content--clamp">
                <strong>{row.course_id}</strong>
                <p>{row.course_name_th}</p>
                <p>Section {row.section_no}</p>
              </div>
            ),
          },
          {
            key: "exam_date",
            label: "Exam Slot",
            width: "16%",
            render: (row) => (
              <div className="data-table__content data-table__content--clamp">
                <strong>{row.exam_date || "-"}</strong>
                <p>{row.exam_time || "Time not assigned"}</p>
                <p>{row.room || "Exam room not assigned yet"}</p>
              </div>
            ),
          },
          {
            key: "num_students",
            label: "Volume",
            width: "12%",
            render: (row) => (
              <div className="data-table__content data-table__content--clamp">
                <strong>{formatNumber(row.total_sheets)} sheets</strong>
                <p>{formatNumber(row.num_students)} students</p>
                <p>{formatNumber(row.num_pages)} pages</p>
              </div>
            ),
          },
          {
            key: "print_duplex",
            label: "Print Setup",
            width: "22%",
            render: renderPrintInstructions,
          },
          {
            key: "answer_paper_sheets",
            label: "Answer Materials",
            width: "18%",
            render: renderMaterials,
          },
          {
            key: "print_note",
            label: "Notes",
            width: "14%",
            render: (row) => (
              <div className="data-table__content data-table__content--clamp">
                <p>{row.print_note || "No print note"}</p>
                <p>{row.special_note || "No material note"}</p>
              </div>
            ),
          },
        ]}
        emptyTitle="No copy-count data yet"
        emptyDescription="Copy-count details will appear after schedules and teacher submissions are available."
        loading={loading}
        rowKey={(row) => `${row.course_id}-${row.section_no}-${row.exam_date ?? "na"}-${row.exam_time ?? "na"}`}
        rows={data?.rows ?? []}
        scrollThreshold={5}
        tableLayout="fixed"
      />
    </div>
  );
}
