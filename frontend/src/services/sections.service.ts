import type { SectionOut } from "@/types/api";
import { del, get, post, put } from "./api";

export interface SectionFilters {
  search?: string;
  semester?: string;
  academic_year?: string;
}

type QueryValue = string | number | boolean | null | undefined;

export function listSections(filters: SectionFilters = {}) {
  return get<SectionOut[]>("/courses/sections", { query: filters as Record<string, QueryValue> });
}

export function createSection(body: Record<string, unknown>) {
  return post<SectionOut>("/courses/sections", body);
}

export function updateSection(sectionId: number, body: Record<string, unknown>) {
  return put<SectionOut>(`/courses/sections/${sectionId}`, body);
}

export function deleteSection(sectionId: number) {
  return del<{ success: boolean }>(`/courses/sections/${sectionId}`);
}
