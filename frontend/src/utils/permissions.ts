/**
 * permissions.ts — Semantic frontend permission helpers.
 *
 * Mirrors backend services/permission_service.py at the UI layer.
 * All helpers accept a UserMe | null and return boolean.
 *
 * Usage:
 *   import { canManageUsers, canViewAll } from "@/utils/permissions";
 *   if (canManageUsers(user)) { ... }
 *
 * Rules:
 *   - Use getEffectiveRole() — respects admin view_as impersonation.
 *   - Never check role strings inline in pages; call these helpers.
 *   - Extend here, not in individual page files.
 */

import type { UserMe, UserRole } from "@/types/api";
import { getEffectiveRole, getBaseRole } from "@/utils/roles";

// ── Internal helpers ────────────────────────────────────────────

function role(user: UserMe | null | undefined): UserRole | null {
  return getEffectiveRole(user);
}

function hasAnyRole(
  user: UserMe | null | undefined,
  ...roles: UserRole[]
): boolean {
  const r = role(user);
  return r !== null && roles.includes(r);
}

// ── User management ─────────────────────────────────────────────

/** Create, edit, deactivate users. Admin only. */
export function canManageUsers(user: UserMe | null | undefined): boolean {
  return role(user) === "admin";
}

/** View the full user directory. */
export function canViewUserList(user: UserMe | null | undefined): boolean {
  return hasAnyRole(user, "admin", "esq_head", "secretary");
}

/**
 * Admin impersonation (view_as_role). Requires the *real* base role to be
 * admin — not an impersonated admin session.
 */
export function canUseViewAs(user: UserMe | null | undefined): boolean {
  return getBaseRole(user) === "admin";
}

// ── Data visibility ─────────────────────────────────────────────

/** Access cross-department data: all schedules, all submissions, audit logs. */
export function canViewAll(user: UserMe | null | undefined): boolean {
  return hasAnyRole(user, "admin", "esq_head", "secretary");
}

/** Download full-faculty exports: schedule PDFs, print logs, audit exports. */
export function canExportAdminReports(user: UserMe | null | undefined): boolean {
  return hasAnyRole(user, "admin", "esq_head", "secretary");
}

/** Download department-scoped exports. */
export function canExportOwnDepartment(
  user: UserMe | null | undefined,
): boolean {
  return hasAnyRole(user, "admin", "esq_head", "secretary", "dept_supervisor");
}

// ── Workflow management ─────────────────────────────────────────

/** Advance/revert signing rounds, unlock swap windows. */
export function canManageWorkflow(user: UserMe | null | undefined): boolean {
  return hasAnyRole(user, "admin", "esq_head", "secretary");
}

/** Sign a workflow round. */
export function canSignWorkflow(user: UserMe | null | undefined): boolean {
  return canManageWorkflow(user);
}

/** Create, activate, lock, archive exam periods. */
export function canManageExamPeriods(user: UserMe | null | undefined): boolean {
  return role(user) === "admin";
}

// ── Submissions ─────────────────────────────────────────────────

/** Create or update an exam submission. */
export function canSubmitExamPaper(user: UserMe | null | undefined): boolean {
  return hasAnyRole(user, "admin", "teacher", "dept_supervisor");
}

/** Approve or reject a submission. */
export function canApproveSubmission(user: UserMe | null | undefined): boolean {
  return hasAnyRole(user, "admin", "esq_head", "secretary");
}

// ── Schedule / print ────────────────────────────────────────────

/** Run the optimizer, assign supervisors, edit schedule entries. */
export function canManageSchedule(user: UserMe | null | undefined): boolean {
  return role(user) === "admin";
}

/** View and update the print queue. */
export function canAccessPrintQueue(user: UserMe | null | undefined): boolean {
  return hasAnyRole(user, "admin", "esq_head", "secretary", "print_shop");
}

/** Operational tools shared by admin and staff: pickup QR, room-floor actions, and ops exports. */
export function canManageOperationalWork(user: UserMe | null | undefined): boolean {
  return hasAnyRole(user, "admin", "staff");
}

/** Comment on draft payment documents. */
export function canCommentOnPaymentDocumentReview(user: UserMe | null | undefined): boolean {
  return hasAnyRole(user, "admin", "staff", "esq_head", "secretary");
}

/** Set supervisor/finance review decisions on draft payment documents. */
export function canManagePaymentDocumentReview(user: UserMe | null | undefined): boolean {
  return hasAnyRole(user, "admin", "esq_head", "secretary");
}

/** Update the separate evidence checklist for a draft payment document. */
export function canManagePaymentDocumentReviewChecklist(user: UserMe | null | undefined): boolean {
  return hasAnyRole(user, "admin", "esq_head", "secretary");
}

/** Read term-specific payment document preparation settings. */
export function canViewPaymentDocumentSettings(user: UserMe | null | undefined): boolean {
  return hasAnyRole(user, "admin", "esq_head", "secretary", "staff");
}

/** Modify term-specific payment document preparation settings. */
export function canManagePaymentDocumentSettings(user: UserMe | null | undefined): boolean {
  return hasAnyRole(user, "admin", "esq_head", "secretary");
}

/** Manage or view external (non-standard) exam entries. */
export function canAccessExternalExams(
  user: UserMe | null | undefined,
): boolean {
  return hasAnyRole(user, "admin", "staff", "esq_head", "secretary");
}

/** True only for the teacher role — used to decide personal exam work navigation path. */
export function canViewOwnExamWork(user: UserMe | null | undefined): boolean {
  return role(user) === "teacher";
}

// ── Co-exam groups ──────────────────────────────────────────────

/** Create and manage co-exam groups. */
export function canManageCoExam(user: UserMe | null | undefined): boolean {
  return role(user) === "admin";
}

// ── Settings / configuration ────────────────────────────────────

/** Read system settings. */
export function canViewSettings(user: UserMe | null | undefined): boolean {
  return hasAnyRole(user, "admin", "esq_head", "secretary");
}

/** Modify system settings. */
export function canEditSettings(user: UserMe | null | undefined): boolean {
  return role(user) === "admin";
}
