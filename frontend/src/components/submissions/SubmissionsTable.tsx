import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import type { SubmissionListItem } from "@/types/api";
import { formatDateTime } from "@/utils/format";

function getStatusVariant(status: string) {
  switch (status) {
    case "approved":
      return "green";
    case "rejected":
      return "crimson";
    case "pending":
      return "gold";
    case "submitted":
      return "blue";
    default:
      return "gray";
  }
}

interface SubmissionsTableProps {
  items: SubmissionListItem[];
  onOpenMessages: (item: SubmissionListItem) => void;
}

export function SubmissionsTable({ items, onOpenMessages }: SubmissionsTableProps) {
  return (
    <div className="table-wrap">
      <table className="data-table submissions-table">
        <thead>
          <tr>
            <th>Exam ID</th>
            <th>Subject</th>
            <th>Submitted</th>
            <th>Status</th>
            <th>Exam type</th>
            <th>Version</th>
            <th className="submissions-table__actions-header">Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>
                <strong>#{item.id}</strong>
                <p>Section {item.section_no ?? "-"}</p>
              </td>
              <td>
                <strong>{item.course_name ?? item.course_id ?? "Untitled submission"}</strong>
                <p>{item.course_id ?? "Course code pending"}</p>
              </td>
              <td>
                <strong>{formatDateTime(item.submitted_at)}</strong>
                <p>{item.submitter ?? "Pending submission owner"}</p>
              </td>
              <td>
                <Badge variant={getStatusVariant(item.status)}>{item.status}</Badge>
              </td>
              <td>{item.exam_type_choice ?? "-"}</td>
              <td>v{item.version ?? 1}</td>
              <td className="submissions-table__actions-cell">
                <Button size="sm" type="button" variant="outline" onClick={() => onOpenMessages(item)}>
                  Open thread
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
