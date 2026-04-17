import { useMemo, useState } from "react";

export type WorkflowBatchStatus = "ready" | "pending" | "returned";
export type WorkflowRiskLevel = "low" | "medium" | "high";

export interface WorkflowCalendarDay {
  key: string;
  label: string;
  dateLabel: string;
  isFocus?: boolean;
}

export interface WorkflowScheduleSlot {
  id: number;
  courseCode: string;
  courseTitle: string;
  location: string;
  dayKey: string;
  timeSlot: string;
  stream: "primary" | "secondary" | "tertiary";
}

export interface WorkflowRegistryRow {
  id: number;
  batchCode: string;
  department: string;
  owner: string;
  status: WorkflowBatchStatus;
  risk: WorkflowRiskLevel;
  lastUpdated: string;
  comment: string;
}

export interface WorkflowReviewNote {
  id: number;
  author: string;
  createdAt: string;
  severity: "info" | "warning";
  message: string;
}

const calendarDays: WorkflowCalendarDay[] = [
  { key: "mon", label: "Mon", dateLabel: "13 May" },
  { key: "tue", label: "Tue", dateLabel: "14 May", isFocus: true },
  { key: "wed", label: "Wed", dateLabel: "15 May", isFocus: true },
  { key: "thu", label: "Thu", dateLabel: "16 May" },
  { key: "fri", label: "Fri", dateLabel: "17 May" },
];

const timeSlots = ["09:00", "13:00"];

const scheduleSlots: WorkflowScheduleSlot[] = [
  {
    id: 1,
    courseCode: "LAW-402",
    courseTitle: "Advanced Jurisprudence",
    location: "Hall-A",
    dayKey: "tue",
    timeSlot: "09:00",
    stream: "primary",
  },
  {
    id: 2,
    courseCode: "SOC-101",
    courseTitle: "Ethics and Governance",
    location: "Grand-Aud",
    dayKey: "wed",
    timeSlot: "09:00",
    stream: "secondary",
  },
  {
    id: 3,
    courseCode: "LAW-215",
    courseTitle: "Constitutional Law II",
    location: "Room-402",
    dayKey: "tue",
    timeSlot: "13:00",
    stream: "primary",
  },
  {
    id: 4,
    courseCode: "PHY-301",
    courseTitle: "Quantum Mechanics I",
    location: "Lab-B2",
    dayKey: "wed",
    timeSlot: "13:00",
    stream: "tertiary",
  },
];

const registryRows: WorkflowRegistryRow[] = [
  {
    id: 601,
    batchCode: "SPR-26-LAW-A",
    department: "Law",
    owner: "Patchara S.",
    status: "pending",
    risk: "medium",
    lastUpdated: "17 Apr, 09:22",
    comment: "Hall utilization over 92%",
  },
  {
    id: 602,
    batchCode: "SPR-26-SOC-C",
    department: "Social Sciences",
    owner: "Nattida P.",
    status: "ready",
    risk: "low",
    lastUpdated: "17 Apr, 08:54",
    comment: "All room assignments confirmed",
  },
  {
    id: 603,
    batchCode: "SPR-26-SCI-B",
    department: "Science",
    owner: "Kittisak V.",
    status: "returned",
    risk: "high",
    lastUpdated: "16 Apr, 18:10",
    comment: "Invigilator conflict requires correction",
  },
  {
    id: 604,
    batchCode: "SPR-26-BUS-D",
    department: "Business",
    owner: "Sudarat K.",
    status: "pending",
    risk: "medium",
    lastUpdated: "17 Apr, 10:04",
    comment: "Printing package still validating",
  },
];

const reviewNotes: WorkflowReviewNote[] = [
  {
    id: 1,
    author: "ESQ Head",
    createdAt: "17 Apr, 09:30",
    severity: "warning",
    message: "Review room balancing in SPR-26-LAW-A before sign-off.",
  },
  {
    id: 2,
    author: "Audit Desk",
    createdAt: "17 Apr, 08:40",
    severity: "info",
    message: "Two high-capacity rooms moved from standby to active.",
  },
];

export function useWorkflowData() {
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | WorkflowBatchStatus>("all");

  const filteredRegistry = useMemo(() => {
    return registryRows.filter((row) => {
      const textMatch =
        query.trim().length === 0 ||
        `${row.batchCode} ${row.department} ${row.owner} ${row.comment}`
          .toLowerCase()
          .includes(query.toLowerCase());
      const statusMatch = statusFilter === "all" || row.status === statusFilter;
      return textMatch && statusMatch;
    });
  }, [query, statusFilter]);

  const stats = useMemo(() => {
    const pending = registryRows.filter((row) => row.status === "pending").length;
    const returned = registryRows.filter((row) => row.status === "returned").length;
    const ready = registryRows.filter((row) => row.status === "ready").length;
    const highRisk = registryRows.filter((row) => row.risk === "high").length;

    return {
      total: registryRows.length,
      pending,
      returned,
      ready,
      highRisk,
    };
  }, []);

  const getSlot = (timeSlot: string, dayKey: string) => {
    return scheduleSlots.find((slot) => slot.timeSlot === timeSlot && slot.dayKey === dayKey);
  };

  const resetFilters = () => {
    setQuery("");
    setStatusFilter("all");
  };

  return {
    sessionLabel: "Spring 2026",
    approvalState: "Pending Final Audit",
    calendarDays,
    timeSlots,
    reviewNotes,
    registryRows: filteredRegistry,
    stats,
    query,
    statusFilter,
    setQuery,
    setStatusFilter,
    resetFilters,
    getSlot,
  };
}
