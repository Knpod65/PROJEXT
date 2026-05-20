export function formatScore(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "-";
  return `${Math.round(value)}/100`;
}

export function formatPercentage(value: number | null | undefined, decimals: number = 0): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "-";
  return `${value.toFixed(decimals)}%`;
}

export function formatRatio(numerator: number, denominator: number, fallback: string = "—"): string {
  if (denominator <= 0) return fallback;
  return `${numerator}/${denominator}`;
}

export function formatCount(value: number | null | undefined, fallback: string = "0"): string {
  if (value === null || value === undefined || Number.isNaN(value)) return fallback;
  return String(value);
}

export function formatNullableNumber(value: number | null | undefined, fallback: string = "-"): string {
  if (value === null || value === undefined || Number.isNaN(value)) return fallback;
  return String(value);
}

export function formatMetricValue(value: number | null | undefined): string {
  if (value === null || value === undefined) return "-";
  return String(value);
}