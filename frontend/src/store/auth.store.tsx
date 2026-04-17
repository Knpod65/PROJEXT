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
import type { RoleSelectionValue, UserMe, UserRole } from "@/types/api";
import { getActiveRole, getAvailableRoles, storePendingRole } from "@/utils/roles";
import { useUi } from "./ui.store";

interface AuthContextValue {
  user: UserMe | null;
  loading: boolean;
  initialized: boolean;
  activeRole: UserRole | null;
  availableRoles: UserRole[];
  signIn: (username: string, password: string, selectedRole: RoleSelectionValue) => Promise<UserMe>;
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
    storePendingRole(null);
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
    async (username: string, password: string, selectedRole: RoleSelectionValue) => {
      const response = await login(username, password, selectedRole);
      setUser(response.user);
      storePendingRole(null);
      setInitialized(true);
      setLoading(false);
      toast("Signed in successfully.", "success");
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
      toast("Signed out.", "info");
    }
  }, [clearSession, toast]);

  const switchViewAs = useCallback(
    async (role: UserRole | null) => {
      await setViewAs(role);
      await refreshUser();
      toast(role ? `Previewing as ${role}.` : "Returned to the default admin preview.", "info");
    },
    [refreshUser, toast],
  );

  useEffect(() => {
    void refreshUser();
  }, [refreshUser]);

  useEffect(() => {
    const handleUnauthorized = () => {
      clearSession();
      toast("Your session expired. Please sign in again.", "warning");
    };

    window.addEventListener("ems:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("ems:unauthorized", handleUnauthorized);
  }, [clearSession, toast]);

  const availableRoles = useMemo(() => getAvailableRoles(user), [user]);
  const activeRole = useMemo(() => getActiveRole(user), [user]);

  const value = useMemo(
    () => ({
      user,
      loading,
      initialized,
      activeRole,
      availableRoles,
      signIn,
      signOut,
      refreshUser,
      switchViewAs,
      clearSession,
    }),
    [activeRole, availableRoles, clearSession, initialized, loading, refreshUser, signIn, signOut, switchViewAs, user],
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
