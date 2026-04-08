import type { SubmissionListItem } from "@/types/api";
import { formatDateTime } from "@/utils/format";

import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";

function submissionVariant(status: string) {
  switch (status) {
    case "approved":
      return "green";
    case "pending":
      return "gold";
    case "rejected":
      return "crimson";
    case "revision":
      return "orange";
    default:
      return "gray";
  }
}

interface SubmissionCardProps {
  item: SubmissionListItem;
  onOpenMessages?: (item: SubmissionListItem) => void;
}

export function SubmissionCard({ item, onOpenMessages }: SubmissionCardProps) {
  return (
    <Card
      className="submission-card"
      title={`${item.course_id ?? "—"} ${item.course_name ?? "ยังไม่ระบุวิชา"}`}
      subtitle={`ตอน ${item.section_no ?? "-"} • ส่งเมื่อ ${formatDateTime(item.submitted_at)}`}
      actions={<Badge variant={submissionVariant(item.status)}>{item.status}</Badge>}
    >
      <div className="submission-card__meta">
        <span>รูปแบบ: {item.exam_type_choice ?? "ยังไม่ระบุ"}</span>
        <span>เวอร์ชัน: {item.version ?? 1}</span>
        <span>ผู้ส่ง: {item.submitter ?? "—"}</span>
      </div>
      {onOpenMessages ? (
        <div className="submission-card__actions">
          <Button type="button" variant="outline" onClick={() => onOpenMessages(item)}>
            ดูข้อความ
          </Button>
        </div>
      ) : null}
    </Card>
  );
}
