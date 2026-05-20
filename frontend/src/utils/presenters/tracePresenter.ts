import { getSeverityBadgeModel, getSeverityColorClass } from "./severityPresenter";

export interface TraceTimelineItem {
  id: string;
  stage: string;
  event_type: string;
  severity: string;
  detail: string;
  timestamp: string;
  severityColor: string;
}

export interface TraceSeverityModel {
  severity: string;
  colorClass: string;
  badgeModel: ReturnType<typeof getSeverityBadgeModel>;
}

export function buildTraceTimelineItem(raw: {
  event_id: string;
  stage: string;
  event_type: string;
  severity: string;
  detail: string;
  timestamp: string;
}): TraceTimelineItem {
  return {
    id: raw.event_id,
    stage: raw.stage,
    event_type: raw.event_type,
    severity: raw.severity,
    detail: raw.detail,
    timestamp: raw.timestamp,
    severityColor: getSeverityColorClass(raw.severity),
  };
}

export function buildTraceSeverityModel(severity: string): TraceSeverityModel {
  const badgeModel = getSeverityBadgeModel(severity);
  return {
    severity,
    colorClass: getSeverityColorClass(severity),
    badgeModel,
  };
}

export interface RejectedAlternativeModel {
  id: string;
  score: number;
  reason?: string;
}

export function buildRejectedAlternativeModel(
  candidate: { id: string; score?: number; reason?: string },
  selected: boolean,
): RejectedAlternativeModel | null {
  if (selected) return null;
  return {
    id: candidate.id,
    score: candidate.score ?? 0,
    reason: candidate.reason,
  };
}