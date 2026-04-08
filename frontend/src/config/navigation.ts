import type { UserRole } from "@/types/api";

export interface AppPageConfig {
  key: string;
  title: string;
  path: string;
  icon: string;
  roles?: UserRole[];
  public?: boolean;
  navGroup?: string;
  mobile?: boolean;
  hidden?: boolean;
}

export const appPages: AppPageConfig[] = [
  {
    key: "dashboard",
    title: "แดชบอร์ด",
    path: "/dashboard",
    icon: "📊",
    roles: ["admin", "esq_head", "secretary", "dept_supervisor", "staff"],
    navGroup: "ภาพรวม",
    mobile: true,
  },
  {
    key: "schedule",
    title: "ตารางสอบ",
    path: "/schedule",
    icon: "📅",
    roles: ["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher"],
    navGroup: "ภาพรวม",
    mobile: true,
  },
  {
    key: "myexam",
    title: "จัดการสอบของฉัน",
    path: "/myexam",
    icon: "📋",
    roles: ["teacher"],
    navGroup: "งานของฉัน",
  },
  {
    key: "submissions",
    title: "ส่งข้อสอบ",
    path: "/submissions",
    icon: "📤",
    roles: ["admin", "esq_head", "secretary", "dept_supervisor", "teacher"],
    navGroup: "งานของฉัน",
    mobile: true,
  },
  {
    key: "swaps",
    title: "การสลับกะ",
    path: "/swaps",
    icon: "🔄",
    roles: ["admin", "dept_supervisor", "staff", "teacher"],
    navGroup: "งานของฉัน",
    mobile: true,
  },
  {
    key: "checkins",
    title: "Check-in วันสอบ",
    path: "/checkins",
    icon: "✅",
    roles: ["admin", "dept_supervisor", "staff", "teacher"],
    navGroup: "งานของฉัน",
    mobile: true,
  },
  {
    key: "student-search",
    title: "ค้นหาตารางสอบ",
    path: "/student-search",
    icon: "🔍",
    public: true,
    navGroup: "งานของฉัน",
  },
  {
    key: "sections",
    title: "รายวิชา / Sections",
    path: "/sections",
    icon: "📚",
    roles: ["admin", "esq_head", "secretary", "staff", "teacher"],
    navGroup: "ข้อมูล",
  },
  {
    key: "copy",
    title: "คำนวณค่าถ่าย",
    path: "/copy",
    icon: "🖨",
    roles: ["admin", "staff"],
    navGroup: "ข้อมูล",
  },
  {
    key: "workflow",
    title: "ยืนยันตาราง",
    path: "/workflow",
    icon: "🖊",
    roles: ["admin", "esq_head", "secretary"],
    navGroup: "วางแผนสอบ",
  },
  {
    key: "coexam",
    title: "Co-Exam",
    path: "/coexam",
    icon: "🔗",
    roles: ["admin"],
    navGroup: "วางแผนสอบ",
  },
  {
    key: "optimizer",
    title: "จัดตารางสอบ",
    path: "/optimizer",
    icon: "🎯",
    roles: ["admin"],
    navGroup: "วางแผนสอบ",
  },
  {
    key: "printreview",
    title: "ตรวจก่อนพิมพ์",
    path: "/printreview",
    icon: "🖨️",
    roles: ["admin"],
    navGroup: "วางแผนสอบ",
  },
  {
    key: "external",
    title: "สอบพิเศษ",
    path: "/external",
    icon: "🏛️",
    roles: ["admin"],
    navGroup: "วางแผนสอบ",
  },
  {
    key: "import",
    title: "นำเข้าข้อมูล",
    path: "/import",
    icon: "📥",
    roles: ["admin"],
    navGroup: "ระบบ",
  },
  {
    key: "period",
    title: "รอบสอบ",
    path: "/period",
    icon: "🗓️",
    roles: ["admin"],
    navGroup: "ระบบ",
  },
  {
    key: "settings",
    title: "ตั้งค่าระบบ",
    path: "/settings",
    icon: "⚙️",
    roles: ["admin"],
    navGroup: "ระบบ",
  },
  {
    key: "users",
    title: "ผู้ใช้งาน",
    path: "/users",
    icon: "👥",
    roles: ["admin"],
    navGroup: "ระบบ",
  },
  {
    key: "exammanager",
    title: "มอบหมายผู้รับผิดชอบ",
    path: "/exammanager",
    icon: "🧑‍🏫",
    roles: ["admin"],
    navGroup: "ระบบ",
    hidden: true,
  },
  {
    key: "login",
    title: "เข้าสู่ระบบ",
    path: "/login",
    icon: "🔐",
    public: true,
    hidden: true,
  },
];

export const mobilePageKeys = ["dashboard", "schedule", "submissions", "swaps", "checkins"];

export function getPageConfig(pathname: string) {
  return appPages.find((page) => page.path === pathname);
}
