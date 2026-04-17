import { useMemo, useState } from "react";

import type { RoomOut } from "@/types/api";

export type RoomStatus = "available" | "occupied" | "maintenance" | "reserved";
export type AllocationStage = "free" | "pending" | "assigned" | "review";

export interface RoomRecordV2 extends RoomOut {
  zone: string;
  status: RoomStatus;
  utilization: number;
  upcomingExam: string;
  nextSlot: string;
  allocationStage: AllocationStage;
  notes: string;
}

export interface VenueRecordV2 {
  id: number;
  venueCode: string;
  venueName: string;
  building: string;
  totalRooms: number;
  availableRooms: number;
  totalSeats: number;
  allocatedSeats: number;
  utilization: number;
  allocationStage: AllocationStage;
  status: RoomStatus;
  notes: string;
}

const roomRows: RoomRecordV2[] = [
  {
    id: 101,
    room_name: "Hall A-101",
    building: "Main Tower",
    capacity: 180,
    is_active: true,
    zone: "A",
    status: "available",
    utilization: 0.42,
    upcomingExam: "LAW-402",
    nextSlot: "09:00",
    allocationStage: "assigned",
    notes: "Primary hall for high-capacity exams.",
  },
  {
    id: 102,
    room_name: "Hall A-102",
    building: "Main Tower",
    capacity: 160,
    is_active: true,
    zone: "A",
    status: "occupied",
    utilization: 0.78,
    upcomingExam: "SOC-201",
    nextSlot: "13:00",
    allocationStage: "pending",
    notes: "Current session requires final seat confirmation.",
  },
  {
    id: 103,
    room_name: "Room B-210",
    building: "Science Block",
    capacity: 90,
    is_active: true,
    zone: "B",
    status: "reserved",
    utilization: 0.55,
    upcomingExam: "SCI-301",
    nextSlot: "10:00",
    allocationStage: "review",
    notes: "Reserved for mixed-format paper.",
  },
  {
    id: 104,
    room_name: "Room B-211",
    building: "Science Block",
    capacity: 72,
    is_active: true,
    zone: "B",
    status: "available",
    utilization: 0.31,
    upcomingExam: "PHY-101",
    nextSlot: "15:00",
    allocationStage: "free",
    notes: "Suitable for smaller class groups.",
  },
  {
    id: 105,
    room_name: "Lab C-03",
    building: "Annex C",
    capacity: 48,
    is_active: true,
    zone: "C",
    status: "maintenance",
    utilization: 0.0,
    upcomingExam: "-",
    nextSlot: "-",
    allocationStage: "review",
    notes: "Maintenance block until network line is certified.",
  },
  {
    id: 106,
    room_name: "Hall D-401",
    building: "Faculty Wing",
    capacity: 120,
    is_active: false,
    zone: "D",
    status: "occupied",
    utilization: 0.63,
    upcomingExam: "POL-498",
    nextSlot: "17:00",
    allocationStage: "assigned",
    notes: "Inactive for admin review only.",
  },
];

const venueRows: VenueRecordV2[] = [
  {
    id: 201,
    venueCode: "MT",
    venueName: "Main Tower",
    building: "Main Tower",
    totalRooms: 12,
    availableRooms: 7,
    totalSeats: 1480,
    allocatedSeats: 920,
    utilization: 0.62,
    allocationStage: "assigned",
    status: "available",
    notes: "Core capacity venue for large sessions.",
  },
  {
    id: 202,
    venueCode: "SB",
    venueName: "Science Block",
    building: "Science Block",
    totalRooms: 8,
    availableRooms: 5,
    totalSeats: 620,
    allocatedSeats: 432,
    utilization: 0.7,
    allocationStage: "pending",
    status: "occupied",
    notes: "High turnover venue with compact room types.",
  },
  {
    id: 203,
    venueCode: "AC",
    venueName: "Annex C",
    building: "Annex C",
    totalRooms: 5,
    availableRooms: 3,
    totalSeats: 240,
    allocatedSeats: 120,
    utilization: 0.5,
    allocationStage: "review",
    status: "reserved",
    notes: "Used for controlled review and overflow sessions.",
  },
  {
    id: 204,
    venueCode: "FW",
    venueName: "Faculty Wing",
    building: "Faculty Wing",
    totalRooms: 7,
    availableRooms: 2,
    totalSeats: 510,
    allocatedSeats: 400,
    utilization: 0.78,
    allocationStage: "assigned",
    status: "occupied",
    notes: "Mostly locked for faculty-specific session blocks.",
  },
];

function statusMatches(status: RoomStatus, filter: "all" | RoomStatus) {
  return filter === "all" || status === filter;
}

function stageMatches(stage: AllocationStage, filter: "all" | AllocationStage) {
  return filter === "all" || stage === filter;
}

export function useRoomsData() {
  const [query, setQuery] = useState("");
  const [buildingFilter, setBuildingFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState<"all" | RoomStatus>("all");
  const [stageFilter, setStageFilter] = useState<"all" | AllocationStage>("all");

  const buildings = useMemo(() => {
    const values = [...new Set([...roomRows.map((row) => row.building ?? "Unknown"), ...venueRows.map((row) => row.building)])];
    return values.sort();
  }, []);

  const filteredRooms = useMemo(() => {
    return roomRows.filter((row) => {
      const matchesQuery =
        query.trim().length === 0 ||
        `${row.room_name} ${row.building ?? ""} ${row.zone} ${row.notes} ${row.upcomingExam}`
          .toLowerCase()
          .includes(query.toLowerCase());
      const matchesBuilding = buildingFilter === "all" || (row.building ?? "") === buildingFilter;
      const matchesStatus = statusMatches(row.status, statusFilter);
      const matchesStage = stageMatches(row.allocationStage, stageFilter);

      return matchesQuery && matchesBuilding && matchesStatus && matchesStage;
    });
  }, [buildingFilter, query, stageFilter, statusFilter]);

  const filteredVenues = useMemo(() => {
    return venueRows.filter((row) => {
      const matchesQuery =
        query.trim().length === 0 ||
        `${row.venueCode} ${row.venueName} ${row.building} ${row.notes}`.toLowerCase().includes(query.toLowerCase());
      const matchesBuilding = buildingFilter === "all" || row.building === buildingFilter;
      const matchesStatus = statusMatches(row.status, statusFilter);
      const matchesStage = stageMatches(row.allocationStage, stageFilter);

      return matchesQuery && matchesBuilding && matchesStatus && matchesStage;
    });
  }, [buildingFilter, query, stageFilter, statusFilter]);

  const roomStats = useMemo(() => {
    const available = roomRows.filter((row) => row.status === "available").length;
    const occupied = roomRows.filter((row) => row.status === "occupied").length;
    const maintenance = roomRows.filter((row) => row.status === "maintenance").length;
    const reserved = roomRows.filter((row) => row.status === "reserved").length;

    return {
      total: roomRows.length,
      available,
      occupied,
      maintenance,
      reserved,
      totalCapacity: roomRows.reduce((sum, row) => sum + row.capacity, 0),
    };
  }, []);

  const venueStats = useMemo(() => {
    const available = venueRows.filter((row) => row.status === "available").length;
    const occupied = venueRows.filter((row) => row.status === "occupied").length;
    const reserved = venueRows.filter((row) => row.status === "reserved").length;
    const review = venueRows.filter((row) => row.allocationStage === "review").length;

    return {
      total: venueRows.length,
      available,
      occupied,
      reserved,
      review,
      totalSeats: venueRows.reduce((sum, row) => sum + row.totalSeats, 0),
    };
  }, []);

  const allocationMatrix = useMemo(() => {
    const timeSlots = ["08:00", "10:00", "13:00", "15:00", "17:00"];
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];

    return days.map((day, dayIndex) => ({
      day,
      cells: timeSlots.map((slot, slotIndex) => {
        const seed = (dayIndex + 1) * (slotIndex + 2);
        const room = roomRows[seed % roomRows.length];
        return {
          slot,
          roomName: room.room_name,
          label: room.status === "available" ? "Available" : room.upcomingExam,
          tone: room.status === "available" ? "available" : room.status,
        };
      }),
    }));
  }, []);

  const resetFilters = () => {
    setQuery("");
    setBuildingFilter("all");
    setStatusFilter("all");
    setStageFilter("all");
  };

  return {
    query,
    buildingFilter,
    statusFilter,
    stageFilter,
    setQuery,
    setBuildingFilter,
    setStatusFilter,
    setStageFilter,
    resetFilters,
    buildings,
    filteredRooms,
    filteredVenues,
    roomStats,
    venueStats,
    allocationMatrix,
  };
}
