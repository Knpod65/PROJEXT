import { translate } from "@/i18n";

export const statusLabels: Record<string, string> = {
  draft: translate("status.draft"),
  submitted: translate("status.submitted"),
  approved: translate("status.approved"),
  rejected: translate("status.rejected"),
  released: translate("status.released"),
  locked: translate("status.locked"),
  swap_open: translate("status.swap_open"),
  confirmed: translate("status.confirmed"),
};

export function getStatusLabel(status: string): string {
  return statusLabels[status] || status;
}
