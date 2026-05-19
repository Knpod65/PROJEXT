import { get } from "./api";

export interface AuditEvent {
  id: number;
  actor: string;
  action: string;
  table_name: string | null;
  record_id: number | null;
  timestamp: string;
  http_status: number | null;
}

export interface GovernanceEvent {
  id: number;
  actor: string;
  action: string;
  timestamp: string;
  detail: string;
}

export interface LifecycleEvent {
  id: number;
  event_type: string;
  timestamp: string;
  detail: string;
}

async function fetchAuditEvents(): Promise<AuditEvent[]> {
  const resp = await get<{ logs: AuditEvent[] }>("/exports/audit-logs?limit=50");
  return resp.logs;
}

async function fetchGovernanceTimeline(sessionId?: string): Promise<GovernanceEvent[]> {
  const url = sessionId ? `/analytics/governance-timeline?session_id=${sessionId}` : "/analytics/governance-timeline";
  return get<GovernanceEvent[]>(url);
}

async function fetchLifecycleTimeline(sessionId: string): Promise<LifecycleEvent[]> {
  return get<LifecycleEvent[]>(`/analytics/lifecycle-timeline/${sessionId}`);
}

export { fetchAuditEvents, fetchGovernanceTimeline, fetchLifecycleTimeline };