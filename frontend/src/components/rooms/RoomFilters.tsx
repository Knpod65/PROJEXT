import type { FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import type { AllocationStage, RoomStatus } from "@/hooks/useRoomsData";

interface RoomFiltersProps {
  query: string;
  buildingFilter: string;
  statusFilter: "all" | RoomStatus;
  stageFilter: "all" | AllocationStage;
  buildings: string[];
  onQueryChange: (value: string) => void;
  onBuildingChange: (value: string) => void;
  onStatusChange: (value: "all" | RoomStatus) => void;
  onStageChange: (value: "all" | AllocationStage) => void;
  onReset: () => void;
}

export function RoomFilters({
  buildingFilter,
  buildings,
  onBuildingChange,
  onQueryChange,
  onReset,
  onStageChange,
  onStatusChange,
  query,
  stageFilter,
  statusFilter,
}: RoomFiltersProps) {
  return (
    <section className="filter-bar" aria-label="Room filters">
      <div className="filter-bar__fields">
        <label className="filter-field">
          <span>Search</span>
          <input
            type="text"
            value={query}
            onChange={(event: FormEvent<HTMLInputElement>) => onQueryChange(event.currentTarget.value)}
            placeholder="Room name, building, zone, or exam"
          />
        </label>

        <label className="filter-field">
          <span>Building</span>
          <select value={buildingFilter} onChange={(event: FormEvent<HTMLSelectElement>) => onBuildingChange(event.currentTarget.value)}>
            <option value="all">All buildings</option>
            {buildings.map((building) => (
              <option key={building} value={building}>{building}</option>
            ))}
          </select>
        </label>

        <label className="filter-field">
          <span>Status</span>
          <select
            value={statusFilter}
            onChange={(event: FormEvent<HTMLSelectElement>) => onStatusChange(event.currentTarget.value as "all" | RoomStatus)}
          >
            <option value="all">All statuses</option>
            <option value="available">Available</option>
            <option value="occupied">Occupied</option>
            <option value="maintenance">Maintenance</option>
            <option value="reserved">Reserved</option>
          </select>
        </label>

        <label className="filter-field">
          <span>Allocation Stage</span>
          <select
            value={stageFilter}
            onChange={(event: FormEvent<HTMLSelectElement>) => onStageChange(event.currentTarget.value as "all" | AllocationStage)}
          >
            <option value="all">All stages</option>
            <option value="free">Free</option>
            <option value="pending">Pending</option>
            <option value="assigned">Assigned</option>
            <option value="review">Review</option>
          </select>
        </label>
      </div>

      <div className="filter-bar__actions">
        <Button type="button" variant="outline" onClick={onReset}>
          Reset Filters
        </Button>
      </div>
    </section>
  );
}
