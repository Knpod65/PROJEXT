import { useAuth } from "@/store/auth.store";
import { getEffectiveRole } from "@/utils/roles";

export function useEffectiveRole() {
  const { user } = useAuth();
  return getEffectiveRole(user);
}
