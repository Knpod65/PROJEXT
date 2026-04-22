import type { FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { useI18n } from "@/i18n";
import type { UserRole } from "@/types/api";
import { formatRole, formatTranslatedValue } from "@/utils/format";

interface UserFiltersProps {
  query: string;
  roleFilter: "all" | UserRole;
  activeFilter: "all" | "active" | "inactive";
  onQueryChange: (value: string) => void;
  onRoleChange: (value: "all" | UserRole) => void;
  onActiveChange: (value: "all" | "active" | "inactive") => void;
  onReset: () => void;
}

const roleOptions: UserRole[] = ["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher", "student", "print_shop"];

export function UserFilters({
  activeFilter,
  onActiveChange,
  onQueryChange,
  onReset,
  onRoleChange,
  query,
  roleFilter,
}: UserFiltersProps) {
  const { t } = useI18n();

  return (
    <section className="filter-bar" aria-label={t("users.filtersAria")}>
      <div className="filter-bar__fields">
        <label className="filter-field">
          <span>{t("common.search")}</span>
          <input
            type="text"
            value={query}
            onChange={(event: FormEvent<HTMLInputElement>) => onQueryChange(event.currentTarget.value)}
            placeholder={t("users.filters.searchPlaceholder")}
          />
        </label>

        <label className="filter-field">
          <span>{t("common.role")}</span>
          <select
            value={roleFilter}
            onChange={(event: FormEvent<HTMLSelectElement>) => onRoleChange(event.currentTarget.value as "all" | UserRole)}
          >
            <option value="all">{t("common.allRoles")}</option>
            {roleOptions.map((role) => (
              <option key={role} value={role}>
                {formatRole(role)}
              </option>
            ))}
          </select>
        </label>

        <label className="filter-field">
          <span>{t("common.status")}</span>
          <select
            value={activeFilter}
            onChange={(event: FormEvent<HTMLSelectElement>) =>
              onActiveChange(event.currentTarget.value as "all" | "active" | "inactive")
            }
          >
            <option value="all">{t("common.allStatuses")}</option>
            <option value="active">{formatTranslatedValue("status", "active")}</option>
            <option value="inactive">{formatTranslatedValue("status", "inactive")}</option>
          </select>
        </label>
      </div>

      <div className="filter-bar__actions">
        <Button type="button" variant="outline" onClick={onReset}>
          {t("users.filters.reset")}
        </Button>
      </div>
    </section>
  );
}
