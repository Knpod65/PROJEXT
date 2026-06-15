import { DataTable } from "@/components/ui/DataTable";
import { StatusChip } from "@/components/ui/StatusChip";
import type { RoomRecordV2 } from "@/hooks/useRoomsData";
import { formatNumber } from "@/utils/format";
import { statusLabel, statusTone } from "@/utils/statusPresentation";

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
          render: (row) => <StatusChip tone={statusTone(row.status)}>{statusLabel(row.status)}</StatusChip>,
        },
        {
          key: "allocationStage",
          label: "Allocation Stage",
          render: (row) => <StatusChip tone={statusTone(row.allocationStage)}>{statusLabel(row.allocationStage)}</StatusChip>,
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
