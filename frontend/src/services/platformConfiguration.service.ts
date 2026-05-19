import { get, post } from "./api";

export interface PlatformConfigSnapshot {
  faculty_configs: unknown[];
  workload_policies: unknown[];
  governance_flows: unknown[];
  academic_group_configs: unknown[];
  role_mappings: unknown[];
  integration_contracts: unknown[];
  analytics_metrics: unknown[];
  export_metadata: {
    source: string;
    note: string;
  };
}

/**
 * Fetch the full platform configuration snapshot.
 * Admin-only endpoint. Returns empty arrays/lists for DB-backed config objects
 * that are not yet fully wired through the D3 config registry layer.
 */
export function getPlatformConfig() {
  return get<PlatformConfigSnapshot>("/admin/platform-config");
}
