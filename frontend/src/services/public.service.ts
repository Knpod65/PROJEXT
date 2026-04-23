import type { PublicStudentSchedule } from "@/types/api";
import { get } from "./api";

export function getStudentSchedule(studentId: string) {
  return get<PublicStudentSchedule>(`/public/schedule/student/${encodeURIComponent(studentId)}`);
}

export function getPublicTimeline() {
  return get<Record<string, unknown>>("/public/timeline");
}
