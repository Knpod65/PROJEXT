import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "@/store/auth.store";
import { getPublicEntryRoute } from "@/utils/roles";
import { PageSkeleton } from "../ui/PageSkeleton";

export function ProtectedRoute() {
  const { initialized, loading, user } = useAuth();
  const location = useLocation();

  if (loading || !initialized) {
    return <PageSkeleton />;
  }

  if (!user) {
    return (
      <Navigate
        replace
        to={getPublicEntryRoute()}
        state={{ from: `${location.pathname}${location.search}${location.hash}` }}
      />
    );
  }

  return <Outlet />;
}
