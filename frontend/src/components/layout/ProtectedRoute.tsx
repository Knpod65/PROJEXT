import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "@/store/auth.store";
import { Skeleton } from "../ui/Skeleton";

export function ProtectedRoute() {
  const { initialized, loading, user } = useAuth();
  const location = useLocation();

  if (loading || !initialized) {
    return (
      <div className="page-loading">
        <Skeleton className="page-loading__hero" />
        <Skeleton className="page-loading__line" />
        <Skeleton className="page-loading__line" />
      </div>
    );
  }

  if (!user) {
    return <Navigate replace to="/login" state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}
