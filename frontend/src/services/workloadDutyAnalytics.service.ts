import { get } from "./api";
import type { WorkloadDutyAnalyticsPayload, DutyType, WorkloadRoleGroup } from "../types/workloadDutyAnalytics";

export interface WorkloadDutyAnalyticsQuery {
  semester?: string | null;
  academic_year?: string | null;
  period_id?: number | null;
  exam_type?: string | null;
  role_group?: WorkloadRoleGroup;
  person_id?: string | null;
  include_teachers?: boolean;
  include_staff?: boolean;
  duty_type?: DutyType;
}

export function fetchWorkloadDutyAnalytics(query: WorkloadDutyAnalyticsQuery = {}): Promise<WorkloadDutyAnalyticsPayload> {
  const params: Record<string, string | number | boolean> = {
    role_group: query.role_group ?? "all",
    duty_type: query.duty_type ?? "all",
    include_teachers: query.include_teachers ?? true,
    include_staff: query.include_staff ?? true,
  };

  if (query.semester) params.semester = query.semester;
  if (query.academic_year) params.academic_year = query.academic_year;
  if (query.period_id) params.period_id = query.period_id;
  if (query.exam_type) params.exam_type = query.exam_type;
  if (query.person_id) params.person_id = query.person_id;

  return get<WorkloadDutyAnalyticsPayload>("/dashboard/workload-duty-analytics", { query: params });
}
