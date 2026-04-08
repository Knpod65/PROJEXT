import type { SwapItem, UserOut } from "@/types/api";
import { del, get, post } from "./api";

export function getMySwaps() {
  return get<SwapItem[]>("/swaps2/my");
}

export function getWaitingSwaps() {
  return get<SwapItem[]>("/swaps2/waiting");
}

export function getAvailableUsers(supervisionId: number) {
  return get<UserOut[]>(`/swaps2/available-users/${supervisionId}`);
}

export function createSwap(mySupervisionId: number, targetUserId: number, message?: string) {
  return post("/swaps2", {
    my_supervision_id: mySupervisionId,
    target_user_id: targetUserId,
    message,
  });
}

export function respondSwap(swapId: number, accept: boolean, reason?: string) {
  return post(`/swaps2/${swapId}/respond`, { accept, reason });
}

export function cancelSwap(swapId: number) {
  return del(`/swaps2/${swapId}`);
}

