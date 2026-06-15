import { translateWithFallback } from "@/i18n";
import type { StatusTone } from "@/components/ui/StatusChip";

const SUCCESS = new Set(["active", "approved", "available", "completed", "confirmed", "connected", "ready", "published", "passed"]);
const INFORMATION = new Set(["assigned", "escalated", "in_progress", "open", "review", "under_review"]);
const WARNING = new Set(["attention", "occupied", "pending", "revision", "revisions_requested", "waiting"]);
const DANGER = new Set(["cancelled", "critical", "disconnected", "error", "failed", "high", "maintenance", "rejected"]);
const BLOCKED = new Set(["blocked", "hold", "locked"]);
const DRAFT = new Set(["draft", "draft_config", "draft_not_authorized", "preview_only"]);
const READ_ONLY = new Set(["read_only", "readonly"]);

function normalize(value?: string | null) {
  return value?.trim().toLowerCase().replace(/[\s-]+/g, "_") ?? "";
}

function humanize(value: string) {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function statusTone(value?: string | null): StatusTone {
  const status = normalize(value);
  if (SUCCESS.has(status)) return "success";
  if (INFORMATION.has(status)) return "information";
  if (WARNING.has(status)) return "warning";
  if (DANGER.has(status)) return "danger";
  if (BLOCKED.has(status)) return "blocked";
  if (DRAFT.has(status)) return "draft";
  if (READ_ONLY.has(status)) return "readOnly";
  return "neutral";
}

export function statusLabel(value?: string | null) {
  if (!value) return "-";
  const status = normalize(value);
  return translateWithFallback(`status.${status}`, humanize(status));
}
