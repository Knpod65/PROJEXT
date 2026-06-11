import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { useI18n } from "@/i18n";
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
  const { t } = useI18n();
  return (
    <div className="table-wrap">
      <table className="data-table submissions-table">
        <thead>
          <tr>
            <th>{t("legacy.submissions.table.examId")}</th>
            <th>{t("legacy.submissions.table.subject")}</th>
            <th>{t("legacy.submissions.table.submitted")}</th>
            <th>{t("common.status")}</th>
            <th>{t("legacy.submissions.table.examType")}</th>
            <th>{t("legacy.submissions.table.version")}</th>
            <th className="submissions-table__actions-header">{t("common.actions")}</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>
                <strong>#{item.id}</strong>
                <p>{t("legacy.submissions.table.section", { value: item.section_no ?? "-" })}</p>
              </td>
              <td>
                <strong>{item.course_name ?? item.course_id ?? t("legacy.submissions.table.untitled")}</strong>
                <p>{item.course_id ?? t("legacy.submissions.table.coursePending")}</p>
              </td>
              <td>
                <strong>{formatDateTime(item.submitted_at)}</strong>
                <p>{item.submitter ?? t("legacy.submissions.table.ownerPending")}</p>
              </td>
              <td>
                <Badge variant={getStatusVariant(item.status)}>{t(`legacy.submissions.status.${item.status}`)}</Badge>
              </td>
              <td>{item.exam_type_choice ?? "-"}</td>
              <td>v{item.version ?? 1}</td>
              <td className="submissions-table__actions-cell">
                <Button size="sm" type="button" variant="outline" onClick={() => onOpenMessages(item)}>
                  {t("legacy.submissions.actions.openThread")}
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
