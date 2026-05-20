import { getSeverityLabel } from "@/utils/labels/severityLabels";

export type SeverityLevel = "critical" | "error" | "warning" | "info" | "high" | "medium" | "low";

export interface SeverityBadgeModel {
  label: string;
  colorClass: string;
  severity: string;
}

export function getSeverityTone(severity: string): "critical" | "error" | "warning" | "info" {
  const toneMap: Record<string, "critical" | "error" | "warning" | "info"> = {
    critical: "critical",
    error: "error",
    warning: "warning",
    info: "info",
    high: "error",
    medium: "warning",
    low: "info",
  };
  return toneMap[severity] ?? "info";
}

export function getSeverityBadgeModel(severity: string): SeverityBadgeModel {
  return {
    label: getSeverityLabel(severity),
    colorClass: getSeverityColorClass(severity),
    severity,
  };
}

export function getSeverityColorClass(severity: string): string {
  return severity === "critical"
    ? "bg-red-200 text-red-900"
    : severity === "error" || severity === "high"
      ? "bg-red-100 text-red-800"
      : severity === "warning" || severity === "medium"
        ? "bg-yellow-100 text-yellow-800"
        : "bg-blue-100 text-blue-800";
}

export function normalizeSeverity(severity: string | null | undefined): string {
  if (!severity) return "info";
  const lower = severity.toLowerCase();
  if (["critical", "high"].includes(lower)) return "high";
  if (["error", "warning", "medium"].includes(lower)) return "medium";
  return "low";
}