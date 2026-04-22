import { get, post, put } from "./api";
import type {
  PeriodCloseResponse,
  RetentionPolicy,
  RetentionPolicyUpdateInput,
  TermSettingsPreview,
} from "@/types/api";

export interface SettingValue {
  value: string | null;
  description: string;
  updated_at: string | null;
}

export type SettingsMap = Record<string, SettingValue>;

export function listSettings() {
  return get<SettingsMap>("/settings");
}

export function updateSetting(key: string, value: string) {
  return put<{ key: string; value: string; updated: boolean }>(`/settings/${key}`, undefined, {
    query: { value },
  });
}

export function getTermPreview(periodId?: number) {
  return get<TermSettingsPreview>("/settings/term-preview", {
    query: { period_id: periodId },
  });
}

export function closeTerm(periodId: number) {
  return post<PeriodCloseResponse>(`/period/${periodId}/close`);
}

export function getRetentionPolicy() {
  return get<RetentionPolicy>("/settings/retention-policy");
}

export function updateRetentionPolicy(payload: RetentionPolicyUpdateInput) {
  return put<RetentionPolicy>("/settings/retention-policy", payload);
}
