export type Band = "green" | "amber" | "red";

export function getBandColor(band: Band | null | undefined): string {
  if (!band) return "bg-green-100 text-green-800";
  return band === "green"
    ? "bg-green-100 text-green-800"
    : band === "amber"
      ? "bg-yellow-100 text-yellow-800"
      : "bg-red-100 text-red-800";
}

export function getRiskBand(score: number | null | undefined): Band | null {
  if (score === null || score === undefined) return null;
  return score >= 75 ? "green" : score >= 50 ? "amber" : "red";
}

export function getSeverityBandColor(severity: string): string {
  return severity === "high"
    ? "bg-red-100 text-red-800"
    : severity === "medium"
      ? "bg-yellow-100 text-yellow-800"
      : "bg-green-100 text-green-800";
}

export function getPriorityBandColor(priority: string): string {
  return priority === "high"
    ? "bg-red-100 text-red-800"
    : priority === "medium"
      ? "bg-yellow-100 text-yellow-800"
      : "bg-green-100 text-green-800";
}

export interface BandModel {
  band: Band | null;
  colorClass: string;
  labelKey: string;
}

export function buildBandModel(
  band: Band | null | undefined,
  labelKeyBase: string,
): BandModel {
  const safeBand = band ?? "green";
  return {
    band: band ?? null,
    colorClass: getBandColor(safeBand),
    labelKey: `${labelKeyBase}.${safeBand}`,
  };
}