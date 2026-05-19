import { get } from "./api";

/**
 * Call multiple health/integrity endpoints and return a unified summary.
 * All calls are fire-and-forget from the service perspective — the page
 * renders whatever succeeded and shows "—" for failures.
 */
export async function getOperationalHealth() {
  const [health, analytics] = await Promise.allSettled([
    get<{ status: string; service: string; timestamp: string }>("/health"),
    get<{ overall_health_score: number }>("/analytics/executive-summary"),
  ]);

  const healthData =
    health.status === "fulfilled" ? health.value : null;
  const analyticsData =
    analytics.status === "fulfilled" ? analytics.value : null;

  const integrationRaw = await get("/analytics/integration-contracts")
    .then((r: any) => r)
    .catch(() => null);

  const integrationActive = Array.isArray(integrationRaw)
    ? integrationRaw.filter((c: any) => c.status === "active").length
    : 0;
  const integrationTotal = Array.isArray(integrationRaw) ? integrationRaw.length : 0;

  return {
    backend_healthy: healthData?.status === "ok",
    health_timestamp: healthData?.timestamp ?? null,
    analytics_score: analyticsData?.overall_health_score ?? null,
    integration_active: integrationActive,
    integration_total: integrationTotal,
  };
}
