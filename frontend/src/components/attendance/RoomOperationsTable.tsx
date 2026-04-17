import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import type { CheckinEventItem, ScheduleWithSection } from "@/types/api";
import { formatDate, formatNumber } from "@/utils/format";

export interface RoomOperationsRow {
  schedule: ScheduleWithSection;
  events: CheckinEventItem[];
}

function getAttendanceStatus(row: RoomOperationsRow) {
  const latest = row.events[0];

  if (!latest) {
    return { label: "No check-in", variant: "gray" as const };
  }

  if (latest.confirmed || latest.confirmed_by_all) {
    return { label: "Confirmed", variant: "green" as const };
  }

  return { label: "Pending confirm", variant: "gold" as const };
}

interface RoomOperationsTableProps {
  rows: RoomOperationsRow[];
  mode: "attendance" | "checkins";
  onOpenDetails: (schedule: ScheduleWithSection) => void;
  onPrimaryAction?: (schedule: ScheduleWithSection) => void;
  onConfirmLatest?: (event: CheckinEventItem) => void;
  confirmingId?: number | null;
}

export function RoomOperationsTable({
  confirmingId,
  mode,
  onConfirmLatest,
  onOpenDetails,
  onPrimaryAction,
  rows,
}: RoomOperationsTableProps) {
  return (
    <div className="table-wrap">
      <table className="data-table room-operations-table">
        <thead>
          <tr>
            <th>Session</th>
            <th>Date & time</th>
            <th>Room</th>
            <th>Faculty</th>
            <th>Attendance</th>
            <th>Status</th>
            <th className="room-operations-table__actions-header">Actions</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const latest = row.events[0];
            const status = getAttendanceStatus(row);
            const present = latest?.students_present ?? 0;
            const absent = latest?.absent_count ?? 0;

            return (
              <tr key={row.schedule.id}>
                <td>
                  <strong>{row.schedule.section?.course?.course_name_th ?? row.schedule.section?.course?.course_id ?? "Untitled exam"}</strong>
                  <p>Section {row.schedule.section?.section_no ?? "-"} / {formatNumber(row.schedule.section?.num_students ?? 0)} students</p>
                </td>
                <td>
                  <strong>{formatDate(row.schedule.exam_date)}</strong>
                  <p>{row.schedule.exam_time}</p>
                </td>
                <td>
                  <strong>{row.schedule.room?.room_name ?? "Room pending"}</strong>
                  <p>{row.schedule.room?.building ?? "Building not assigned"}</p>
                </td>
                <td>
                  <strong>{row.schedule.section?.teacher?.full_name ?? row.schedule.section?.teacher?.username ?? "Faculty pending"}</strong>
                  <p>{row.schedule.supervisions.length} invigilator slots</p>
                </td>
                <td>
                  <strong>{formatNumber(present)}</strong>
                  <p>{formatNumber(absent)} absent</p>
                </td>
                <td>
                  <Badge variant={status.variant}>{status.label}</Badge>
                </td>
                <td className="room-operations-table__actions-cell">
                  <Button size="sm" type="button" variant="outline" onClick={() => onOpenDetails(row.schedule)}>
                    View details
                  </Button>
                  {mode === "checkins" && onPrimaryAction ? (
                    <Button size="sm" type="button" onClick={() => onPrimaryAction(row.schedule)}>
                      {latest ? "New update" : "Check in"}
                    </Button>
                  ) : null}
                  {mode === "checkins" && latest && !latest.confirmed && !latest.confirmed_by_all && onConfirmLatest ? (
                    <Button
                      disabled={confirmingId === latest.id}
                      size="sm"
                      type="button"
                      variant="ghost"
                      onClick={() => onConfirmLatest(latest)}
                    >
                      {confirmingId === latest.id ? "Confirming..." : "Confirm"}
                    </Button>
                  ) : null}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
