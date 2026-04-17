import { Button } from "@/components/ui/Button";
import type { WorkflowBatchStatus } from "@/hooks/useWorkflowData";
import type { FormEvent } from "react";

interface WorkflowFiltersProps {
  query: string;
  statusFilter: "all" | WorkflowBatchStatus;
  onQueryChange: (value: string) => void;
  onStatusChange: (value: "all" | WorkflowBatchStatus) => void;
  onReset: () => void;
}

export function WorkflowFilters({
  onQueryChange,
  onReset,
  onStatusChange,
  query,
  statusFilter,
}: WorkflowFiltersProps) {
  return (
    <section className="filter-bar" aria-label="Workflow filters">
      <div className="filter-bar__fields">
        <label className="filter-field">
          <span>Search</span>
          <input
            type="text"
            value={query}
            onChange={(event: FormEvent<HTMLInputElement>) => onQueryChange(event.currentTarget.value)}
            placeholder="Batch code, department, owner"
          />
        </label>

        <label className="filter-field">
          <span>Status</span>
          <select
            value={statusFilter}
            onChange={(event: FormEvent<HTMLSelectElement>) => onStatusChange(event.currentTarget.value as "all" | WorkflowBatchStatus)}
          >
            <option value="all">All statuses</option>
            <option value="pending">Pending</option>
            <option value="ready">Ready</option>
            <option value="returned">Returned</option>
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
