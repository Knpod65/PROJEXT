import { useState, useMemo } from "react";
import { useAuditEvents, useGovernanceTimeline, useLifecycleTimeline } from "@/hooks/useAuditExplorer";

export interface UseAuditExplorerReturn {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  auditEvents: Array<{ _id: string; id: number | null; actor: string; action: string; table_name: string | null; timestamp: string; http_status: number | null }>;
  governanceEvents: unknown[];
  lifecycleEvents: unknown[];
  isLoading: boolean;
  error: boolean;
  hasAuditData: boolean;
  hasGovernanceData: boolean;
  columnHeaders: Array<{ key: string; labelKey: string }>;
  tabKeys: Array<{ key: string; labelKey: string }>;
  emptyStateKey: string;
  errorAudit: unknown;
  errorGov: unknown;
  errorLifecycle: unknown;
  auditRaw: unknown;
  governanceRaw: unknown;
  lifecycleRaw: unknown;
}

const COLUMN_HEADERS = [
  { key: "id", labelKey: "auditEvents.col.id" },
  { key: "actor", labelKey: "auditEvents.col.actor" },
  { key: "action", labelKey: "auditEvents.col.action" },
  { key: "table", labelKey: "auditEvents.col.table" },
  { key: "time", labelKey: "auditEvents.col.time" },
];

const TAB_KEYS = [
  { key: "audit", labelKey: "auditEvents.tab" },
  { key: "governance", labelKey: "governanceTimeline.tab" },
  { key: "lifecycle", labelKey: "lifecycleTimeline.tab" },
];

export function useAuditExplorer(): UseAuditExplorerReturn {
  const [activeTab, setActiveTab] = useState<string>("audit");
  const { data: auditRaw, isLoading: loadingAudit, error: errorAudit } = useAuditEvents();
  const { data: governanceRaw, isLoading: loadingGov, error: errorGov } = useGovernanceTimeline();
  const { data: lifecycleRaw, isLoading: loadingLifecycle, error: errorLifecycle } = useLifecycleTimeline("");

  const isLoading = loadingAudit || loadingGov || loadingLifecycle;
  const error = !!errorAudit || !!errorGov || !!errorLifecycle;

  const auditEvents = useMemo(() => {
    const events = Array.isArray(auditRaw) ? auditRaw : [];
    return events.map((raw) => {
      const rec = { ...(raw as object) } as Record<string, unknown>;
      return {
        _id: String(rec.id ?? rec.timestamp ?? crypto.randomUUID()),
        id: (rec.id as number | null) ?? null,
        actor: String(rec.actor ?? "-"),
        action: String(rec.action ?? "-"),
        table_name: (rec.table_name as string | null) ?? null,
        timestamp: String(rec.timestamp ?? ""),
        http_status: (rec.http_status as number | null) ?? null,
      };
    });
  }, [auditRaw]);

  const governanceEvents = governanceRaw ?? [];
  const lifecycleEvents = lifecycleRaw ?? [];

  const hasAuditData = auditEvents.length > 0;
  const hasGovernanceData = Array.isArray(governanceRaw) && (governanceRaw as unknown[]).length > 0;
  const emptyStateKey = "auditEvents.noData";

  return {
    activeTab,
    setActiveTab,
    auditEvents,
    governanceEvents,
    lifecycleEvents,
    isLoading,
    error,
    hasAuditData,
    hasGovernanceData,
    columnHeaders: COLUMN_HEADERS,
    tabKeys: TAB_KEYS,
    emptyStateKey,
    errorAudit,
    errorGov,
    errorLifecycle,
    auditRaw,
    governanceRaw,
    lifecycleRaw,
  };
}
