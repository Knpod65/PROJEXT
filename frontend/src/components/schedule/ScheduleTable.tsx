import { Badge } from "@/components/ui/Badge";
import type { ScheduleWithSection } from "@/types/api";
import { formatDate, formatNumber } from "@/utils/format";

function getStatusVariant(status?: string) {
  switch (status) {
    case "confirmed":
      return "green";
    case "published":
      return "blue";
    case "cancelled":
      return "crimson";
    case "draft":
    default:
      return "gray";
  }
}

function getStaffLine(schedule: ScheduleWithSection) {
  if (schedule.supervisions.length === 0) {
    return "Unassigned";
  }

  return schedule.supervisions
    .map((item) => item.user?.full_name ?? item.user?.username ?? item.role_in_exam ?? "Staff")
    .join(", ");
}

interface ScheduleTableProps {
  title: string;
  subtitle: string;
  items: ScheduleWithSection[];
}

export function ScheduleTable({ items, subtitle, title }: ScheduleTableProps) {
  return (
    <section className="schedule-board">
      <header className="schedule-board__header">
        <div>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
        <span>{items.length} sessions</span>
      </header>

      <div className="table-wrap">
        <table className="data-table schedule-table">
          <thead>
            <tr>
              <th>Date & time</th>
              <th>Exam</th>
              <th>Room</th>
              <th>Coverage</th>
              <th>Paper</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {items.map((schedule) => (
              <tr key={schedule.id}>
                <td>
                  <strong>{formatDate(schedule.exam_date)}</strong>
                  <p>{schedule.exam_time}</p>
                </td>
                <td>
                  <strong>{schedule.section?.course?.course_name_th ?? schedule.section?.course?.course_id ?? "Untitled exam"}</strong>
                  <p>
                    {schedule.section?.course?.course_id ?? "Course pending"} / Section {schedule.section?.section_no ?? "-"}
                  </p>
                </td>
                <td>
                  <strong>{schedule.room?.room_name ?? "Room pending"}</strong>
                  <p>{schedule.room?.building ?? "Building not assigned"}</p>
                </td>
                <td>
                  <strong>{getStaffLine(schedule)}</strong>
                  <p>{formatNumber(schedule.section?.num_students ?? 0)} students</p>
                </td>
                <td>
                  <strong>{formatNumber(schedule.total_sheets)}</strong>
                  <p>{formatNumber(schedule.num_pages)} pages</p>
                </td>
                <td>
                  <Badge variant={getStatusVariant(schedule.status)}>{schedule.status}</Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
