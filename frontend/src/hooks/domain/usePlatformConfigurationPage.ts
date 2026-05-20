import { useMemo } from "react";
import { usePlatformConfig } from "@/hooks/usePlatformConfig";
import { translate } from "@/i18n";
import type { PlatformConfigSnapshot } from "@/services/platformConfiguration.service";

export interface UsePlatformConfigurationPageReturn {
  isLoading: boolean;
  error: unknown;
  refresh: () => void;
  data: PlatformConfigSnapshot | undefined;
  facultyConfigs: unknown[];
  workloadPolicies: unknown[];
  governanceFlows: unknown[];
  integrationContracts: unknown[];
  analyticsMetrics: unknown[];
  facultyHeaders: string[];
  workloadHeaders: string[];
  governanceHeaders: string[];
  integrationHeaders: string[];
  analyticsHeaders: string[];
  emptyStateKey: string;
}

export function usePlatformConfigurationPage(): UsePlatformConfigurationPageReturn {
  const { data, isLoading, error, refetch } = usePlatformConfig();

  const facultyConfigs = data?.faculty_configs ?? [];
  const workloadPolicies = (data as any)?.workload_policies ?? [];
  const governanceFlows = (data as any)?.governance_flows ?? [];
  const integrationContracts = (data as any)?.integration_contracts ?? [];
  const analyticsMetrics = (data as any)?.analytics_metrics ?? [];

  const facultyHeaders = useMemo(() => [
    translate("platformConfig.table.id"),
    translate("platformConfig.table.code"),
    translate("platformConfig.table.name"),
    translate("platformConfig.table.nameTh"),
    translate("platformConfig.table.nameEn"),
    translate("platformConfig.table.active"),
  ], []);

  const workloadHeaders = useMemo(() => [
    translate("platformConfig.table.facultyId"),
    translate("platformConfig.table.division"),
    translate("platformConfig.table.maxSupervision"),
    translate("platformConfig.table.crossDept"),
  ], []);

  const governanceHeaders = useMemo(() => [
    translate("platformConfig.table.facultyId"),
    translate("platformConfig.table.flowName"),
    translate("platformConfig.table.requiresReview"),
    translate("platformConfig.table.quorum"),
  ], []);

  const integrationHeaders = useMemo(() => [
    translate("platformConfig.table.system"),
    translate("platformConfig.table.direction"),
    translate("platformConfig.table.domain"),
    translate("platformConfig.table.syncMode"),
    translate("platformConfig.table.ownerUnit"),
  ], []);

  const analyticsHeaders = useMemo(() => [
    translate("platformConfig.table.code"),
    translate("platformConfig.table.name"),
    translate("platformConfig.table.category"),
    translate("platformConfig.table.unit"),
    translate("platformConfig.table.pdpaLevel"),
  ], []);

  return {
    isLoading,
    error,
    refresh: () => void refetch(),
    data,
    facultyConfigs,
    workloadPolicies,
    governanceFlows,
    integrationContracts,
    analyticsMetrics,
    facultyHeaders,
    workloadHeaders,
    governanceHeaders,
    integrationHeaders,
    analyticsHeaders,
    emptyStateKey: "platformConfig.noData",
  };
}