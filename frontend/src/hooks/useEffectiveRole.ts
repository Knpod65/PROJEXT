import { getEffectiveRole } from "@/utils/roles";
import { useAuth } from "@/store/auth.store";
import type { UserRole } from "@/types/api";

/**
 * A convenient hook to get the current user's effective role,
 * handling admin impersonation and fallback logic consistently.
 */
export function useEffectiveRole(): UserRole | null {
  const { user } = useAuth();
  return getEffectiveRole(user);
}
