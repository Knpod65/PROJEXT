import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { useI18n } from "@/i18n";
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

const AUTH_BOOTSTRAP_HINT_KEY = "ems.auth_hint";
const PUBLIC_BOOTSTRAP_PATHS = new Set(["/", "/role-selection", "/login", "/student-search"]);

function getAuthBootstrapHint() {
  if (typeof window === "undefined") {
    return false;
  }

  return window.localStorage.getItem(AUTH_BOOTSTRAP_HINT_KEY) === "1";
}

function setAuthBootstrapHint(enabled: boolean) {
  if (typeof window === "undefined") {
    return;
  }

  if (enabled) {
    window.localStorage.setItem(AUTH_BOOTSTRAP_HINT_KEY, "1");
    return;
  }

  window.localStorage.removeItem(AUTH_BOOTSTRAP_HINT_KEY);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const { t } = useI18n();
  const { toast } = useUi();
  const [user, setUser] = useState<UserMe | null>(null);
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);

  const clearSession = useCallback(() => {
    setUser(null);
    setAuthBootstrapHint(false);
    storePendingRole(null);
    setLoading(false);
    setInitialized(true);
  }, []);

  const refreshUser = useCallback(async () => {
    setLoading(true);
    try {
      const currentUser = await me();
      if (currentUser) {
        setUser(currentUser);
        setAuthBootstrapHint(true);
        storePendingRole(null);
      } else {
        setUser(null);
        setAuthBootstrapHint(false);
        storePendingRole(null);
      }
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
      setAuthBootstrapHint(true);
      storePendingRole(null);
      setInitialized(true);
      setLoading(false);
      toast(t("errors.signedInSuccess"), "success");
      return response.user;
    },
    [t, toast],
  );

  const signOut = useCallback(async () => {
    try {
      await logout({ notifyOnUnauthorized: false });
    } catch {
      // Ignore logout errors and clear local session anyway.
    } finally {
      clearSession();
      toast(t("errors.signedOut"), "info");
    }
  }, [clearSession, t, toast]);

  const switchViewAs = useCallback(
    async (role: UserRole | null) => {
      await setViewAs(role);
      await refreshUser();
      toast(role ? t("settings.viewAsSwitched", { role }) : t("settings.viewAsReset"), "info");
    },
    [refreshUser, t, toast],
  );

  useEffect(() => {
    if (typeof window !== "undefined") {
      const currentPath = window.location.pathname;
      if (PUBLIC_BOOTSTRAP_PATHS.has(currentPath) && !getAuthBootstrapHint()) {
        setUser(null);
        setLoading(false);
        setInitialized(true);
        return;
      }
    }

    void refreshUser();
  }, [refreshUser]);

  useEffect(() => {
    const handleUnauthorized = () => {
      clearSession();
      toast(t("errors.sessionExpired"), "warning");
    };

    window.addEventListener("ems:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("ems:unauthorized", handleUnauthorized);
  }, [clearSession, t, toast]);

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
