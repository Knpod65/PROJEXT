import { useMemo, useState } from "react";

import { useAuth } from "@/store/auth.store";
import type { RoleTheme } from "@/theme/roleThemes";
import { getRoleTheme } from "@/theme/roleThemes";
import type { UserRole } from "@/types/api";
import { getEffectiveRole } from "@/utils/roles";

interface GeneralSettingsDraft {
  systemName: string;
  primaryContactEmail: string;
  supportPhone: string;
}

interface LocalizationSettingsDraft {
  language: string;
  timezone: string;
  dateFormat: string;
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

const roleDescriptions: Record<UserRole, string> = {
  admin: "Full institutional oversight and configuration control.",
  esq_head: "Executive quality and reporting perspective.",
  secretary: "Coordination desk and approval pacing view.",
  dept_supervisor: "Department-level supervision and readiness view.",
  staff: "Operations and logistics support perspective.",
  teacher: "Teaching and exam coordination perspective.",
  student: "Public-facing exam visibility perspective.",
  print_shop: "Dedicated production queue, dispatch, and printing workflow preview.",
};

const initialGeneralSettings: GeneralSettingsDraft = {
  systemName: "Editorial Authority EMS",
  primaryContactEmail: "admin@institution.edu",
  supportPhone: "+66 2 000 0000",
};

const initialLocalizationSettings: LocalizationSettingsDraft = {
  language: "Thai (Standard)",
  timezone: "(GMT+07:00) Bangkok, Hanoi, Jakarta",
  dateFormat: "DD MMM YYYY",
};

const initialAccessSettings: AccessSettingsDraft = {
  mfaEnabled: true,
  sessionTimeoutMinutes: 45,
  allowPreviewNotifications: true,
};

export function useSettingsData() {
  const { switchViewAs, user } = useAuth();
  const activeRole = getEffectiveRole(user);
  const activeTheme = getRoleTheme(activeRole);
  const [generalSettings, setGeneralSettings] = useState(initialGeneralSettings);
  const [localizationSettings, setLocalizationSettings] = useState(initialLocalizationSettings);
  const [accessSettings, setAccessSettings] = useState(initialAccessSettings);

  const viewAsOptions = useMemo<ViewAsOption[]>(
    () =>
      previewRoles.map((role) => ({
        role,
        label: getRoleTheme(role).label,
        description: roleDescriptions[role],
        theme: getRoleTheme(role),
        active: activeRole === role,
      })),
    [activeRole],
  );

  const updateGeneralSetting = <Key extends keyof GeneralSettingsDraft>(key: Key, value: GeneralSettingsDraft[Key]) => {
    setGeneralSettings((current) => ({ ...current, [key]: value }));
  };

  const updateLocalizationSetting = <Key extends keyof LocalizationSettingsDraft>(
    key: Key,
    value: LocalizationSettingsDraft[Key],
  ) => {
    setLocalizationSettings((current) => ({ ...current, [key]: value }));
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
