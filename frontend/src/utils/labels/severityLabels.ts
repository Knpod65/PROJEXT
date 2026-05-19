import { translate } from "@/i18n";

export const severityLabels: Record<string, string> = {
  info: translate("severity.info"),
  warning: translate("severity.warning"),
  error: translate("severity.error"),
  critical: translate("severity.critical"),
  high: translate("severity.high"),
  medium: translate("severity.medium"),
  low: translate("severity.low"),
};

export function getSeverityLabel(severity: string): string {
  return severityLabels[severity] || severity;
}
