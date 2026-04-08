import type { PeriodItem } from "@/types/api";
import { get, post } from "./api";

export function listPeriods() {
  return get<PeriodItem[]>("/period");
}

export function getActivePeriod() {
  return get<PeriodItem>("/period/active");
}

export function createPeriod(body: {
  academic_year: string;
  semester: string;
  exam_type: string;
  label?: string;
}) {
  return post<PeriodItem>("/period", body);
}

export function activatePeriod(periodId: number) {
  return post<{ status: string; active_period: PeriodItem }>(`/period/${periodId}/activate`);
}

export function rolloverPeriod(body: Record<string, unknown>) {
  return post("/period/rollover", body);
}
