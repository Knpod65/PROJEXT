import { useMemo, useState } from "react";

import type { UserRole } from "@/types/api";

export type SwapPriority = "low" | "medium" | "high";
export type SwapStatus = "pending" | "approved" | "rejected" | "escalated";
export type SwapsViewRole = "admin" | "staff" | "teacher";

export interface SwapRequestV2 {
  id: number;
  requester: string;
  target: string;
  course: string;
  room: string;
  examDate: string;
  examTime: string;
  requestedAt: string;
  priority: SwapPriority;
  status: SwapStatus;
  createdByRole: "teacher" | "staff";
  createdByMe: boolean;
  reviewQueue: boolean;
  scope: "department" | "system";
  note?: string;
}

const mockSwapRequests: SwapRequestV2[] = [
  {
    id: 2401,
    requester: "Anan K.",
    target: "Sirin P.",
    course: "PS 211",
    room: "SCB 2101",
    examDate: "2026-05-02",
    examTime: "09:00-12:00",
    requestedAt: "2026-04-17T09:14:00",
    priority: "high",
    status: "pending",
    createdByRole: "teacher",
    createdByMe: false,
    reviewQueue: true,
    scope: "system",
    note: "Medical leave overlap",
  },
  {
    id: 2402,
    requester: "Nicha T.",
    target: "Korn C.",
    course: "PS 314",
    room: "SCB 1407",
    examDate: "2026-05-03",
    examTime: "13:00-16:00",
    requestedAt: "2026-04-17T09:46:00",
    priority: "medium",
    status: "pending",
    createdByRole: "teacher",
    createdByMe: false,
    reviewQueue: true,
    scope: "department",
    note: "Schedule collision with graduate seminar",
  },
  {
    id: 2403,
    requester: "Panupong W.",
    target: "Sasi M.",
    course: "PS 121",
    room: "SCB 1203",
    examDate: "2026-05-04",
    examTime: "09:00-12:00",
    requestedAt: "2026-04-16T18:22:00",
    priority: "low",
    status: "approved",
    createdByRole: "teacher",
    createdByMe: true,
    reviewQueue: false,
    scope: "department",
  },
  {
    id: 2404,
    requester: "Chonticha R.",
    target: "Thana B.",
    course: "PS 487",
    room: "SCB 3308",
    examDate: "2026-05-04",
    examTime: "13:00-16:00",
    requestedAt: "2026-04-16T16:55:00",
    priority: "high",
    status: "escalated",
    createdByRole: "staff",
    createdByMe: false,
    reviewQueue: true,
    scope: "system",
    note: "No qualified replacement confirmed",
  },
  {
    id: 2405,
    requester: "Pimchanok L.",
    target: "Thanit N.",
    course: "PS 498",
    room: "SCB 4102",
    examDate: "2026-05-05",
    examTime: "09:00-12:00",
    requestedAt: "2026-04-16T13:10:00",
    priority: "medium",
    status: "rejected",
    createdByRole: "teacher",
    createdByMe: true,
    reviewQueue: false,
    scope: "department",
    note: "Target assigned to concurrent venue",
  },
  {
    id: 2406,
    requester: "Napat S.",
    target: "Pitcha A.",
    course: "PS 205",
    room: "SCB 2210",
    examDate: "2026-05-05",
    examTime: "13:00-16:00",
    requestedAt: "2026-04-17T07:28:00",
    priority: "high",
    status: "pending",
    createdByRole: "teacher",
    createdByMe: true,
    reviewQueue: true,
    scope: "department",
  },
  {
    id: 2407,
    requester: "Rachan S.",
    target: "Nara C.",
    course: "PS 305",
    room: "SCB 2411",
    examDate: "2026-05-06",
    examTime: "09:00-12:00",
    requestedAt: "2026-04-17T10:02:00",
    priority: "medium",
    status: "pending",
    createdByRole: "staff",
    createdByMe: false,
    reviewQueue: true,
    scope: "department",
  },
];

function toViewRole(role: UserRole | null | undefined): SwapsViewRole {
  if (role === "admin") {
    return "admin";
  }

  if (role === "staff" || role === "dept_supervisor") {
    return "staff";
  }

  return "teacher";
}

function toDateLabel(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function useSwapsData(role: UserRole | null | undefined) {
  const viewRole = toViewRole(role);
  const [rows, setRows] = useState<SwapRequestV2[]>(mockSwapRequests);
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | SwapStatus>("all");
  const [priorityFilter, setPriorityFilter] = useState<"all" | SwapPriority>("all");

  const roleScopedRows = useMemo(() => {
    if (viewRole === "admin") {
      return rows;
    }

    if (viewRole === "staff") {
      return rows.filter((row) => row.reviewQueue || row.createdByRole === "staff");
    }

    return rows.filter((row) => row.createdByRole === "teacher" && row.createdByMe);
  }, [rows, viewRole]);

  const filteredRows = useMemo(() => {
    return roleScopedRows.filter((row) => {
      const textMatch =
        query.trim().length === 0 ||
        `${row.requester} ${row.target} ${row.course} ${row.room}`.toLowerCase().includes(query.toLowerCase());
      const statusMatch = statusFilter === "all" || row.status === statusFilter;
      const priorityMatch = priorityFilter === "all" || row.priority === priorityFilter;
      return textMatch && statusMatch && priorityMatch;
    });
  }, [priorityFilter, query, roleScopedRows, statusFilter]);

  const stats = useMemo(() => {
    const pending = roleScopedRows.filter((row) => row.status === "pending").length;
    const escalated = roleScopedRows.filter((row) => row.status === "escalated").length;
    const approvedToday = roleScopedRows.filter((row) => row.status === "approved").length;
    const highPriority = roleScopedRows.filter((row) => row.priority === "high").length;

    return {
      total: roleScopedRows.length,
      pending,
      escalated,
      approvedToday,
      highPriority,
    };
  }, [roleScopedRows]);

  const resetFilters = () => {
    setQuery("");
    setStatusFilter("all");
    setPriorityFilter("all");
  };

  const patchStatus = (id: number, status: SwapStatus) => {
    setRows((current) =>
      current.map((row) => {
        if (row.id !== id) {
          return row;
        }

        return {
          ...row,
          status,
          requestedAt: toDateLabel(new Date().toISOString()),
        };
      }),
    );
  };

  const requestSwap = () => {
    setRows((current) => [
      {
        id: Math.max(...current.map((item) => item.id)) + 1,
        requester: "Current User",
        target: "Swap Pool",
        course: "PS 399",
        room: "SCB 1102",
        examDate: "2026-05-07",
        examTime: "09:00-12:00",
        requestedAt: new Date().toISOString(),
        priority: "medium",
        status: "pending",
        createdByRole: "teacher",
        createdByMe: true,
        reviewQueue: true,
        scope: "department",
        note: "Draft request created from V2 test flow",
      },
      ...current,
    ]);
  };

  return {
    viewRole,
    rows: filteredRows,
    rawRows: roleScopedRows,
    stats,
    query,
    statusFilter,
    priorityFilter,
    setQuery,
    setStatusFilter,
    setPriorityFilter,
    resetFilters,
    requestSwap,
    approveSwap: (id: number) => patchStatus(id, "approved"),
    rejectSwap: (id: number) => patchStatus(id, "rejected"),
    escalateSwap: (id: number) => patchStatus(id, "escalated"),
    withdrawSwap: (id: number) => patchStatus(id, "rejected"),
  };
}
