import type { AuthResponse, UserMe, UserRole } from "@/types/api";
import { get, post } from "./api";

export function login(username: string, password: string) {
  return post<AuthResponse>("/auth/login", { username, password });
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

