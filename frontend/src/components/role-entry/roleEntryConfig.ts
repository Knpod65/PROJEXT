import { translate } from "@/i18n";
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

const roleEntryDefinitions: Array<Omit<RoleEntryDefinition, "title" | "eyebrow" | "description">> = [
  {
    key: "admin",
    icon: "admin_panel_settings",
    accentRole: "admin",
    roles: ["admin"],
  },
  {
    key: "teacher",
    icon: "school",
    accentRole: "teacher",
    roles: ["teacher"],
  },
  {
    key: "staff",
    icon: "inventory",
    accentRole: "staff",
    roles: ["staff"],
  },
  {
    key: "governance",
    icon: "gavel",
    accentRole: "esq_head",
    roles: ["esq_head", "secretary"],
  },
  {
    key: "dept_supervisor",
    icon: "supervisor_account",
    accentRole: "dept_supervisor",
    roles: ["dept_supervisor"],
  },
  {
    key: "student",
    icon: "person_search",
    accentRole: "student",
    roles: ["student"],
  },
  {
    key: "print_shop",
    icon: "print",
    accentRole: "print_shop",
    roles: ["print_shop"],
  },
];

function localizeEntry(entry: Omit<RoleEntryDefinition, "title" | "eyebrow" | "description">): RoleEntryDefinition {
  return {
    ...entry,
    title: translate(`roleEntry.${entry.key}.title`),
    eyebrow: translate(`roleEntry.${entry.key}.eyebrow`),
    description: translate(`roleEntry.${entry.key}.description`),
  };
}

export function getRoleSelectionEntries() {
  return roleEntryDefinitions.map(localizeEntry);
}

export function getRoleSelectionEntry(key: RoleSelectionValue | null | undefined) {
  if (!key) {
    return null;
  }

  const entry = roleEntryDefinitions.find((candidate) => candidate.key === key) ?? null;
  return entry ? localizeEntry(entry) : null;
}
