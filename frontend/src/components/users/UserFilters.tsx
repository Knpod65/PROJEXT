import type { FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import type { UserRole } from "@/types/api";

interface UserFiltersProps {
  query: string;
  roleFilter: "all" | UserRole;
  activeFilter: "all" | "active" | "inactive";
  onQueryChange: (value: string) => void;
  onRoleChange: (value: "all" | UserRole) => void;
  onActiveChange: (value: "all" | "active" | "inactive") => void;
  onReset: () => void;
}

export function UserFilters({
  activeFilter,
  onActiveChange,
  onQueryChange,
  onReset,
  onRoleChange,
  query,
  roleFilter,
}: UserFiltersProps) {
  return (
    <section className="filter-bar" aria-label="User filters">
      <div className="filter-bar__fields">
        <label className="filter-field">
          <span>Search</span>
          <input
            type="text"
            value={query}
            onChange={(event: FormEvent<HTMLInputElement>) => onQueryChange(event.currentTarget.value)}
            placeholder="Name, username, email, department"
          />
        </label>

        <label className="filter-field">
          <span>Role</span>
          <select
            value={roleFilter}
            onChange={(event: FormEvent<HTMLSelectElement>) => onRoleChange(event.currentTarget.value as "all" | UserRole)}
          >
            <option value="all">All roles</option>
            <option value="admin">Admin</option>
            <option value="esq_head">ESQ Head</option>
            <option value="secretary">Secretary</option>
            <option value="dept_supervisor">Dept Supervisor</option>
            <option value="staff">Staff</option>
            <option value="teacher">Teacher</option>
            <option value="student">Student</option>
            <option value="print_shop">Print Shop</option>
          </select>
        </label>

        <label className="filter-field">
          <span>Status</span>
          <select
            value={activeFilter}
            onChange={(event: FormEvent<HTMLSelectElement>) =>
              onActiveChange(event.currentTarget.value as "all" | "active" | "inactive")
            }
          >
            <option value="all">All statuses</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
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
