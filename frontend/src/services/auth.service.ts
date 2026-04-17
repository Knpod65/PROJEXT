import type { AuthResponse, RoleSelectionValue, UserMe, UserRole } from "@/types/api";
import { get, post } from "./api";

export function login(username: string, password: string, selectedRole: RoleSelectionValue) {
  return post<AuthResponse>("/auth/login", { username, password, selected_role: selectedRole });
}

export function me() {
  return get<UserMe>("/auth/me");
}

export function logout() {
  return post<{ success: boolean; message?: string }>("/auth/logout");
}

export function setViewAs(role: UserRole | null) {
  return post<{ success: boolean; view_as_role: UserRole | null; effective_role: UserRole }>(
    "/auth/view-as",
    { role },
  );
}
