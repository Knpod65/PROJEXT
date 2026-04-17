import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { DataTable } from "@/components/ui/DataTable";
import { getPrintJobActionLabel } from "@/hooks/usePrintQueueData";
import type { PrintQueueJob } from "@/types/api";
import { formatDate, formatNumber } from "@/utils/format";

function priorityVariant(priority: PrintQueueJob["priority"]) {
  if (priority === "high") {
    return "orange" as const;
  }

  if (priority === "medium") {
    return "blue" as const;
  }

  return "gray" as const;
}

function statusVariant(status: PrintQueueJob["status"]) {
  if (status === "processing") {
    return "gold" as const;
  }

  if (status === "completed") {
    return "navy" as const;
  }

  if (status === "dispatched") {
    return "blue" as const;
  }

  if (status === "delivered") {
    return "green" as const;
  }

  return "gray" as const;
}

interface PrintQueueTableProps {
  jobs: PrintQueueJob[];
  loading?: boolean;
  onPreview: (job: PrintQueueJob) => void;
  onAdvanceJob: (job: PrintQueueJob) => void;
}

export function PrintQueueTable({ jobs, loading, onAdvanceJob, onPreview }: PrintQueueTableProps) {
  return (
    <DataTable<PrintQueueJob>
      columns={[
        {
          key: "identity",
          label: "Queue Item",
          render: (job) => (
            <div>
              <strong>{job.course_code}</strong>
              <p>{job.subject_name}</p>
              <p>Section {job.section}</p>
            </div>
          ),
        },
        {
          key: "schedule",
          label: "Exam Schedule",
          render: (job) => (
            <div>
              <strong>{formatDate(job.exam_date)}</strong>
              <p>{job.room || "Room pending"}</p>
              <p>{job.exam_time ?? "Time pending"}</p>
            </div>
          ),
        },
        {
          key: "volume",
          label: "Volume",
          render: (job) => (
            <div>
              <strong>{formatNumber(job.total_sheets)} sheets</strong>
              <p>
                {formatNumber(job.students)} students x {formatNumber(job.pages)} pages
              </p>
            </div>
          ),
        },
        {
          key: "specs",
          label: "Print Specs",
          render: (job) => (
            <div className="tag-list">
              {job.specs.map((spec) => (
                <span key={`${job.id}-${spec}`} className="tag-list__item">
                  {spec}
                </span>
              ))}
            </div>
          ),
        },
        {
          key: "status",
          label: "Status",
          render: (job) => (
            <div className="plain-list" style={{ paddingLeft: 0 }}>
              <Badge variant={statusVariant(job.status)} size="sm">
                {job.status}
              </Badge>
              <Badge variant={priorityVariant(job.priority)} size="sm">
                {job.priority} priority
              </Badge>
            </div>
          ),
        },
        {
          key: "actions",
          label: "Actions",
          render: (job) => (
            <div className="submissions-table__actions-cell">
              <Button size="sm" type="button" variant="outline" onClick={() => onPreview(job)}>
                Details
              </Button>
              <Button
                size="sm"
                type="button"
                disabled={job.status === "delivered"}
                onClick={() => onAdvanceJob(job)}
              >
                {getPrintJobActionLabel(job.status)}
              </Button>
            </div>
          ),
        },
      ]}
      emptyTitle="No print jobs available"
      emptyDescription="Released submissions have not created any print queue jobs yet."
      loading={loading}
      rowKey={(job) => job.id}
      rows={jobs}
    />
  );
}
