import { Band, getBandColor, getRiskBand } from "./bandPresenter";
import { getSeverityBadgeModel, getSeverityColorClass } from "./severityPresenter";

export interface MetricCardModel {
  label: string;
  value: number;
  key: string;
  suffix?: string;
}

export interface HealthScoreModel {
  score: number;
  band: Band | null;
  colorClass: string;
  labelKey: string;
}

export interface RiskBandModel {
  risk: string;
  severity: string;
  category: string;
  severityColor: string;
  severityModel: ReturnType<typeof getSeverityBadgeModel>;
}

export function buildMetricCardModel(
  label: string,
  value: number,
  key: string,
  suffix?: string,
): MetricCardModel {
  return { label, value, key, suffix };
}

export function buildHealthScoreModel(score: number | null | undefined): HealthScoreModel {
  const band = getRiskBand(score);
  const colorClass = getBandColor(band);
  return {
    score: score ?? 0,
    band,
    colorClass,
    labelKey: "analytics.healthScore",
  };
}

export function buildRiskBandModel(
  risk: string,
  severity: string,
  category: string,
): RiskBandModel {
  const severityModel = getSeverityBadgeModel(severity);
  return {
    risk,
    severity,
    category,
    severityColor: getSeverityColorClass(severity),
    severityModel,
  };
}

export interface TrendModel {
  direction: "up" | "down" | "stable";
  change: number;
  labelKey: string;
}

export function buildTrendModel(
  current: number,
  previous: number,
  labelKeyBase: string,
): TrendModel {
  const change = current - previous;
  const direction = change > 0 ? "up" : change < 0 ? "down" : "stable";
  return { direction, change: Math.abs(change), labelKey: `${labelKeyBase}.${direction}` };
}