import type { UserMe, UserRole } from "@/types/api";

export const ROLE_HOME_ROUTE: Record<UserRole, string> = {
  admin: "/dashboard",
  esq_head: "/schedule",
  secretary: "/schedule",
  dept_supervisor: "/schedule",
  staff: "/dashboard",
  teacher: "/schedule",
  student: "/student-search",
};

export function getEffectiveRole(user?: UserMe | null): UserRole | null {
  if (!user) return null;
  return user.view_as_role ?? user.effective_role ?? user.role;
}

export function hasRole(user: UserMe | null | undefined, allowedRoles?: UserRole[]) {
  if (!allowedRoles || allowedRoles.length === 0) return true;
  const role = getEffectiveRole(user);
  return role ? allowedRoles.includes(role) : false;
}

export function canViewAs(user: UserMe | null | undefined) {
  return user?.role === "admin";
}

export function getDefaultRoute(user: UserMe | null | undefined) {
  const role = getEffectiveRole(user);
  return role ? ROLE_HOME_ROUTE[role] : "/login";
}
