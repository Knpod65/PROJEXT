import { useEffect, useMemo, useState } from "react";

import { type AppLanguage, useI18n } from "@/i18n";
import { useEffectiveRole } from "@/hooks/useEffectiveRole";
import { useAuth } from "@/store/auth.store";
import type { RoleTheme } from "@/theme/roleThemes";
import { getRoleTheme } from "@/theme/roleThemes";
import type { UserRole } from "@/types/api";

interface GeneralSettingsDraft {
  systemName: string;
  primaryContactEmail: string;
  supportPhone: string;
}

interface LocalizationSettingsDraft {
  language: AppLanguage;
  timezone: "bangkok" | "utc";
  dateFormat: "compact" | "iso";
}

interface AccessSettingsDraft {
  mfaEnabled: boolean;
  sessionTimeoutMinutes: number;
  allowPreviewNotifications: boolean;
}

export interface ViewAsOption {
  role: UserRole;
  label: string;
  description: string;
  theme: RoleTheme;
  active: boolean;
}

const previewRoles: UserRole[] = ["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher", "student", "print_shop"];

const initialGeneralSettings: GeneralSettingsDraft = {
  systemName: "Editorial Authority EMS",
  primaryContactEmail: "admin@institution.edu",
  supportPhone: "+66 2 000 0000",
};

const initialAccessSettings: AccessSettingsDraft = {
  mfaEnabled: true,
  sessionTimeoutMinutes: 45,
  allowPreviewNotifications: true,
};

export function useSettingsData() {
  const { language, setLanguage, t } = useI18n();
  const { switchViewAs, user } = useAuth();
  const activeRole = useEffectiveRole();
  const activeTheme = getRoleTheme(activeRole);
  const [generalSettings, setGeneralSettings] = useState(initialGeneralSettings);
  const [localizationSettings, setLocalizationSettings] = useState<LocalizationSettingsDraft>({
    language,
    timezone: "bangkok",
    dateFormat: "compact",
  });
  const [accessSettings, setAccessSettings] = useState(initialAccessSettings);

  useEffect(() => {
    setLocalizationSettings((current) => ({ ...current, language }));
  }, [language]);

  const viewAsOptions = useMemo<ViewAsOption[]>(
    () =>
      previewRoles.map((role) => ({
        role,
        label: getRoleTheme(role).label,
        description: t(`settings.previewRole.${role}`),
        theme: getRoleTheme(role),
        active: activeRole === role,
      })),
    [activeRole, t],
  );

  const updateGeneralSetting = <Key extends keyof GeneralSettingsDraft>(key: Key, value: GeneralSettingsDraft[Key]) => {
    setGeneralSettings((current) => ({ ...current, [key]: value }));
  };

  const updateLocalizationSetting = <Key extends keyof LocalizationSettingsDraft>(
    key: Key,
    value: LocalizationSettingsDraft[Key],
  ) => {
    setLocalizationSettings((current) => ({ ...current, [key]: value }));

    if (key === "language") {
      setLanguage(value as AppLanguage);
    }
  };

  const updateAccessSetting = <Key extends keyof AccessSettingsDraft>(key: Key, value: AccessSettingsDraft[Key]) => {
    setAccessSettings((current) => ({ ...current, [key]: value }));
  };

  return {
    activeRole,
    activeTheme,
    accessSettings,
    generalSettings,
    localizationSettings,
    resetViewAs: () => switchViewAs(null),
    switchViewAs,
    updateAccessSetting,
    updateGeneralSetting,
    updateLocalizationSetting,
    viewAsOptions,
  };
}
