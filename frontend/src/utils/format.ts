import type { UserRole } from "@/types/api";
import { getCurrentLocale, translate, translateWithFallback } from "@/i18n";

function getDateFormatter(options: Intl.DateTimeFormatOptions) {
  return new Intl.DateTimeFormat(getCurrentLocale(), options);
}

function getNumberFormatter(options?: Intl.NumberFormatOptions) {
  return new Intl.NumberFormat(getCurrentLocale(), options);
}

export function formatDate(value?: string | null) {
  if (!value) return "-";
  return getDateFormatter({
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

export function formatDateTime(value?: string | null) {
  if (!value) return "-";
  return getDateFormatter({
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function formatNumber(value?: number | null) {
  if (value === null || value === undefined) return "-";
  return getNumberFormatter().format(value);
}

export function formatCurrency(value?: number | null) {
  if (value === null || value === undefined) return "-";
  return getNumberFormatter({
    style: "currency",
    currency: "THB",
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatRole(role?: UserRole | null) {
  return role ? translateWithFallback(`roles.${role}`, role) : "-";
}

export function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(value)) return "-";
  return `${Math.round(value)}%`;
}

export function formatDateRange(date?: string | null, time?: string | null) {
  const datePart = formatDate(date);
  if (!time) return datePart;
  return `${datePart} ${translate("common.dateConnectorAt")} ${time}`;
}

export function formatTranslatedValue(namespace: string, value?: string | null) {
  if (!value) {
    return "-";
  }

  return translateWithFallback(`${namespace}.${value}`, value);
}
