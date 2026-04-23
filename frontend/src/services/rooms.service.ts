import type { RoomOut } from "@/types/api";
import { del, get, post, put } from "./api";

export interface RoomUnavailabilityRecord {
  id: number;
  room_id: number;
  room_name: string | null;
  capacity: number | null;
  block_date: string;
  block_time: string | null;
  start_time?: string | null;
  end_time?: string | null;
  all_day: boolean;
  reason: string | null;
}

export interface RoomCreateData {
  room_name: string;
  building?: string;
  capacity: number;
  e_room_code?: string;
}

export interface RoomUpdateData {
  room_name?: string;
  building?: string;
  capacity?: number;
  e_room_code?: string;
  is_active?: boolean;
}

export function getRooms(includeInactive = false) {
  return get<RoomOut[]>("/courses/rooms", {
    query: { include_inactive: includeInactive },
  });
}

export function createRoom(data: RoomCreateData) {
  return post<RoomOut>("/courses/rooms", data);
}

export function updateRoom(roomId: number, data: RoomUpdateData) {
  return put<RoomOut>(`/courses/rooms/${roomId}`, data);
}

export function getRoomUnavailability(roomId?: number) {
  return get<RoomUnavailabilityRecord[]>("/workflow/room-unavailability/", {
    query: roomId !== undefined ? { room_id: roomId } : undefined,
  });
}

export function addRoomUnavailability(data: {
  room_id: number;
  block_date: string;
  block_time?: string;
  start_time?: string;
  end_time?: string;
  reason?: string;
}) {
  return post<{ id: number; status: string }>("/workflow/room-unavailability/", data);
}

export function deleteRoomUnavailability(id: number) {
  return del<{ status: string }>(`/workflow/room-unavailability/${id}`);
}
