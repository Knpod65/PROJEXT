import { get, put } from "./api";

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
