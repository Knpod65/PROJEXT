import { Badge } from "@/components/ui/Badge";
import { DataTable } from "@/components/ui/DataTable";
import type { WorkflowRegistryRow } from "@/hooks/useWorkflowData";

interface WorkflowRegistryTableProps {
  rows: WorkflowRegistryRow[];
}

function statusVariant(status: WorkflowRegistryRow["status"]) {
  switch (status) {
    case "ready":
      return "green" as const;
    case "returned":
      return "crimson" as const;
    default:
      return "gold" as const;
  }
}

function riskVariant(risk: WorkflowRegistryRow["risk"]) {
  switch (risk) {
    case "high":
      return "crimson" as const;
    case "medium":
      return "orange" as const;
    default:
      return "gray" as const;
  }
}

export function WorkflowRegistryTable({ rows }: WorkflowRegistryTableProps) {
  return (
    <DataTable<WorkflowRegistryRow>
      columns={[
        {
          key: "batchCode",
          label: "Batch",
        },
        {
          key: "department",
          label: "Department",
        },
        {
          key: "owner",
          label: "Owner",
        },
        {
          key: "status",
          label: "Status",
          render: (row) => <Badge variant={statusVariant(row.status)}>{row.status}</Badge>,
        },
        {
          key: "risk",
          label: "Risk",
          render: (row) => <Badge variant={riskVariant(row.risk)}>{row.risk}</Badge>,
        },
        {
          key: "comment",
          label: "Review Note",
        },
        {
          key: "lastUpdated",
          label: "Last Updated",
        },
      ]}
      rows={rows}
      rowKey={(row) => row.id}
      emptyTitle="No registry records matched"
      emptyDescription="Try changing search text or status filter."
    />
  );
}
