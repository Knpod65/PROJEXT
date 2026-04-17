import { Badge } from "@/components/ui/Badge";
import { DataTable } from "@/components/ui/DataTable";
import type { RoomRecordV2 } from "@/hooks/useRoomsData";
import { formatNumber } from "@/utils/format";

function statusVariant(status: RoomRecordV2["status"]) {
  if (status === "available") {
    return "green" as const;
  }

  if (status === "occupied") {
    return "gold" as const;
  }

  if (status === "maintenance") {
    return "crimson" as const;
  }

  return "orange" as const;
}

function stageVariant(stage: RoomRecordV2["allocationStage"]) {
  if (stage === "assigned") {
    return "green" as const;
  }

  if (stage === "pending") {
    return "gold" as const;
  }

  if (stage === "review") {
    return "orange" as const;
  }

  return "gray" as const;
}

interface RoomAvailabilityTableProps {
  rows: RoomRecordV2[];
}

export function RoomAvailabilityTable({ rows }: RoomAvailabilityTableProps) {
  return (
    <DataTable<RoomRecordV2>
      columns={[
        {
          key: "room_name",
          label: "Room",
          render: (row) => (
            <div>
              <strong>{row.room_name}</strong>
              <p>{row.building}</p>
            </div>
          ),
        },
        {
          key: "zone",
          label: "Zone",
        },
        {
          key: "capacity",
          label: "Capacity",
          render: (row) => <span>{formatNumber(row.capacity)}</span>,
        },
        {
          key: "status",
          label: "Status",
          render: (row) => <Badge variant={statusVariant(row.status)}>{row.status}</Badge>,
        },
        {
          key: "allocationStage",
          label: "Allocation Stage",
          render: (row) => <Badge variant={stageVariant(row.allocationStage)}>{row.allocationStage}</Badge>,
        },
        {
          key: "upcomingExam",
          label: "Upcoming Exam",
        },
        {
          key: "nextSlot",
          label: "Next Slot",
        },
        {
          key: "notes",
          label: "Notes",
        },
      ]}
      rows={rows}
      rowKey={(row) => row.id}
      emptyTitle="No rooms matched"
      emptyDescription="Try changing the building, status, or stage filters."
    />
  );
}
