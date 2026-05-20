import React from "react";
import type { ReactNode } from "react";
import { getSeverityBadgeModel, getSeverityColorClass } from "./severityPresenter";

export interface AuditTimelineItem {
  _id: string;
  id: number | null;
  actor: string;
  action: string;
  table_name: string | null;
  timestamp: string;
  http_status: number | null;
}

export interface AuditEventBadgeModel {
  severity: string;
  colorClass: string;
  badgeModel: ReturnType<typeof getSeverityBadgeModel>;
}

export function buildAuditTimelineItem(raw: Record<string, unknown>): AuditTimelineItem {
  return {
    _id: String(raw.id ?? raw.timestamp ?? ""),
    id: (raw.id as number | null) ?? null,
    actor: String(raw.actor ?? "-"),
    action: String(raw.action ?? "-"),
    table_name: (raw.table_name as string | null) ?? null,
    timestamp: String(raw.timestamp ?? ""),
    http_status: (raw.http_status as number | null) ?? null,
  };
}

export function buildAuditEventBadgeModel(severity: string): AuditEventBadgeModel {
  const badgeModel = getSeverityBadgeModel(severity);
  return {
    severity,
    colorClass: getSeverityColorClass(severity),
    badgeModel,
  };
}

export interface RenderTabButtonOptions {
  active: boolean;
  onClick: () => void;
  label: string;
}

export function renderTabButton({ active, onClick, label }: RenderTabButtonOptions): ReactNode {
  const cls = active
    ? "border-blue-500 text-blue-600"
    : "border-transparent text-gray-500 hover:text-gray-700";
  return React.createElement(
    "button",
    {
      onClick,
      className: "px-4 py-2 text-sm font-medium border-b-2 " + cls,
    },
    label
  );
}