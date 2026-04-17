import type { RoleSelectionValue, UserRole } from "@/types/api";

export type RoleEntryKey = RoleSelectionValue;

export interface RoleEntryDefinition {
  key: RoleEntryKey;
  title: string;
  eyebrow: string;
  description: string;
  icon: string;
  accentRole: UserRole;
  roles: UserRole[];
}

const roleEntries: RoleEntryDefinition[] = [
  {
    key: "admin",
    title: "Admin",
    eyebrow: "Authority",
    description: "System-wide configuration, institutional oversight, and administrative control.",
    icon: "admin_panel_settings",
    accentRole: "admin",
    roles: ["admin"],
  },
  {
    key: "teacher",
    title: "Teacher",
    eyebrow: "Growth",
    description: "Exam content, submissions, and teaching-side coordination for the active period.",
    icon: "school",
    accentRole: "teacher",
    roles: ["teacher"],
  },
  {
    key: "staff",
    title: "Staff",
    eyebrow: "Action",
    description: "Operational logistics, venue readiness, and room-side support workflows.",
    icon: "inventory",
    accentRole: "staff",
    roles: ["staff"],
  },
  {
    key: "governance",
    title: "ESQ Head / Secretary",
    eyebrow: "Formal Decision",
    description: "Shared governance and approval flow for final review, sign-off, and reporting.",
    icon: "gavel",
    accentRole: "esq_head",
    roles: ["esq_head", "secretary"],
  },
  {
    key: "dept_supervisor",
    title: "Dept Supervisor",
    eyebrow: "Oversight",
    description: "Departmental oversight, compliance pacing, and schedule-level supervision.",
    icon: "supervisor_account",
    accentRole: "dept_supervisor",
    roles: ["dept_supervisor"],
  },
  {
    key: "student",
    title: "Student Search",
    eyebrow: "Guest",
    description: "Student-facing exam lookup and schedule visibility for inquiry and support.",
    icon: "person_search",
    accentRole: "student",
    roles: ["student"],
  },
  {
    key: "print_shop",
    title: "Print Shop",
    eyebrow: "Logistics",
    description: "Dedicated print queue, dispatch tracking, and production-floor execution workspace.",
    icon: "print",
    accentRole: "print_shop",
    roles: ["print_shop"],
  },
];

export function getRoleSelectionEntries() {
  return roleEntries;
}

export function getRoleSelectionEntry(key: RoleSelectionValue | null | undefined) {
  if (!key) {
    return null;
  }

  return roleEntries.find((entry) => entry.key === key) ?? null;
}
