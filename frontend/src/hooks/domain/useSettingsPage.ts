import { useCallback, useEffect, useState } from "react";
import { useAsyncData } from "@/hooks/useAsyncData";
import { translate } from "@/i18n";
import { listSettings, updateSetting, type SettingsMap, type SettingValue } from "@/services/settings.service";
import { useUi } from "@/store/ui.store";

export interface SettingsSection {
  key: string;
  value: string;
  description: string;
}

export interface UseSettingsPageReturn {
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  sections: SettingsSection[];
  drafts: Record<string, string>;
  updateDraft: (key: string, value: string) => void;
  save: (key: string) => Promise<void>;
  hasData: boolean;
}

export function useSettingsPage(): UseSettingsPageReturn {
  const { toast } = useUi();
  const loader = useCallback(() => listSettings(), []);
  const state = useAsyncData(loader, [loader]);
  const [drafts, setDrafts] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!state.data) return;
    const nextDrafts: Record<string, string> = {};
    Object.entries(state.data).forEach(([key, value]) => {
      nextDrafts[key] = value.value ?? "";
    });
    setDrafts(nextDrafts);
  }, [state.data]);

  const updateDraft = useCallback((key: string, value: string) => {
    setDrafts((current) => ({ ...current, [key]: value }));
  }, []);

  const save = useCallback(async (key: string) => {
    try {
      await updateSetting(key, drafts[key] ?? "");
      toast(translate("settings.saved"), "success");
      await state.reload();
    } catch (err) {
      toast(err instanceof Error ? err.message : translate("settings.saveFailed"), "error");
    }
  }, [drafts, state, toast]);

  const sections = Object.entries(state.data ?? {}).map(([key, value]: [string, SettingValue]) => ({
    key,
    value: value.value ?? "",
    description: value.description,
  }));

  return {
    isLoading: state.loading,
    error: state.error,
    refresh: state.reload,
    sections,
    drafts,
    updateDraft,
    save,
    hasData: Object.keys(state.data ?? {}).length > 0,
  };
}