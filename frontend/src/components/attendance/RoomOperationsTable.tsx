import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { useI18n } from "@/i18n";
import type { CheckinEventItem, ScheduleWithSection } from "@/types/api";
import { formatDate, formatNumber } from "@/utils/format";

export interface RoomOperationsRow {
  schedule: ScheduleWithSection;
  events: CheckinEventItem[];
}

function getAttendanceStatus(row: RoomOperationsRow) {
  const latest = row.events[0];

  if (!latest) {
    return { key: "roomOperations.status.noCheckin", variant: "gray" as const };
  }

  if (latest.confirmed || latest.confirmed_by_all) {
    return { key: "common.confirmed", variant: "green" as const };
  }

  return { key: "roomOperations.status.pendingConfirm", variant: "gold" as const };
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
  const { t } = useI18n();

  return (
    <div className="table-wrap">
      <table className="data-table room-operations-table">
        <thead>
          <tr>
            <th>{t("roomOperations.table.session")}</th>
            <th>{t("roomOperations.table.dateTime")}</th>
            <th>{t("common.room")}</th>
            <th>{t("roomOperations.table.faculty")}</th>
            <th>{t("roomOperations.table.attendance")}</th>
            <th>{t("common.status")}</th>
            <th className="room-operations-table__actions-header">{t("common.actions")}</th>
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
                  <strong>
                    {row.schedule.section?.course?.course_name_th ??
                      row.schedule.section?.course?.course_id ??
                      t("roomOperations.table.untitledExam")}
                  </strong>
                  <p>
                    {t("roomOperations.table.sectionStudents", {
                      section: row.schedule.section?.section_no ?? "-",
                      count: formatNumber(row.schedule.section?.num_students ?? 0),
                    })}
                  </p>
                </td>
                <td>
                  <strong>{formatDate(row.schedule.exam_date)}</strong>
                  <p>{row.schedule.exam_time}</p>
                </td>
                <td>
                  <strong>{row.schedule.room?.room_name ?? t("roomOperations.table.roomPending")}</strong>
                  <p>{row.schedule.room?.building ?? t("roomOperations.table.buildingPending")}</p>
                </td>
                <td>
                  <strong>
                    {row.schedule.section?.teacher?.full_name ??
                      row.schedule.section?.teacher?.username ??
                      t("roomOperations.table.facultyPending")}
                  </strong>
                  <p>{t("roomOperations.table.invigilatorSlots", { count: row.schedule.supervisions.length })}</p>
                </td>
                <td>
                  <strong>{formatNumber(present)}</strong>
                  <p>{t("roomOperations.table.absentCount", { count: formatNumber(absent) })}</p>
                </td>
                <td>
                  <Badge variant={status.variant}>{t(status.key)}</Badge>
                </td>
                <td className="room-operations-table__actions-cell">
                  <Button size="sm" type="button" variant="outline" onClick={() => onOpenDetails(row.schedule)}>
                    {t("common.details")}
                  </Button>
                  {mode === "checkins" && onPrimaryAction ? (
                    <Button size="sm" type="button" onClick={() => onPrimaryAction(row.schedule)}>
                      {latest ? t("roomOperations.actions.newUpdate") : t("roomOperations.actions.checkIn")}
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
                      {confirmingId === latest.id ? t("roomOperations.actions.confirming") : t("common.confirm")}
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
