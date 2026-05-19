/**
 * D3.9 — Platform config types and utilities for multi-faculty configuration.
 * Additive layer — no existing services modified.
 */

export interface FacultyConfig {
  faculty_id: number;
  code: string;
  name_th: string;
  name_en: string;
  email_domain: string;
  timezone: string;
  academic_year_default: string;
  semester_default: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
}

export interface GovernanceFlowSummary {
  faculty_id: number | null;
  flow_name: string;
  round_1_signer_count: number;
  round_2_signer_count: number;
  requires_governance_review: boolean;
  approval_quorum: number;
}

export interface WorkloadPolicySummary {
  faculty_id: number | null;
  excluded_username_count: number;
  excluded_division_count: number;
  max_supervision_sessions: number;
  allow_cross_department: boolean;
}

export function getFacultyDisplayName(
  config: FacultyConfig | null | undefined,
  lang: "th" | "en" = "th",
): string {
  if (!config) return "—";
  return lang === "en" ? config.name_en || "—" : config.name_th || "—";
}

export function formatAcademicPeriod(
  config: FacultyConfig | null | undefined,
): string {
  if (!config) return "—";
  const year = config.academic_year_default;
  const semester = config.semester_default;
  if (!year || !semester) return "—";
  return `${year}/${semester}`;
}
