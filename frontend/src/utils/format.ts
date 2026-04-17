import type { UserRole } from "@/types/api";

const thaiDate = new Intl.DateTimeFormat("th-TH", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

const thaiDateTime = new Intl.DateTimeFormat("th-TH", {
  day: "numeric",
  month: "short",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

const thaiCurrency = new Intl.NumberFormat("th-TH", {
  style: "currency",
  currency: "THB",
  maximumFractionDigits: 2,
});

const thaiNumber = new Intl.NumberFormat("th-TH");

export const ROLE_LABELS: Record<UserRole, string> = {
  admin: "Administrator",
  esq_head: "ESQ Head",
  secretary: "Secretary",
  dept_supervisor: "Department Supervisor",
  staff: "Staff",
  teacher: "Teacher",
  student: "Student",
  print_shop: "Print Shop",
};

export function formatDate(value?: string | null) {
  if (!value) return "-";
  return thaiDate.format(new Date(value));
}

export function formatDateTime(value?: string | null) {
  if (!value) return "-";
  return thaiDateTime.format(new Date(value));
}

export function formatNumber(value?: number | null) {
  if (value === null || value === undefined) return "-";
  return thaiNumber.format(value);
}

export function formatCurrency(value?: number | null) {
  if (value === null || value === undefined) return "-";
  return thaiCurrency.format(value);
}

export function formatRole(role?: UserRole | null) {
  return role ? ROLE_LABELS[role] : "-";
}

export function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(value)) return "-";
  return `${Math.round(value)}%`;
}

export function formatDateRange(date?: string | null, time?: string | null) {
  const datePart = formatDate(date);
  if (!time) return datePart;
  return `${datePart} at ${time}`;
}
