import { formatDate, formatDateTime } from "@/utils/format";

export function formatDisplayDate(value: string | null | undefined): string {
  return formatDate(value);
}

export function formatDisplayDateTime(value: string | null | undefined): string {
  return formatDateTime(value);
}

export function formatDateRange(date?: string | null, time?: string | null): string {
  if (!date) return "-";
  const datePart = formatDisplayDate(date);
  if (!time) return datePart;
  return `${datePart} ${time}`;
}

export function formatNullableDate(value: string | null | undefined, fallback: string = "-"): string {
  if (!value) return fallback;
  try {
    return formatDate(value);
  } catch {
    return fallback;
  }
}