import { DataTable } from "@/components/ui/DataTable";
import { StatusChip } from "@/components/ui/StatusChip";
import type { WorkflowRegistryRow } from "@/hooks/useWorkflowData";
import { statusLabel, statusTone } from "@/utils/statusPresentation";

interface WorkflowRegistryTableProps {
  rows: WorkflowRegistryRow[];
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
          render: (row) => <StatusChip tone={statusTone(row.status)}>{statusLabel(row.status)}</StatusChip>,
        },
        {
          key: "risk",
          label: "Risk",
          render: (row) => <StatusChip tone={statusTone(row.risk)}>{statusLabel(row.risk)}</StatusChip>,
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
