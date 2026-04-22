import { Badge } from "@/components/ui/Badge";
import { DataTable } from "@/components/ui/DataTable";
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
        <span className="schedule-table__count">{items.length} sessions</span>
      </header>

      <DataTable<ScheduleWithSection>
        columns={[
          {
            key: "date_time",
            label: "Date & time",
            width: "15%",
            minWidth: "150px",
            render: (schedule) => (
              <div className="data-table__content data-table__content--truncate">
                <strong>{formatDate(schedule.exam_date)}</strong>
                <p>{schedule.exam_time}</p>
              </div>
            ),
          },
          {
            key: "exam",
            label: "Exam",
            width: "30%",
            minWidth: "280px",
            cellClassName: "schedule-table__cell--exam",
            render: (schedule) => (
              <div className="data-table__content">
                <strong>{schedule.section?.course?.course_name_th ?? schedule.section?.course?.course_id ?? "Untitled exam"}</strong>
                <p>
                  {schedule.section?.course?.course_id ?? "Course pending"} / Section {schedule.section?.section_no ?? "-"}
                </p>
              </div>
            ),
          },
          {
            key: "room",
            label: "Room",
            width: "15%",
            minWidth: "150px",
            render: (schedule) => (
              <div className="data-table__content data-table__content--truncate">
                <strong>{schedule.room?.room_name ?? "Room pending"}</strong>
                <p>{schedule.room?.building ?? "Building not assigned"}</p>
              </div>
            ),
          },
          {
            key: "coverage",
            label: "Coverage",
            width: "18%",
            minWidth: "180px",
            cellClassName: "schedule-table__cell--coverage",
            render: (schedule) => (
              <div className="data-table__content">
                <strong>{getStaffLine(schedule)}</strong>
                <p>{formatNumber(schedule.section?.num_students ?? 0)} students</p>
              </div>
            ),
          },
          {
            key: "paper",
            label: "Paper",
            width: "10%",
            minWidth: "110px",
            render: (schedule) => (
              <div className="data-table__content data-table__content--truncate schedule-table__paper">
                <strong>{formatNumber(schedule.total_sheets)}</strong>
                <p>{formatNumber(schedule.num_pages)} pages</p>
              </div>
            ),
          },
          {
            key: "status",
            label: "Status",
            width: "12%",
            minWidth: "120px",
            render: (schedule) => (
              <span className="schedule-table__status">
                <Badge variant={getStatusVariant(schedule.status)}>{schedule.status}</Badge>
              </span>
            ),
          },
        ]}
        rows={items}
        rowKey={(schedule) => schedule.id}
        compact
        tableClassName="schedule-table"
        tableLayout="fixed"
        scrollThreshold={5}
        maxHeight={360}
      />
    </section>
  );
}
