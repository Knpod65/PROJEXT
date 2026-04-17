import { RoomAllocationMatrix } from "@/components/rooms/RoomAllocationMatrix";
import { RoomFilters } from "@/components/rooms/RoomFilters";
import { RoomStatsCards } from "@/components/rooms/RoomStatsCards";
import { RoomVenueOverview } from "@/components/rooms/RoomVenueOverview";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useRoomsData } from "@/hooks/useRoomsData";
import { useUi } from "@/store/ui.store";

export function VenueManagementV2Page() {
  const { toast } = useUi();
  const {
    allocationMatrix,
    buildingFilter,
    buildings,
    filteredVenues,
    query,
    resetFilters,
    setBuildingFilter,
    setQuery,
    setStageFilter,
    setStatusFilter,
    stageFilter,
    statusFilter,
    venueStats,
  } = useRoomsData();

  return (
    <div className="page-stack page-stack--spacious">
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">Venue management and capacity</span>
          <h1 className="page-hero__title">Venue Management V2</h1>
          <p className="page-hero__description">
            Mock venue-level capacity and allocation view following the room availability template. Allocation actions remain disabled in this milestone.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => toast("Venue refresh is preview-only in Milestone 6.", "info")}>Refresh</Button>
          <Button type="button" onClick={() => toast("Add venue is preview-only in Milestone 6.", "info")}>Add Venue</Button>
        </div>
      </section>

      <RoomStatsCards
        stats={{
          total: venueStats.total,
          available: venueStats.available,
          occupied: venueStats.occupied,
          maintenance: venueStats.reserved,
          reserved: venueStats.review,
          totalCapacity: venueStats.totalSeats,
        }}
        titlePrefix="Venue"
      />

      <RoomVenueOverview
        title="Venue Allocation Snapshot"
        subtitle="Mock summary of venue capacity and allocation state"
        metrics={[
          { label: "Venues in view", value: String(filteredVenues.length), tone: "blue" },
          { label: "Available venues", value: String(venueStats.available), tone: "green" },
          { label: "Reservation queue", value: String(venueStats.reserved), tone: "orange" },
          { label: "Under review", value: String(venueStats.review), tone: "crimson" },
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

      <Card title="Venue Capacity Table" subtitle="Mock capacity overview and usage by venue">
        <RoomAllocationMatrix
          rows={allocationMatrix}
          title="Venue Allocation Placeholder"
          subtitle="Shared matrix preview for venue-level scheduling and coverage"
        />
      </Card>
    </div>
  );
}
