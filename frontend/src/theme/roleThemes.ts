import type { CSSProperties } from "react";

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

const roleThemes: Record<UserRole, RoleTheme> = {
  admin: {
    role: "admin",
    label: "Admin",
    shellTitle: "Admin Master",
    shellSubtitle: "Institutional oversight and exam command",
    badgeLabel: "ADMIN",
    brandIcon: "account_balance",
    accent: "#0d6efd",
    accentStrong: "#004cb6",
    accentSoft: "rgba(13, 110, 253, 0.14)",
    accentText: "#0f4eb3",
    sidebarBg: "#f6f3f2",
    sidebarSurface: "#ffffff",
    sidebarBorder: "#e4e2e2",
    sidebarText: "#1f2937",
    sidebarMuted: "#6b7280",
    canvasGlow: "rgba(13, 110, 253, 0.12)",
  },
  esq_head: {
    role: "esq_head",
    label: "ESQ Head",
    shellTitle: "Governance Desk",
    shellSubtitle: "Institutional approvals, registry checks, and final visibility",
    badgeLabel: "ESQ HEAD",
    brandIcon: "gavel",
    accent: "#4f46e5",
    accentStrong: "#3730a3",
    accentSoft: "rgba(79, 70, 229, 0.14)",
    accentText: "#4338ca",
    sidebarBg: "#f5f5ff",
    sidebarSurface: "#ffffff",
    sidebarBorder: "#dadcff",
    sidebarText: "#1e1b4b",
    sidebarMuted: "#6b7280",
    canvasGlow: "rgba(79, 70, 229, 0.12)",
  },
  secretary: {
    role: "secretary",
    label: "Secretary",
    shellTitle: "Governance Desk",
    shellSubtitle: "Institutional approvals, registry checks, and final visibility",
    badgeLabel: "SECRETARY",
    brandIcon: "gavel",
    accent: "#0f766e",
    accentStrong: "#115e59",
    accentSoft: "rgba(15, 118, 110, 0.14)",
    accentText: "#0f766e",
    sidebarBg: "#f1fbfa",
    sidebarSurface: "#ffffff",
    sidebarBorder: "#d6eeec",
    sidebarText: "#134e4a",
    sidebarMuted: "#64748b",
    canvasGlow: "rgba(15, 118, 110, 0.12)",
  },
  dept_supervisor: {
    role: "dept_supervisor",
    label: "Department Supervisor",
    shellTitle: "Department Oversight",
    shellSubtitle: "Faculty coverage, compliance, and session visibility",
    badgeLabel: "SUPERVISOR",
    brandIcon: "supervisor_account",
    accent: "#7c3aed",
    accentStrong: "#6d28d9",
    accentSoft: "rgba(124, 58, 237, 0.14)",
    accentText: "#6d28d9",
    sidebarBg: "#f8f5ff",
    sidebarSurface: "#ffffff",
    sidebarBorder: "#e9ddff",
    sidebarText: "#3b0764",
    sidebarMuted: "#6b7280",
    canvasGlow: "rgba(124, 58, 237, 0.12)",
  },
  staff: {
    role: "staff",
    label: "Staff",
    shellTitle: "Staff Portal",
    shellSubtitle: "Logistics, venue coverage, and room operations",
    badgeLabel: "STAFF",
    brandIcon: "badge",
    accent: "#f59e0b",
    accentStrong: "#d97706",
    accentSoft: "rgba(245, 158, 11, 0.16)",
    accentText: "#b45309",
    sidebarBg: "#fbf7ef",
    sidebarSurface: "#ffffff",
    sidebarBorder: "#f0e6cf",
    sidebarText: "#422006",
    sidebarMuted: "#78716c",
    canvasGlow: "rgba(245, 158, 11, 0.14)",
  },
  teacher: {
    role: "teacher",
    label: "Teacher",
    shellTitle: "Editorial Authority",
    shellSubtitle: "Teaching duties, submissions, and exam coordination",
    badgeLabel: "TEACHER",
    brandIcon: "school",
    accent: "#059669",
    accentStrong: "#047857",
    accentSoft: "rgba(5, 150, 105, 0.14)",
    accentText: "#047857",
    sidebarBg: "#f2fbf7",
    sidebarSurface: "#ffffff",
    sidebarBorder: "#d6efe4",
    sidebarText: "#064e3b",
    sidebarMuted: "#6b7280",
    canvasGlow: "rgba(5, 150, 105, 0.12)",
  },
  student: {
    role: "student",
    label: "Student",
    shellTitle: "Student Search",
    shellSubtitle: "Exam lookup and session visibility",
    badgeLabel: "STUDENT",
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
    label: "Print Shop",
    shellTitle: "Editorial Ops",
    shellSubtitle: "Queue orchestration, dispatch, and production tracking",
    badgeLabel: "PRINT SHOP",
    brandIcon: "print",
    accent: "#475569",
    accentStrong: "#334155",
    accentSoft: "rgba(71, 85, 105, 0.14)",
    accentText: "#334155",
    sidebarBg: "#f7f8fb",
    sidebarSurface: "#ffffff",
    sidebarBorder: "#dde3ea",
    sidebarText: "#0f172a",
    sidebarMuted: "#64748b",
    canvasGlow: "rgba(71, 85, 105, 0.12)",
  },
};

const fallbackTheme = roleThemes.admin;

export function getRoleTheme(role?: UserRole | null) {
  if (!role) {
    return fallbackTheme;
  }

  return roleThemes[role] ?? fallbackTheme;
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
