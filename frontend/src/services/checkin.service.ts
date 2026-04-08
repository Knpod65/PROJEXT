import type { CheckinEventItem } from "@/types/api";
import { get, post } from "./api";

export function getCheckinsForSchedule(scheduleId: number) {
  return get<CheckinEventItem[]>(`/checkins/schedule/${scheduleId}`);
}

export function createCheckin(body: {
  schedule_id: number;
  checkin_type: string;
  students_present?: number;
  late_count?: number;
  absent_student_ids?: string[];
  notes?: string;
}) {
  return post<{ success: boolean; checkin_id: number }>("/checkins", body);
}

export function confirmCheckin(checkinId: number) {
  return post<{ success: boolean; confirmed_by_all: boolean }>("/checkins/confirm", {
    checkin_id: checkinId,
  });
}
