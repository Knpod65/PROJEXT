import { useCallback, useState } from "react";

import {
  cancelSwap,
  createSwap,
  getMySupervisions,
  getMySwaps,
  getWaitingSwaps,
  respondSwap,
  type MySupervisionSlot,
} from "@/services/swap.service";
import type { SwapItem } from "@/types/api";

export type SwapsTab = "mine" | "incoming" | "history";

interface SwapsLiveState {
  mine: SwapItem[];
  incoming: SwapItem[];
  loading: boolean;
  error: string | null;
}

export function useSwapsLive() {
  const [state, setState] = useState<SwapsLiveState>({
    mine: [],
    incoming: [],
    loading: false,
    error: null,
  });
  const [tab, setTab] = useState<SwapsTab>("mine");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const [mine, incoming] = await Promise.all([getMySwaps(), getWaitingSwaps()]);
      setState({ mine, incoming, loading: false, error: null });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Could not load swaps.";
      setState((s) => ({ ...s, loading: false, error: message }));
    }
  }, []);

  const doCancel = useCallback(
    async (swapId: number) => {
      setBusy(true);
      try {
        await cancelSwap(swapId);
        await load();
      } finally {
        setBusy(false);
      }
    },
    [load],
  );

  const doRespond = useCallback(
    async (swapId: number, accept: boolean, reason?: string) => {
      setBusy(true);
      try {
        await respondSwap(swapId, accept, reason);
        await load();
      } finally {
        setBusy(false);
      }
    },
    [load],
  );

  const doCreate = useCallback(
    async (supervisionId: number, targetUserId: number, message?: string) => {
      setBusy(true);
      try {
        await createSwap(supervisionId, targetUserId, message);
        await load();
      } finally {
        setBusy(false);
      }
    },
    [load],
  );

  const loadMySupervisions = useCallback(async (): Promise<MySupervisionSlot[]> => {
    return getMySupervisions();
  }, []);

  // Derived views
  const history = state.mine.filter(
    (s) => s.status !== "pending",
  );

  const pendingMine = state.mine.filter((s) => s.status === "pending" && s.is_requester);

  const stats = {
    pendingMine: pendingMine.length,
    incomingCount: state.incoming.length,
    historyCount: history.length,
    totalMine: state.mine.length,
  };

  return {
    tab,
    setTab,
    mine: state.mine,
    incoming: state.incoming,
    history,
    pendingMine,
    stats,
    loading: state.loading,
    error: state.error,
    busy,
    load,
    doCancel,
    doRespond,
    doCreate,
    loadMySupervisions,
  };
}
