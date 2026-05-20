/** OPS-DASH: Admin Intelligence Dashboard service. */

import { get } from "./api";
import type {
  AdminIntelligenceDashboard,
  RoleDashboardPayload,
  OpsHealthPayload,
  PdpaHealthPayload,
  ExecDashboardPayload,
} from "../types/dashboardMetrics";

export function fetchAdminIntelligenceDashboard(
  semester = "2",
  academicYear = "2568",
): Promise<AdminIntelligenceDashboard> {
  return get<AdminIntelligenceDashboard>("/dashboard/admin-intelligence", {
    query: { semester, academic_year: academicYear },
  });
}

export function fetchRoleSummary(role?: string): Promise<RoleDashboardPayload> {
  const path = role ? `/dashboard/role-summary/${role}` : "/dashboard/role-summary";
  return get<RoleDashboardPayload>(path);
}

export function fetchOpsHealth(): Promise<OpsHealthPayload> {
  return get<OpsHealthPayload>("/dashboard/ops-health");
}

export function fetchPdpaHealth(): Promise<PdpaHealthPayload> {
  return get<PdpaHealthPayload>("/dashboard/pdpa-health");
}

export function fetchExecutiveSummary(
  semester = "2",
  academicYear = "2568",
): Promise<ExecDashboardPayload> {
  return get<ExecDashboardPayload>("/dashboard/executive-summary", {
    query: { semester, academic_year: academicYear },
  });
}
