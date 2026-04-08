import type { ReactNode } from "react";

import type { ScheduleWithSection } from "@/types/api";
import { formatDateRange, formatNumber } from "@/utils/format";

import { Badge } from "../ui/Badge";
import { Card } from "../ui/Card";

function statusVariant(status?: string) {
  switch (status) {
    case "published":
      return "blue";
    case "confirmed":
      return "green";
    case "cancelled":
      return "crimson";
    default:
      return "gray";
  }
}

interface ScheduleCardProps {
  schedule: ScheduleWithSection;
  actions?: ReactNode;
}

export function ScheduleCard({ actions, schedule }: ScheduleCardProps) {
  const course = schedule.section?.course;
  const teacher = schedule.section?.teacher;
  const supervisors = schedule.supervisions
    .map((item) => item.user?.full_name)
    .filter(Boolean)
    .join(", ");

  return (
    <Card
      className="schedule-card"
      title={`${course?.course_id ?? "—"} ${course?.course_name_th ?? "ยังไม่ระบุชื่อวิชา"}`}
      subtitle={formatDateRange(schedule.exam_date, schedule.exam_time)}
      actions={<Badge variant={statusVariant(schedule.status)}>{schedule.status ?? "draft"}</Badge>}
    >
      <div className="schedule-card__grid">
        <span>ห้อง: {schedule.room?.room_name ?? "ยังไม่กำหนด"}</span>
        <span>นศ.: {formatNumber(schedule.section?.num_students ?? 0)} คน</span>
        <span>แผ่น: {formatNumber(schedule.total_sheets)} แผ่น</span>
        <span>อาจารย์: {teacher?.full_name ?? "—"}</span>
      </div>
      {supervisors ? <p className="schedule-card__staff">ผู้คุมสอบ: {supervisors}</p> : null}
      {actions ? <div className="schedule-card__actions">{actions}</div> : null}
    </Card>
  );
}
