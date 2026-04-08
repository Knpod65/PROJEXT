import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { login, logout, me, setViewAs } from "@/services/auth.service";
import type { UserMe, UserRole } from "@/types/api";
import { useUi } from "./ui.store";

interface AuthContextValue {
  user: UserMe | null;
  loading: boolean;
  initialized: boolean;
  signIn: (username: string, password: string) => Promise<UserMe>;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
  switchViewAs: (role: UserRole | null) => Promise<void>;
  clearSession: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { toast } = useUi();
  const [user, setUser] = useState<UserMe | null>(null);
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);

  const clearSession = useCallback(() => {
    setUser(null);
    setLoading(false);
    setInitialized(true);
  }, []);

  const refreshUser = useCallback(async () => {
    setLoading(true);
    try {
      const currentUser = await me();
      setUser(currentUser);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
      setInitialized(true);
    }
  }, []);

  const signIn = useCallback(
    async (username: string, password: string) => {
      const response = await login(username, password);
      setUser(response.user);
      setInitialized(true);
      setLoading(false);
      toast("เข้าสู่ระบบเรียบร้อย", "success");
      return response.user;
    },
    [toast],
  );

  const signOut = useCallback(async () => {
    try {
      await logout();
    } catch {
      // Ignore logout errors and clear local session anyway.
    } finally {
      clearSession();
      toast("ออกจากระบบแล้ว", "info");
    }
  }, [clearSession, toast]);

  const switchViewAs = useCallback(
    async (role: UserRole | null) => {
      await setViewAs(role);
      await refreshUser();
      toast(role ? `สลับมุมมองเป็น ${role}` : "กลับสู่มุมมองของตัวเอง", "info");
    },
    [refreshUser, toast],
  );

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  useEffect(() => {
    const handleUnauthorized = () => {
      clearSession();
      toast("เซสชันหมดอายุ กรุณาเข้าสู่ระบบใหม่", "warning");
    };

    window.addEventListener("ems:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("ems:unauthorized", handleUnauthorized);
  }, [clearSession, toast]);

  const value = useMemo(
    () => ({
      user,
      loading,
      initialized,
      signIn,
      signOut,
      refreshUser,
      switchViewAs,
      clearSession,
    }),
    [clearSession, initialized, loading, refreshUser, signIn, signOut, switchViewAs, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
