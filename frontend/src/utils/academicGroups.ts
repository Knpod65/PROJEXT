export type AcademicGroupCode = "IA" | "GOV" | "PA" | "STB" | "ALL";

const LEGACY_GROUP_ALIASES: Record<string, AcademicGroupCode> = {
  IR: "IA",
};

const PREFIX_TO_GROUP: Record<string, AcademicGroupCode> = {
  "126": "IA",
  "127": "GOV",
  "128": "PA",
  "131": "STB",
  "140": "ALL",
};

const GROUP_LABELS: Record<AcademicGroupCode, string> = {
  IA: "International Affairs",
  GOV: "Political Science",
  PA: "Public Administration",
  STB: "School of Sustainability",
  ALL: "Cross-group",
};

export function normalizeAcademicGroupCode(value?: string | null): AcademicGroupCode | null {
  if (!value) {
    return null;
  }
  const normalized = value.trim().toUpperCase();
  return LEGACY_GROUP_ALIASES[normalized] ?? (normalized in GROUP_LABELS ? (normalized as AcademicGroupCode) : null);
}

export function getAcademicGroupFromCourseId(courseId?: string | null): AcademicGroupCode | null {
  if (!courseId) {
    return null;
  }
  const digits = courseId.replace(/\D/g, "");
  return PREFIX_TO_GROUP[digits.slice(0, 3)] ?? null;
}

export function getAcademicGroupLabel(group?: string | null): string | null {
  const normalized = normalizeAcademicGroupCode(group);
  return normalized ? GROUP_LABELS[normalized] : null;
}
