import type { UserOut } from "@/types/api";
import { del, get, post, put } from "./api";

export function listUsers() {
  return get<UserOut[]>("/users");
}

export function createUser(body: Record<string, unknown>) {
  return post<UserOut>("/users", body);
}

export function updateUser(userId: number, body: Record<string, unknown>) {
  return put<UserOut>(`/users/${userId}`, body);
}

export function deactivateUser(userId: number) {
  return del<{ success: boolean; message?: string }>(`/users/${userId}`);
}

export function listTeachers() {
  return get<UserOut[]>("/users/teachers");
}
