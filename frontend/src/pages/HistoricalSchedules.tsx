import { useCallback, useEffect, useMemo, useState } from "react";

import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { useAsyncData } from "@/hooks/useAsyncData";
import {
  buildHistoricalComparisonCsvUrl,
  buildHistoricalWorkloadCsvUrl,
  getHistoricalComparison,
  getHistoricalDistributionRows,
  getHistoricalScheduleOverview,
  getHistoricalScheduleRows,
  getHistoricalWorkload,
  type HistoricalComparisonRow,
  type HistoricalDistributionRow,
  type HistoricalScheduleRow,
  type HistoricalScheduleVersion,
  type HistoricalWorkloadAssignmentRow,
  type HistoricalWorkloadSummaryRow,
  updateHistoricalRoomOpeningStart,
} from "@/services/historicalSchedule.service";
import { useUi } from "@/store/ui.store";
import { Button } from "@/components/ui/Button";
import { formatDate, formatNumber } from "@/utils/format";

function openExport(url: string) {
  window.open(url, "_blank", "noopener,noreferrer");
}

function renderBatchMeta(batch: {
  source_filename: string;
  row_count: number;
  manual_review_count: number;
  imported_at: string | null;
} | null) {
  if (!batch) {
    return <span>-</span>;
  }
  return (
    <div className="data-table__content data-table__content--clamp">
      <strong>{batch.source_filename}</strong>
      <p>
        {formatNumber(batch.row_count)} rows · {formatNumber(batch.manual_review_count)} review flags
      </p>
      <p>{batch.imported_at ? new Date(batch.imported_at).toLocaleString() : "-"}</p>
    </div>
  );
}

export function HistoricalSchedulesPage() {
  const { toast } = useUi();
  const [versionKind, setVersionKind] = useState<HistoricalScheduleVersion>("final_adjusted");
  const [roomOpeningStart, setRoomOpeningStart] = useState("");

  const overviewLoader = useCallback(() => getHistoricalScheduleOverview(), []);
  const rowsLoader = useCallback(() => getHistoricalScheduleRows(versionKind), [versionKind]);
  const distributionLoader = useCallback(() => getHistoricalDistributionRows(versionKind), [versionKind]);
  const workloadLoader = useCallback(() => getHistoricalWorkload(versionKind), [versionKind]);
  const comparisonLoader = useCallback(() => getHistoricalComparison(), []);

  const overviewState = useAsyncData(overviewLoader, [overviewLoader]);
  const rowsState = useAsyncData(rowsLoader, [rowsLoader]);
  const distributionState = useAsyncData(distributionLoader, [distributionLoader]);
  const workloadState = useAsyncData(workloadLoader, [workloadLoader]);
  const comparisonState = useAsyncData(comparisonLoader, [comparisonLoader]);

  useEffect(() => {
    if (overviewState.data?.room_opening_start_username) {
      setRoomOpeningStart(overviewState.data.room_opening_start_username);
    }
  }, [overviewState.data?.room_opening_start_username]);

  const reviewCount = useMemo(
    () => (rowsState.data?.rows ?? []).filter((row) => row.parse_flags.length > 0).length,
    [rowsState.data?.rows],
  );

  async function handleSaveRoomOpeningStart() {
    try {
      await updateHistoricalRoomOpeningStart(roomOpeningStart);
      toast("บันทึกผู้เริ่มเวียนเปิดห้องแล้ว", "success");
      await overviewState.reload();
    } catch (error) {
      toast(error instanceof Error ? error.message : "บันทึกค่าเริ่มต้นไม่สำเร็จ", "error");
    }
  }

  if (overviewState.loading) {
    return (
      <div className="page-stack">
        <div className="dashboard-skeleton" />
      </div>
    );
  }

  if (overviewState.error || !overviewState.data) {
    return (
      <EmptyState
        icon={<Icon name="history" />}
        title="Historical schedule snapshots unavailable"
        description={overviewState.error ?? "No imported historical schedule snapshots are available yet."}
      />
    );
  }

  return (
    <div className="page-stack">
      <Card title="Historical Final Schedule 2/2568" subtitle="Compare optimized baseline vs final adjusted PDF imports without overwriting the live EMS exam schedule.">
        <div className="summary-grid">
          <div className="summary-box">
            <span>Final adjusted</span>
            <strong>{formatNumber(overviewState.data.final_adjusted_batch?.row_count ?? 0)}</strong>
          </div>
          <div className="summary-box">
            <span>Optimized baseline</span>
            <strong>{formatNumber(overviewState.data.optimized_baseline_batch?.row_count ?? 0)}</strong>
          </div>
          <div className="summary-box">
            <span>Differences detected</span>
            <strong>{formatNumber(overviewState.data.comparison_count)}</strong>
          </div>
          <div className="summary-box">
            <span>Selected review flags</span>
            <strong>{formatNumber(reviewCount)}</strong>
          </div>
        </div>
      </Card>

      <Card
        title="Snapshot Sources"
        subtitle="These two PDF imports are stored separately as optimized_original_result and final_adjusted_result."
        actions={(
          <div className="inline-actions">
            <Button size="sm" variant="outline" type="button" onClick={() => openExport(buildHistoricalComparisonCsvUrl())}>
              Export comparison CSV
            </Button>
            <Button size="sm" variant="outline" type="button" onClick={() => openExport(buildHistoricalWorkloadCsvUrl(versionKind))}>
              Export workload CSV
            </Button>
          </div>
        )}
      >
        <DataTable
          columns={[
            { key: "label", label: "Version", width: "18%" },
            {
              key: "batch",
              label: "Imported source",
              width: "42%",
              render: (row: { batch: typeof overviewState.data.final_adjusted_batch | null }) => renderBatchMeta(row.batch),
            },
            {
              key: "notes",
              label: "Stored meaning",
              width: "40%",
            },
          ]}
          rowKey={(row: { label: string }) => row.label}
          rows={[
            {
              label: "final_adjusted",
              batch: overviewState.data.final_adjusted_batch,
              notes: "Confirmed historical final schedule with corrected room, invigilator, and paper-distribution assignments.",
            },
            {
              label: "optimized_baseline",
              batch: overviewState.data.optimized_baseline_batch,
              notes: "Original optimization/workload baseline before later manual schedule adjustments.",
            },
          ]}
          tableLayout="fixed"
        />
      </Card>

      <Card
        title="Room-Opening Rotation"
        subtitle="Used as fallback only when imported room-opening staff is missing. Imported explicit assignments remain the source of truth."
      >
        <div className="filter-row">
          <label className="field">
            <span className="field__label">Starting person</span>
            <select className="input" value={roomOpeningStart} onChange={(event) => setRoomOpeningStart(event.target.value)}>
              {overviewState.data.room_opening_candidates.map((candidate) => (
                <option key={candidate.username} value={candidate.username}>
                  {candidate.full_name}
                </option>
              ))}
            </select>
          </label>
          <Button type="button" onClick={handleSaveRoomOpeningStart}>
            Save rotation start
          </Button>
        </div>
      </Card>

      <Card title="Schedule Snapshot" subtitle="Toggle between final adjusted and optimized baseline to review parsed rows, invigilators, and distribution assignments.">
        <div className="filter-row">
          <label className="field">
            <span className="field__label">Snapshot version</span>
            <select className="input" value={versionKind} onChange={(event) => setVersionKind(event.target.value as HistoricalScheduleVersion)}>
              <option value="final_adjusted">final_adjusted</option>
              <option value="optimized_baseline">optimized_baseline</option>
            </select>
          </label>
        </div>
        <DataTable<HistoricalScheduleRow>
          columns={[
            {
              key: "slot",
              label: "Date / Time",
              width: "16%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <strong>{formatDate(row.exam_date)}</strong>
                  <p>{row.exam_time}</p>
                </div>
              ),
            },
            {
              key: "course",
              label: "Course",
              width: "14%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <strong>{row.course_code}</strong>
                  <p>Sec {row.section_no}</p>
                </div>
              ),
            },
            {
              key: "instructor_name",
              label: "Instructor",
              width: "18%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <strong>{row.instructor_name}</strong>
                  <p>{formatNumber(row.student_count)} students</p>
                </div>
              ),
            },
            {
              key: "room_name",
              label: "Exam room",
              width: "12%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <strong>{row.room_name ?? "-"}</strong>
                  <p>{row.room_opening_staff_name ? `Room opening: ${row.room_opening_staff_name}` : "No room-opening data"}</p>
                </div>
              ),
            },
            {
              key: "invigilators",
              label: "กรรมการคุมสอบ",
              width: "22%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <strong>{row.invigilators_raw ?? "-"}</strong>
                  <p>{row.invigilators.map((item) => item.display_name).join(", ") || "No parsed invigilators"}</p>
                </div>
              ),
            },
            {
              key: "distribution",
              label: "กรรมการจ่ายข้อสอบ",
              width: "18%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <strong>{row.paper_distribution_staff_name ?? "-"}</strong>
                  <p>{row.room_opening_staff_name ? `${row.room_opening_staff_name} (room opening)` : row.distribution_raw ?? "No slot assignment"}</p>
                  {row.parse_flags.length ? <p>{row.parse_flags.join(" | ")}</p> : null}
                </div>
              ),
            },
          ]}
          emptyTitle="No historical schedule rows"
          emptyDescription="Import the 2/2568 PDFs before reviewing the historical schedule."
          loading={rowsState.loading}
          rowKey={(row) => row.id}
          rows={rowsState.data?.rows ?? []}
          scrollThreshold={5}
          tableLayout="fixed"
        />
      </Card>

      <Card title="Distribution Slots" subtitle="Paper distribution is counted once per exam slot. Room opening is tracked but not counted in fairness totals.">
        <DataTable<HistoricalDistributionRow>
          columns={[
            {
              key: "slot",
              label: "Slot",
              width: "18%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <strong>{formatDate(row.exam_date)}</strong>
                  <p>{row.exam_time}</p>
                </div>
              ),
            },
            {
              key: "paper_distribution_staff_name",
              label: "Paper distribution",
              width: "18%",
              render: (row) => <span>{row.paper_distribution_staff_name ?? "-"}</span>,
            },
            {
              key: "room_opening_staff_name",
              label: "Room opening",
              width: "16%",
              render: (row) => <span>{row.room_opening_staff_name ?? "-"}</span>,
            },
            {
              key: "covered_courses",
              label: "Courses covered",
              width: "28%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <p>{row.covered_courses.join(", ") || "-"}</p>
                </div>
              ),
            },
            {
              key: "covered_rooms",
              label: "Rooms",
              width: "10%",
              render: (row) => <span>{row.covered_rooms.join(", ") || "-"}</span>,
            },
            {
              key: "source_mode",
              label: "Source",
              width: "10%",
              render: (row) => <span>{row.source_mode}</span>,
            },
          ]}
          emptyTitle="No distribution slots"
          emptyDescription="Distribution slots will appear once the PDF snapshot is imported."
          loading={distributionState.loading}
          rowKey={(row) => row.id}
          rows={distributionState.data?.rows ?? []}
          scrollThreshold={5}
          tableLayout="fixed"
        />
      </Card>

      <Card title="Workload Summary" subtitle="INVIGILATION and PAPER_DISTRIBUTION are counted. ROOM_OPENING is tracked separately and excluded from counted totals.">
        <DataTable<HistoricalWorkloadSummaryRow>
          columns={[
            {
              key: "person_name",
              label: "Person",
              width: "28%",
              render: (row) => <strong>{row.person_name}</strong>,
            },
            { key: "invigilation_count", label: "Invigilation", width: "14%" },
            { key: "paper_distribution_count", label: "Paper distribution", width: "16%" },
            { key: "room_opening_count", label: "Room opening", width: "14%" },
            { key: "total_counted_workload", label: "Counted total", width: "14%" },
            {
              key: "assignments",
              label: "Assignments",
              width: "14%",
              render: (row) => <span>{formatNumber(row.assignments.length)}</span>,
            },
          ]}
          emptyTitle="No historical workload summary"
          emptyDescription="Workload summary is generated from imported invigilators and slot-level distribution assignments."
          loading={workloadState.loading}
          rowKey={(row) => `${row.person_name}-${row.user_id ?? "none"}`}
          rows={workloadState.data?.summary ?? []}
          scrollThreshold={5}
          tableLayout="fixed"
        />
      </Card>

      <Card title="Workload Detail" subtitle="Source-aware detail rows for INVIGILATION, PAPER_DISTRIBUTION, and ROOM_OPENING.">
        <DataTable<HistoricalWorkloadAssignmentRow>
          columns={[
            {
              key: "person_name",
              label: "Person",
              width: "18%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <strong>{row.person_name}</strong>
                  <p>{row.duty_type}</p>
                </div>
              ),
            },
            {
              key: "slot",
              label: "Slot",
              width: "18%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <strong>{formatDate(row.date)}</strong>
                  <p>{row.time_slot}</p>
                </div>
              ),
            },
            {
              key: "courses_covered",
              label: "Courses covered",
              width: "28%",
              render: (row) => <span>{row.courses_covered.join(", ") || "-"}</span>,
            },
            {
              key: "rooms",
              label: "Rooms",
              width: "12%",
              render: (row) => <span>{row.rooms.join(", ") || "-"}</span>,
            },
            { key: "workload_count", label: "Load", width: "8%" },
            {
              key: "counted_or_not_counted",
              label: "Counted",
              width: "8%",
              render: (row) => <span>{row.counted_or_not_counted ? "Yes" : "Tracked only"}</span>,
            },
            { key: "version_kind", label: "Version", width: "8%" },
          ]}
          emptyTitle="No historical workload detail"
          emptyDescription="No workload rows are available for the selected snapshot."
          loading={workloadState.loading}
          rowKey={(row) => `${row.person_name}-${row.duty_type}-${row.date}-${row.time_slot}-${row.courses_covered.join("|")}`}
          rows={workloadState.data?.rows ?? []}
          scrollThreshold={5}
          tableLayout="fixed"
        />
      </Card>

      <Card title="Optimized vs Final Adjusted Comparison" subtitle="Detect room, invigilator, distribution, room-opening, and student-count changes by course/section/date/time.">
        <DataTable<HistoricalComparisonRow>
          columns={[
            {
              key: "slot",
              label: "Course / Slot",
              width: "20%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <strong>{row.course_code} Sec {row.section_no}</strong>
                  <p>{formatDate(row.exam_date)} · {row.exam_time}</p>
                </div>
              ),
            },
            {
              key: "changes",
              label: "Changes",
              width: "18%",
              render: (row) => <span>{row.changes.join(", ")}</span>,
            },
            {
              key: "baseline",
              label: "Optimized baseline",
              width: "31%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <strong>{String(row.baseline?.room_name ?? "-")}</strong>
                  <p>{String(row.baseline?.invigilators_raw ?? "-")}</p>
                  <p>{String(row.baseline?.paper_distribution_staff_name ?? "-")} / {String(row.baseline?.room_opening_staff_name ?? "-")}</p>
                </div>
              ),
            },
            {
              key: "final",
              label: "Final adjusted",
              width: "31%",
              render: (row) => (
                <div className="data-table__content data-table__content--clamp">
                  <strong>{String(row.final?.room_name ?? "-")}</strong>
                  <p>{String(row.final?.invigilators_raw ?? "-")}</p>
                  <p>{String(row.final?.paper_distribution_staff_name ?? "-")} / {String(row.final?.room_opening_staff_name ?? "-")}</p>
                </div>
              ),
            },
          ]}
          emptyTitle="No differences detected"
          emptyDescription="The selected optimized baseline and final adjusted snapshots are identical."
          loading={comparisonState.loading}
          rowKey={(row) => row.key}
          rows={comparisonState.data?.rows ?? []}
          scrollThreshold={5}
          tableLayout="fixed"
        />
      </Card>
    </div>
  );
}
