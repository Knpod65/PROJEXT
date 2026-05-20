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
     key: "admin-intelligence-dashboard",
     title: "Admin Intelligence",
     description: "Role-based significant metrics dashboard for operational oversight.",
     path: "/admin-intelligence-dashboard",
     icon: "insights",
     roles: ["admin"],
     navGroup: "dashboard",
     mobile: true,
   },
   {
     key: "executive-analytics",
    title: "Executive Analytics",
    description: "Institutional health score, workload trends, and governance metrics.",
    path: "/analytics",
    icon: "insights",
    roles: ["admin", "esq_head", "secretary"],
    navGroup: "dashboard",
  },
  {
    key: "governance-cockpit",
    title: "Governance Cockpit",
    description: "Blocker counts, pending approvals, publication gates, escalation and rollback events.",
    path: "/governance",
    icon: "admin_panel_settings",
    roles: ["admin", "esq_head", "secretary"],
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
    roles: ["admin", "staff"],
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
    key: "optimizer-trace",
    title: "Optimization Trace",
    description: "Candidate lineage, rejected alternatives, constraint hits, and quality scoring for optimizer runs.",
    path: "/optimizer-trace",
    icon: "hub",
    roles: ["admin"],
    navGroup: "operations",
  },
  {
    key: "staff-availability",
    title: "Staff Availability",
    description: "Block operational availability for invigilation, distribution, and external-exam staffing.",
    path: "/staff-availability",
    icon: "event_busy",
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
    roles: ["admin", "staff"],
    navGroup: "operations",
  },
  {
    key: "exports-center",
    title: "Export Center",
    description: "Centralized export hub for documents, workload, staffing, and schedule reports.",
    path: "/exports-center",
    icon: "inventory_2",
    roles: ["admin", "staff"],
    navGroup: "operations",
  },
  {
    key: "historical-schedules",
    title: "Historical Schedule Review",
    description: "Compare optimized baseline and final adjusted schedule imports for the historical 2/2568 final exam period.",
    path: "/historical-schedules",
    icon: "history",
    roles: ["admin"],
    navGroup: "operations",
  },

  // ── Exam Management group ─────────────────────────────────────
  {
    key: "sections",
    title: "Sections",
    description: "Course sections, enrollments, and assigned teaching records.",
    path: "/sections",
    icon: "menu_book",
    roles: ["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher"],
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
    key: "platform-configuration",
    title: "Platform Configuration",
    description: "View D3 faculty config, workload policy, governance flow, integration contracts, and analytics metrics.",
    path: "/platform-config",
    icon: "tune",
    roles: ["admin"],
    navGroup: "system",
  },
  {
    key: "exammanager",
    title: "Course Ownership",
    description: "Department-scoped teacher responsibility assignment for each exam cycle.",
    path: "/exammanager",
    icon: "assignment_add",
    roles: ["admin", "dept_supervisor"],
    navGroup: "examManagement",
  },
  {
    key: "operational-health",
    title: "Operational Health",
    description: "Backend health, analytics health, integration readiness, and service status.",
    path: "/operational-health",
    icon: "health_and_safety",
    roles: ["admin", "esq_head"],
    navGroup: "system",
  },
  {
    key: "audit-explorer",
    title: "Audit Explorer",
    description: "Audit events, governance timeline, and lifecycle tracking.",
    path: "/audit-explorer",
    icon: "history",
    roles: ["admin", "esq_head"],
    navGroup: "system",
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
