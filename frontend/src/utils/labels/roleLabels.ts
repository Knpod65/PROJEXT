import { translate } from "@/i18n";

export const roleLabels: Record<string, string> = {
  admin: translate("common.role.admin"),
  staff: translate("common.role.staff"),
  teacher: translate("common.role.teacher"),
  esq_head: translate("common.role.esq_head"),
  secretary: translate("common.role.secretary"),
  dept_supervisor: translate("common.role.dept_supervisor"),
};

export function getRoleLabel(role: string): string {
  return roleLabels[role] || role;
}
