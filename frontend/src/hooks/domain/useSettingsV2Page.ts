import { useCallback } from "react";
import { useSettingsData, type ViewAsOption } from "@/hooks/useSettingsData";
import { translate } from "@/i18n";
import { useUi } from "@/store/ui.store";
import { formatRole } from "@/utils/format";
import type { UserRole } from "@/types/api";

export interface GeneralSettingsDraft {
  systemName: string;
  primaryContactEmail: string;
  supportPhone: string;
}

export interface LocalizationSettingsDraft {
  language: "th" | "en";
  timezone: "bangkok" | "utc";
  dateFormat: "compact" | "iso";
}

export interface AccessSettingsDraft {
  mfaEnabled: boolean;
  sessionTimeoutMinutes: number;
  allowPreviewNotifications: boolean;
}

export interface UseSettingsV2PageReturn {
  isLoading: boolean;
  generalSettings: GeneralSettingsDraft;
  accessSettings: AccessSettingsDraft;
  localizationSettings: LocalizationSettingsDraft;
  activeRole: UserRole | null;
  activeTheme: ReturnType<typeof useSettingsData>["activeTheme"];
  viewAsOptions: ViewAsOption[];
  updateGeneralSetting: ReturnType<typeof useSettingsData>["updateGeneralSetting"];
  updateLocalizationSetting: ReturnType<typeof useSettingsData>["updateLocalizationSetting"];
  updateAccessSetting: ReturnType<typeof useSettingsData>["updateAccessSetting"];
  handleSaveDraft: (label: string) => void;
  handleSwitchViewAs: (role: UserRole) => Promise<void>;
  handleResetViewAs: () => Promise<void>;
}

export function useSettingsV2Page(): UseSettingsV2PageReturn {
  const { toast } = useUi();
  const settingsData = useSettingsData();

  const handleSaveDraft = useCallback((label: string) => {
    toast(translate("settings.toastSaved", { label }), "success");
  }, [toast]);

  const handleSwitchViewAs = useCallback(async (role: UserRole) => {
    try {
      await settingsData.switchViewAs(role);
      toast(translate("settings.viewAsSwitched", { role: formatRole(role) }), "info");
    } catch (error) {
      toast(error instanceof Error ? error.message : translate("errors.switchViewAs"), "error");
    }
  }, [settingsData, toast]);

  const handleResetViewAs = useCallback(async () => {
    try {
      await settingsData.resetViewAs();
      toast(translate("settings.viewAsReset"), "info");
    } catch (error) {
      toast(error instanceof Error ? error.message : translate("errors.resetViewAs"), "error");
    }
  }, [settingsData, toast]);

  return {
    isLoading: false,
    ...settingsData,
    handleSaveDraft,
    handleSwitchViewAs,
    handleResetViewAs,
  };
}