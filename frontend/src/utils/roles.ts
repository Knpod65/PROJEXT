import type { RoleSelectionValue, UserMe, UserRole } from "@/types/api";

export const PENDING_ROLE_STORAGE_KEY = "ems.pending_role";

export const ALL_APP_ROLES: UserRole[] = [
  "admin",
  "esq_head",
  "secretary",
  "dept_supervisor",
  "staff",
  "teacher",
  "student",
  "print_shop",
];

export const ROLE_HOME_ROUTE: Record<UserRole, string> = {
  admin: "/dashboard",
  esq_head: "/workflow",
  secretary: "/workflow",
  dept_supervisor: "/dashboard",
  staff: "/dashboard",
  teacher: "/dashboard",
  student: "/student-search",
  print_shop: "/print-queue",
};

const FALLBACK_ROLE_SETS: Record<UserRole, UserRole[]> = {
  admin: ALL_APP_ROLES,
  esq_head: ["esq_head"],
  secretary: ["secretary"],
  dept_supervisor: ["dept_supervisor"],
  staff: ["staff"],
  teacher: ["teacher"],
  student: ["student"],
  print_shop: ["print_shop"],
};

interface RoleAccessOptions {
  allowBaseAdminPreview?: boolean;
}

function canUseSessionStorage() {
  return typeof window !== "undefined" && typeof window.sessionStorage !== "undefined";
}

function isUserRole(value: unknown): value is UserRole {
  return typeof value === "string" && ALL_APP_ROLES.includes(value as UserRole);
}

export function isRoleSelectionValue(value: unknown): value is RoleSelectionValue {
  return value === "governance" || isUserRole(value);
}

export function getStoredPendingRole() {
  if (!canUseSessionStorage()) {
    return null;
  }

  const value = window.sessionStorage.getItem(PENDING_ROLE_STORAGE_KEY);
  return isRoleSelectionValue(value) ? value : null;
}

export function storePendingRole(role: RoleSelectionValue | null) {
  if (!canUseSessionStorage()) {
    return;
  }

  if (!role) {
    window.sessionStorage.removeItem(PENDING_ROLE_STORAGE_KEY);
    return;
  }

  window.sessionStorage.setItem(PENDING_ROLE_STORAGE_KEY, role);
}

export function getPublicEntryRoute() {
  return getStoredPendingRole() ? "/login" : "/role-selection";
}

export function getAvailableRoles(user?: UserMe | null) {
  if (!user) {
    return [];
  }

  const source =
    Array.isArray(user.available_roles) && user.available_roles.length > 0
      ? user.available_roles.filter(isUserRole)
      : FALLBACK_ROLE_SETS[user.role] ?? [user.role];

  return Array.from(new Set(source));
}

export function getBaseRole(user?: UserMe | null) {
  return user?.role ?? null;
}

export function getActiveRole(user?: UserMe | null) {
  if (!user) {
    return null;
  }

  if (isUserRole(user.active_role)) {
    return user.active_role;
  }

  return isUserRole(user.role) ? user.role : null;
}

export function getEffectiveRole(user?: UserMe | null) {
  if (!user) {
    return null;
  }

  if (user.view_as_role && isUserRole(user.view_as_role)) {
    return user.view_as_role;
  }

  if (isUserRole(user.active_role)) {
    return user.active_role;
  }

  if (isUserRole(user.effective_role)) {
    return user.effective_role;
  }

  return isUserRole(user.role) ? user.role : null;
}

export function hasRole(
  user: UserMe | null | undefined,
  allowedRoles?: UserRole[],
  options: RoleAccessOptions = {},
) {
  if (!allowedRoles || allowedRoles.length === 0) {
    return true;
  }

  const effectiveRole = getEffectiveRole(user);
  if (effectiveRole && allowedRoles.includes(effectiveRole)) {
    return true;
  }

  if (options.allowBaseAdminPreview && getBaseRole(user) === "admin") {
    return true;
  }

  return false;
}

export function canViewAs(user: UserMe | null | undefined) {
  return getBaseRole(user) === "admin" && getActiveRole(user) === "admin";
}

export function getDefaultRoute(user: UserMe | null | undefined) {
  const role = getEffectiveRole(user);
  return role ? ROLE_HOME_ROUTE[role] : getPublicEntryRoute();
}
