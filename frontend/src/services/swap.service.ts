import type { SwapItem, UserOut } from "@/types/api";
import { del, get, post } from "./api";

export interface MySupervisionSlot {
  supervision_id: number;
  schedule_id: number;
  exam_date: string | null;
  exam_time: string | null;
  course: string | null;
  room: string | null;
  section_no: string | null;
  swap_requested: boolean;
  is_swapped: boolean;
}

export function getMySwaps() {
  return get<SwapItem[]>("/swaps2/my");
}

export function getWaitingSwaps() {
  return get<SwapItem[]>("/swaps2/waiting");
}

export function getMySupervisions() {
  return get<MySupervisionSlot[]>("/swaps2/my-supervisions");
}

export function getAvailableUsers(supervisionId: number) {
  return get<UserOut[]>(`/swaps2/available-users/${supervisionId}`);
}

export function createSwap(mySupervisionId: number, targetUserId: number, message?: string) {
  return post<{ success: boolean; swap_id: number }>("/swaps2", {
    my_supervision_id: mySupervisionId,
    target_user_id: targetUserId,
    message,
  });
}

export function respondSwap(swapId: number, accept: boolean, reason?: string) {
  return post<{ success: boolean; status: string }>(`/swaps2/${swapId}/respond`, {
    accept,
    reason,
  });
}

export function cancelSwap(swapId: number) {
  return del<{ success: boolean; status: string }>(`/swaps2/${swapId}`);
}
