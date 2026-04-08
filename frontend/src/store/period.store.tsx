import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { getActivePeriod } from "@/services/period.service";
import type { PeriodItem } from "@/types/api";
import { useAuth } from "./auth.store";

interface PeriodContextValue {
  activePeriod: PeriodItem | null;
  loading: boolean;
  refreshPeriod: () => Promise<void>;
}

const PeriodContext = createContext<PeriodContextValue | undefined>(undefined);

export function PeriodProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [activePeriod, setActivePeriod] = useState<PeriodItem | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshPeriod = useCallback(async () => {
    if (!user) {
      setActivePeriod(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const period = await getActivePeriod();
      setActivePeriod(period);
    } catch {
      setActivePeriod(null);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    refreshPeriod();
  }, [refreshPeriod]);

  const value = useMemo(
    () => ({
      activePeriod,
      loading,
      refreshPeriod,
    }),
    [activePeriod, loading, refreshPeriod],
  );

  return <PeriodContext.Provider value={value}>{children}</PeriodContext.Provider>;
}

export function usePeriod() {
  const context = useContext(PeriodContext);
  if (!context) {
    throw new Error("usePeriod must be used inside PeriodProvider");
  }
  return context;
}
