import type { CSSProperties } from "react";

import { translate } from "@/i18n";
import type { UserRole } from "@/types/api";

export interface RoleTheme {
  role: UserRole;
  label: string;
  shellTitle: string;
  shellSubtitle: string;
  badgeLabel: string;
  brandIcon: string;
  accent: string;
  accentStrong: string;
  accentSoft: string;
  accentText: string;
  sidebarBg: string;
  sidebarSurface: string;
  sidebarBorder: string;
  sidebarText: string;
  sidebarMuted: string;
  canvasGlow: string;
}

interface RoleThemeDefinition extends Omit<RoleTheme, "label" | "shellTitle" | "shellSubtitle" | "badgeLabel"> {}

const roleThemes: Record<UserRole, RoleThemeDefinition> = {
  admin: {
    role: "admin",
    brandIcon: "account_balance",
    accent: "#1f4d8f",
    accentStrong: "#173867",
    accentSoft: "rgba(31, 77, 143, 0.14)",
    accentText: "#173867",
    sidebarBg: "#f4f7fb",
    sidebarSurface: "#ffffff",
    sidebarBorder: "#d9e3f0",
    sidebarText: "#1f2937",
    sidebarMuted: "#6b7280",
    canvasGlow: "rgba(31, 77, 143, 0.14)",
  },
  esq_head: {
    role: "esq_head",
    brandIcon: "gavel",
    accent: "#8b3a3a",
    accentStrong: "#6d2d2d",
    accentSoft: "rgba(139, 58, 58, 0.14)",
    accentText: "#6d2d2d",
    sidebarBg: "#fbf5f5",
    sidebarSurface: "#ffffff",
    sidebarBorder: "#ead8d8",
    sidebarText: "#4a1f1f",
    sidebarMuted: "#6b7280",
    canvasGlow: "rgba(139, 58, 58, 0.14)",
  },
  secretary: {
    role: "secretary",
    brandIcon: "gavel",
    accent: "#1f7a74",
    accentStrong: "#185f5b",
    accentSoft: "rgba(31, 122, 116, 0.14)",
    accentText: "#185f5b",
    sidebarBg: "#f2fbfa",
    sidebarSurface: "#ffffff",
    sidebarBorder: "#d5ece9",
    sidebarText: "#134e4a",
    sidebarMuted: "#64748b",
    canvasGlow: "rgba(31, 122, 116, 0.12)",
  },
  dept_supervisor: {
    role: "dept_supervisor",
    brandIcon: "supervisor_account",
    accent: "#7a4bb7",
    accentStrong: "#603993",
    accentSoft: "rgba(122, 75, 183, 0.14)",
    accentText: "#603993",
    sidebarBg: "#f8f5ff",
    sidebarSurface: "#ffffff",
    sidebarBorder: "#e6dbf7",
    sidebarText: "#3b0764",
    sidebarMuted: "#6b7280",
    canvasGlow: "rgba(122, 75, 183, 0.12)",
  },
  staff: {
    role: "staff",
    brandIcon: "badge",
    accent: "#c97a1c",
    accentStrong: "#9e5f16",
    accentSoft: "rgba(201, 122, 28, 0.16)",
    accentText: "#9e5f16",
    sidebarBg: "#fcf7ef",
    sidebarSurface: "#ffffff",
    sidebarBorder: "#efdfc7",
    sidebarText: "#422006",
    sidebarMuted: "#78716c",
    canvasGlow: "rgba(201, 122, 28, 0.14)",
  },
  teacher: {
    role: "teacher",
    brandIcon: "school",
    accent: "#2f855a",
    accentStrong: "#256947",
    accentSoft: "rgba(47, 133, 90, 0.14)",
    accentText: "#256947",
    sidebarBg: "#f2fbf7",
    sidebarSurface: "#ffffff",
    sidebarBorder: "#d8ede1",
    sidebarText: "#064e3b",
    sidebarMuted: "#6b7280",
    canvasGlow: "rgba(47, 133, 90, 0.12)",
  },
  student: {
    role: "student",
    brandIcon: "person_search",
    accent: "#475569",
    accentStrong: "#334155",
    accentSoft: "rgba(71, 85, 105, 0.14)",
    accentText: "#334155",
    sidebarBg: "#f8fafc",
    sidebarSurface: "#ffffff",
    sidebarBorder: "#e2e8f0",
    sidebarText: "#0f172a",
    sidebarMuted: "#64748b",
    canvasGlow: "rgba(71, 85, 105, 0.1)",
  },
  print_shop: {
    role: "print_shop",
    brandIcon: "print",
    accent: "#5a6b83",
    accentStrong: "#455365",
    accentSoft: "rgba(90, 107, 131, 0.14)",
    accentText: "#455365",
    sidebarBg: "#f7f9fc",
    sidebarSurface: "#ffffff",
    sidebarBorder: "#d9e1ea",
    sidebarText: "#0f172a",
    sidebarMuted: "#64748b",
    canvasGlow: "rgba(90, 107, 131, 0.12)",
  },
};

const fallbackTheme = roleThemes.admin;

export function getRoleTheme(role?: UserRole | null) {
  const theme = role ? roleThemes[role] ?? fallbackTheme : fallbackTheme;

  return {
    ...theme,
    label: translate(`roles.${theme.role}`),
    shellTitle: translate(`roleThemes.${theme.role}.shellTitle`),
    shellSubtitle: translate(`roleThemes.${theme.role}.shellSubtitle`),
    badgeLabel: translate(`roleThemes.${theme.role}.badgeLabel`),
  };
}

export function getRoleThemeStyle(theme: RoleTheme) {
  return {
    "--role-accent": theme.accent,
    "--role-accent-strong": theme.accentStrong,
    "--role-accent-soft": theme.accentSoft,
    "--role-accent-text": theme.accentText,
    "--role-sidebar-bg": theme.sidebarBg,
    "--role-sidebar-surface": theme.sidebarSurface,
    "--role-sidebar-border": theme.sidebarBorder,
    "--role-sidebar-text": theme.sidebarText,
    "--role-sidebar-muted": theme.sidebarMuted,
    "--role-canvas-glow": theme.canvasGlow,
  } as CSSProperties;
}
