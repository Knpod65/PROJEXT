import { useMemo, useState } from "react";

import { useAsyncData } from "@/hooks/useAsyncData";
import {
  createUser,
  deleteUser,
  listUsers,
  updateUser,
  updateUserStatus,
} from "@/services/users.service";
import type { UserOut, UserRole } from "@/types/api";

export interface UserStats {
  total: number;
  active: number;
  inactive: number;
  teachers: number;
  admins: number;
  pendingApprovals: number;
}

const trackedRoles: UserRole[] = [
  "admin",
  "teacher",
  "staff",
  "dept_supervisor",
  "esq_head",
  "secretary",
  "print_shop",
  "student",
];

export function useUsersData() {
  const [query, setQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState<"all" | UserRole>("all");
  const [activeFilter, setActiveFilter] = useState<"all" | "active" | "inactive">("all");

  const loader = () => listUsers();
  const state = useAsyncData(loader, []);

  const rows = useMemo(() => {
    const allRows = state.data ?? [];

    return allRows.filter((row: UserOut) => {
      const haystack = [
        row.full_name ?? "",
        row.username,
        row.email,
        row.department ?? "",
        row.dept_code ?? "",
      ]
        .join(" ")
        .toLowerCase();
      const matchesQuery = query.trim().length === 0 || haystack.includes(query.toLowerCase());
      const matchesRole = roleFilter === "all" || row.role === roleFilter;
      const matchesActive =
        activeFilter === "all" ||
        (activeFilter === "active" ? row.is_active : !row.is_active);

      return matchesQuery && matchesRole && matchesActive;
    });
  }, [activeFilter, query, roleFilter, state.data]);

  const stats = useMemo<UserStats>(() => {
    const allRows = state.data ?? [];

    return {
      total: allRows.length,
      active: allRows.filter((row: UserOut) => row.is_active).length,
      inactive: allRows.filter((row: UserOut) => !row.is_active).length,
      teachers: allRows.filter((row: UserOut) => row.role === "teacher").length,
      admins: allRows.filter((row: UserOut) => row.role === "admin").length,
      pendingApprovals: allRows.filter((row: UserOut) => row.is_active && row.role !== "admin").length,
    };
  }, [state.data]);

  const roleBreakdown = useMemo(() => {
    const allRows = state.data ?? [];
    const roleCounts = new Map<UserRole, number>();

    trackedRoles.forEach((role) => roleCounts.set(role, 0));
    allRows.forEach((row: UserOut) => {
      roleCounts.set(row.role, (roleCounts.get(row.role) ?? 0) + 1);
    });

    return trackedRoles.map((role) => ({
      role,
      count: roleCounts.get(role) ?? 0,
    }));
  }, [state.data]);

  const resetFilters = () => {
    setQuery("");
    setRoleFilter("all");
    setActiveFilter("all");
  };

  return {
    loading: state.loading,
    error: state.error,
    rows,
    stats,
    roleBreakdown,
    query,
    roleFilter,
    activeFilter,
    setQuery,
    setRoleFilter,
    setActiveFilter,
    resetFilters,
    reload: state.reload,
    createUser,
    deleteUser,
    updateUser,
    updateUserStatus,
  };
}
