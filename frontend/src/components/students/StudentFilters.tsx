import type { FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import type { EnrollmentStage } from "@/hooks/useStudentsData";

interface StudentFiltersProps {
  query: string;
  facultyFilter: "all" | string;
  stageFilter: "all" | EnrollmentStage;
  faculties: string[];
  onQueryChange: (value: string) => void;
  onFacultyChange: (value: "all" | string) => void;
  onStageChange: (value: "all" | EnrollmentStage) => void;
  onReset: () => void;
}

export function StudentFilters({
  faculties,
  facultyFilter,
  onFacultyChange,
  onQueryChange,
  onReset,
  onStageChange,
  query,
  stageFilter,
}: StudentFiltersProps) {
  return (
    <section className="filter-bar" aria-label="Student filters">
      <div className="filter-bar__fields">
        <label className="filter-field">
          <span>Search</span>
          <input
            type="text"
            value={query}
            onChange={(event: FormEvent<HTMLInputElement>) => onQueryChange(event.currentTarget.value)}
            placeholder="Student ID, name, program, section"
          />
        </label>

        <label className="filter-field">
          <span>Faculty</span>
          <select
            value={facultyFilter}
            onChange={(event: FormEvent<HTMLSelectElement>) => onFacultyChange(event.currentTarget.value)}
          >
            <option value="all">All faculties</option>
            {faculties.map((faculty) => (
              <option key={faculty} value={faculty}>{faculty}</option>
            ))}
          </select>
        </label>

        <label className="filter-field">
          <span>Enrollment Stage</span>
          <select
            value={stageFilter}
            onChange={(event: FormEvent<HTMLSelectElement>) =>
              onStageChange(event.currentTarget.value as "all" | EnrollmentStage)
            }
          >
            <option value="all">All stages</option>
            <option value="new">New</option>
            <option value="verified">Verified</option>
            <option value="enrolled">Enrolled</option>
            <option value="flagged">Flagged</option>
          </select>
        </label>
      </div>

      <div className="filter-bar__actions">
        <Button type="button" variant="outline" onClick={onReset}>Reset Filters</Button>
      </div>
    </section>
  );
}
