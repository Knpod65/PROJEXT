import { get } from "./api";
import type { MetricDefinition, MetricValueResponse, ExecutiveDashboardSummary } from "@/types/analytics";
import type { IntegrationContract } from "@/types/analytics";

export function listMetrics()                { return get<MetricDefinition[]>("/api/analytics/metrics"); }
export function getMetric(code: string)      { return get<MetricDefinition>(`/api/analytics/metrics/${code}`); }
export function getExecutiveSummary()        { return get<ExecutiveDashboardSummary>("/api/analytics/executive-summary"); }
export function listIntegrationContracts()   { return get<IntegrationContract[]>("/api/analytics/integration-contracts"); }