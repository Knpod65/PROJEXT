import { Button } from "@/components/ui/Button";
import type { SwapPriority, SwapStatus } from "@/hooks/useSwapsData";
import type { FormEvent } from "react";

interface SwapFiltersProps {
  query: string;
  statusFilter: "all" | SwapStatus;
  priorityFilter: "all" | SwapPriority;
  onQueryChange: (value: string) => void;
  onStatusChange: (value: "all" | SwapStatus) => void;
  onPriorityChange: (value: "all" | SwapPriority) => void;
  onReset: () => void;
}

export function SwapFilters({
  onPriorityChange,
  onQueryChange,
  onReset,
  onStatusChange,
  priorityFilter,
  query,
  statusFilter,
}: SwapFiltersProps) {
  return (
    <section className="filter-bar" aria-label="Swap filters">
      <div className="filter-bar__fields">
        <label className="filter-field">
          <span>Search</span>
          <input
            type="text"
            value={query}
            onChange={(event: FormEvent<HTMLInputElement>) => onQueryChange(event.currentTarget.value)}
            placeholder="Requester, target, course, room"
          />
        </label>

        <label className="filter-field">
          <span>Status</span>
          <select
            value={statusFilter}
            onChange={(event: FormEvent<HTMLSelectElement>) => onStatusChange(event.currentTarget.value as "all" | SwapStatus)}
          >
            <option value="all">All statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="escalated">Escalated</option>
          </select>
        </label>

        <label className="filter-field">
          <span>Priority</span>
          <select
            value={priorityFilter}
            onChange={(event: FormEvent<HTMLSelectElement>) => onPriorityChange(event.currentTarget.value as "all" | SwapPriority)}
          >
            <option value="all">All priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
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
