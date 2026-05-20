import { getStatusLabel } from "@/utils/labels/statusLabels";

export type StatusTone = "success" | "warning" | "error" | "info" | "neutral";

export interface StatusBadgeModel {
  label: string;
  tone: StatusTone;
  normalizedStatus: string;
  icon?: string;
}

export function getStatusTone(status: string): StatusTone {
  const toneMap: Record<string, StatusTone> = {
    active: "success",
    confirmed: "success",
    approved: "success",
    locked: "warning",
    draft: "neutral",
    submitted: "info",
    rejected: "error",
    blocked: "error",
    released: "success",
  };
  return toneMap[status] ?? "neutral";
}

export function getStatusBadgeModel(status: string): StatusBadgeModel {
  return {
    label: getStatusLabel(status),
    tone: getStatusTone(status),
    normalizedStatus: status,
  };
}

export function getLifecycleStatusModel(status: string): StatusBadgeModel {
  return getStatusBadgeModel(status);
}