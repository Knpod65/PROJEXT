import type { DashboardAnalytics, DashboardStats } from "@/types/api";
import { get } from "./api";

export function getDashboardStats(semester = "2", academicYear = "2568") {
  return get<DashboardStats>("/dashboard/", {
    query: { semester, academic_year: academicYear },
  });
}

export function getDashboardAnalytics(semester = "2", academicYear = "2568") {
  return get<DashboardAnalytics>("/dashboard/analytics", {
    query: { semester, academic_year: academicYear },
  });
}
