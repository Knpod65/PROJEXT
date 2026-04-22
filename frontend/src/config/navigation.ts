import type { UserRole } from "@/types/api";
import { translateWithFallback } from "@/i18n";

export interface AppPageConfig {
  key: string;
  title: string;
  description: string;
  path: string;
  icon: string;
  roles?: UserRole[];
  public?: boolean;
  navGroup?: NavGroupKey;
  mobile?: boolean;
  hidden?: boolean;
  allowBaseAdminPreview?: boolean;
}

export type NavGroupKey = "dashboard" | "operations" | "examManagement" | "people" | "system";

export const navGroupOrder: NavGroupKey[] = ["dashboard", "operations", "examManagement", "people", "system"];

export const appPages: AppPageConfig[] = [
  // ── Dashboard group ───────────────────────────────────────────
  {
    key: "dashboard",
    title: "Dashboard",
    description: "Live exam operations, staffing signals, and period-wide momentum.",
    path: "/dashboard",
    icon: "dashboard",
    roles: ["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher"],
    navGroup: "dashboard",
    mobile: true,
  },
  {
    key: "schedule",
    title: "Exam Schedule",
    description: "Master timetable, room allocation, and invigilation coverage.",
    path: "/schedule",
    icon: "event_note",
    roles: ["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher"],
    navGroup: "dashboard",
    mobile: true,
  },
  {
    key: "submissions",
    title: "Submissions",
    description: "Academic assessment records, review status, and message threads.",
    path: "/submissions",
    icon: "description",
    roles: ["admin", "esq_head", "secretary", "dept_supervisor", "teacher"],
    navGroup: "dashboard",
    mobile: true,
  },
  {
    key: "attendance",
    title: "Room Attendance",
    description: "Room occupancy, attendance summaries, and latest floor activity.",
    path: "/attendance",
    icon: "assignment_ind",
    roles: ["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher"],
    navGroup: "dashboard",
    mobile: true,
  },
  {
    key: "checkins",
    title: "Check-ins",
    description: "Operational check-ins, confirmations, and room readiness workflow.",
    path: "/checkins",
    icon: "how_to_reg",
    roles: ["admin", "dept_supervisor", "staff", "teacher"],
    navGroup: "dashboard",
    mobile: true,
  },
  {
    key: "swaps",
    title: "Swap Requests",
    description: "Coverage changes, swap coordination, and conflict resolution.",
    path: "/swaps",
    icon: "swap_horiz",
    roles: ["admin", "dept_supervisor", "staff", "teacher"],
    navGroup: "dashboard",
  },

  // ── Operations group ──────────────────────────────────────────
  {
    key: "workflow",
    title: "Workflow",
    description: "Approval pipeline, signature flow, and period release readiness.",
    path: "/workflow",
    icon: "approval",
    roles: ["admin", "esq_head", "secretary"],
    navGroup: "operations",
  },
  {
    key: "copy",
    title: "Copy Count",
    description: "Sheet counts, copy cost, and print workload tracking.",
    path: "/copy",
    icon: "content_copy",
    roles: ["admin"],
    navGroup: "operations",
  },
  {
    key: "print-queue",
    title: "Print Queue",
    description: "Print-shop batches, delivery status, and supply readiness.",
    path: "/print-queue",
    icon: "print",
    roles: ["print_shop"],
    navGroup: "operations",
  },
  {
    key: "printreview",
    title: "Print Review",
    description: "Pre-print verification, submission approval, and print handoff.",
    path: "/printreview",
    icon: "fact_check",
    roles: ["admin", "esq_head", "secretary"],
    navGroup: "operations",
  },
  {
    key: "coexam",
    title: "Co-Exam",
    description: "Shared-exam planning and group alignment controls.",
    path: "/coexam",
    icon: "groups",
    roles: ["admin"],
    navGroup: "operations",
  },
  {
    key: "optimizer",
    title: "Optimizer",
    description: "Scheduling optimization, fairness checks, and assignment automation.",
    path: "/optimizer",
    icon: "query_stats",
    roles: ["admin"],
    navGroup: "operations",
  },
  {
    key: "rooms-v2",
    title: "Rooms",
    description: "Room capacity, active status, and date blocking for optimizer input.",
    path: "/rooms-v2",
    icon: "meeting_room",
    roles: ["admin"],
    navGroup: "operations",
  },
  {
    key: "external",
    title: "External Exams",
    description: "Special exam sessions managed outside the standard timetable.",
    path: "/external",
    icon: "language",
    roles: ["admin", "staff", "teacher"],
    navGroup: "operations",
  },

  // ── Exam Management group ─────────────────────────────────────
  {
    key: "sections",
    title: "Sections",
    description: "Course sections, enrollments, and assigned teaching records.",
    path: "/sections",
    icon: "menu_book",
    roles: ["admin", "esq_head", "secretary", "staff", "teacher"],
    navGroup: "examManagement",
  },
  {
    key: "myexam",
    title: "My Exam Work",
    description: "Personal assignments, submissions, and responsibilities.",
    path: "/myexam",
    icon: "assignment",
    roles: ["teacher"],
    navGroup: "examManagement",
  },
  {
    key: "import",
    title: "Import Data",
    description: "Bulk data intake for terms, sections, and enrollment records.",
    path: "/import",
    icon: "upload_file",
    roles: ["admin"],
    navGroup: "examManagement",
  },
  {
    key: "import-audit",
    title: "Import Audit",
    description: "Session-level and row-level audit review for import executions.",
    path: "/import-audit",
    icon: "manage_search",
    roles: ["admin"],
    navGroup: "examManagement",
  },

  // ── People group ──────────────────────────────────────────────
  {
    key: "users",
    title: "Users",
    description: "User accounts, role management, and access administration.",
    path: "/users",
    icon: "manage_accounts",
    roles: ["admin"],
    navGroup: "people",
  },

  // ── System group ──────────────────────────────────────────────
  {
    key: "period",
    title: "Exam Periods",
    description: "Term management, active windows, and period switching.",
    path: "/period",
    icon: "calendar_month",
    roles: ["admin"],
    navGroup: "system",
  },
  {
    key: "settings",
    title: "Settings",
    description: "System configuration, retention policy, term preview, and access controls.",
    path: "/settings",
    icon: "settings",
    roles: ["admin"],
    navGroup: "system",
    allowBaseAdminPreview: true,
  },
  {
    key: "exammanager",
    title: "Exam Manager",
    description: "Manual ownership assignment for exam workflows.",
    path: "/exammanager",
    icon: "assignment_add",
    roles: ["admin"],
    navGroup: "system",
    hidden: true,
  },

  // ── Hidden utility pages (routes still registered, not in nav) ─
  {
    key: "venues-v2",
    title: "Venues",
    description: "Venue management.",
    path: "/venues-v2",
    icon: "domain",
    roles: ["admin"],
    hidden: true,
  },
  {
    key: "students-v2",
    title: "Students",
    description: "Student record management.",
    path: "/students-v2",
    icon: "school",
    roles: ["admin"],
    hidden: true,
  },
  {
    key: "student-search",
    title: "Student Search",
    description: "Public lookup for individual student exam timetables.",
    path: "/student-search",
    icon: "person_search",
    roles: ["student"],
    public: true,
    hidden: true,
  },
  {
    key: "role-selection",
    title: "Role Selection",
    description: "Choose the production role before signing in.",
    path: "/role-selection",
    icon: "badge",
    public: true,
    hidden: true,
  },
  {
    key: "login",
    title: "Sign In",
    description: "Authenticate into the exam operations workspace.",
    path: "/login",
    icon: "login",
    public: true,
    hidden: true,
  },
];

export const mobilePageKeys = ["dashboard", "schedule", "submissions", "attendance", "checkins"];

export function getPageConfig(pathname: string) {
  return appPages.find((page) => page.path === pathname);
}

export function getPageTitle(page: AppPageConfig) {
  return translateWithFallback(`navigation.pages.${page.key}.title`, page.title);
}

export function getPageDescription(page: AppPageConfig) {
  return translateWithFallback(`navigation.pages.${page.key}.description`, page.description);
}

export function getNavGroupLabel(group: NavGroupKey) {
  return translateWithFallback(`navigation.groups.${group}`, group);
}
