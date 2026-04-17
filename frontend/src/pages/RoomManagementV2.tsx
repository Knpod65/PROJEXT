import { RoomAllocationMatrix } from "@/components/rooms/RoomAllocationMatrix";
import { RoomAvailabilityTable } from "@/components/rooms/RoomAvailabilityTable";
import { RoomFilters } from "@/components/rooms/RoomFilters";
import { RoomStatsCards } from "@/components/rooms/RoomStatsCards";
import { RoomVenueOverview } from "@/components/rooms/RoomVenueOverview";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useRoomsData } from "@/hooks/useRoomsData";
import { useUi } from "@/store/ui.store";

export function RoomManagementV2Page() {
  const { toast } = useUi();
  const {
    allocationMatrix,
    buildingFilter,
    buildings,
    filteredRooms,
    query,
    resetFilters,
    roomStats,
    setBuildingFilter,
    setQuery,
    setStageFilter,
    setStatusFilter,
    stageFilter,
    statusFilter,
  } = useRoomsData();

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">Room availability management</span>
          <h1 className="page-hero__title">Room Management V2</h1>
          <p className="page-hero__description">
            Mock room oversight based on the chosen Stitch template. Allocation changes are intentionally disabled in this milestone.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => toast("Allocation changes are preview-only in Milestone 6.", "info")}>Refresh</Button>
          <Button type="button" onClick={() => toast("Add room is preview-only in Milestone 6.", "info")}>Add Room</Button>
        </div>
      </section>

      <RoomStatsCards stats={roomStats} titlePrefix="Room" />

      <RoomVenueOverview
        title="Allocation Snapshot"
        subtitle="System-wide mock summary for room availability and usage"
        metrics={[
          { label: "Rooms in view", value: String(filteredRooms.length), tone: "blue" },
          { label: "Available rooms", value: String(roomStats.available), tone: "green" },
          { label: "Under maintenance", value: String(roomStats.maintenance), tone: "crimson" },
          { label: "Allocated sessions", value: String(roomStats.occupied), tone: "gold" },
        ]}
      />

      <RoomFilters
        query={query}
        buildingFilter={buildingFilter}
        statusFilter={statusFilter}
        stageFilter={stageFilter}
        buildings={buildings}
        onQueryChange={setQuery}
        onBuildingChange={setBuildingFilter}
        onStatusChange={setStatusFilter}
        onStageChange={setStageFilter}
        onReset={resetFilters}
      />

      <Card title="Availability Table" subtitle="Room availability, room status, and upcoming exam slots">
        <RoomAvailabilityTable rows={filteredRooms} />
      </Card>

      <Card title="Allocation Matrix Placeholder" subtitle="Mock grid only - no real allocation mutations yet">
        <RoomAllocationMatrix
          rows={allocationMatrix}
          title="Weekly Allocation Matrix"
          subtitle="Preview of mock room-to-slot assignments across the week"
        />
      </Card>
    </div>
  );
}
