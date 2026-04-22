import type {
  CopyCountSummary,
  RoomOut,
  ScheduleWithSection,
} from "@/types/api";
import { get, post, put } from "./api";

export interface ScheduleFilters {
  date?: string;
  room_id?: number;
  status?: string;
  page?: number;
  limit?: number;
}

type QueryValue = string | number | boolean | null | undefined;

export function listSchedules(filters: ScheduleFilters = {}) {
  return get<ScheduleWithSection[]>("/schedule", { query: filters as Record<string, QueryValue> });
}

export function getRooms() {
  return get<RoomOut[]>("/courses/rooms");
}

export function getCopyCount(semester = "2", academicYear = "2568") {
  return get<CopyCountSummary>("/schedule/copy-count", {
    query: { semester, academic_year: academicYear },
  });
}

export function updateSchedule(scheduleId: number, body: Record<string, unknown>) {
  return put(`/schedule/${scheduleId}`, body);
}

export function runOptimizer(body: {
  semester: string;
  academic_year: string;
  exam_type: string;
}) {
  return post("/schedule/optimize", body);
}
