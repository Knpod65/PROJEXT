import type { ScheduleWithSection } from "@/types/api";
import { formatDateRange, formatNumber } from "@/utils/format";

import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";

interface CheckinCardProps {
  schedule: ScheduleWithSection;
  checkedIn?: boolean;
  onCheckin?: () => void;
}

export function CheckinCard({ checkedIn, onCheckin, schedule }: CheckinCardProps) {
  return (
    <Card
      className="checkin-card"
      title={`${schedule.section?.course?.course_id ?? "—"} ${schedule.section?.course?.course_name_th ?? ""}`}
      subtitle={formatDateRange(schedule.exam_date, schedule.exam_time)}
      actions={<Badge variant={checkedIn ? "green" : "gold"}>{checkedIn ? "check-in แล้ว" : "รอ check-in"}</Badge>}
    >
      <div className="checkin-card__meta">
        <span>ห้อง: {schedule.room?.room_name ?? "ยังไม่กำหนด"}</span>
        <span>นักศึกษา: {formatNumber(schedule.section?.num_students ?? 0)} คน</span>
      </div>
      {onCheckin ? (
        <div className="checkin-card__actions">
          <Button type="button" onClick={onCheckin}>
            Check-in ด้วย GPS
          </Button>
        </div>
      ) : null}
    </Card>
  );
}
