import type { ReactNode } from "react";
import { Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { ErrorBoundary } from "@/components/layout/ErrorBoundary";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { ToastViewport } from "@/components/ui/Toast";
import { getPageConfig } from "@/config/navigation";
import { PeriodProvider } from "@/store/period.store";
import { useAuth } from "@/store/auth.store";
import type { UserRole } from "@/types/api";
import { getDefaultRoute, getPublicEntryRoute, hasRole } from "@/utils/roles";

import { CheckinsPage } from "@/pages/Checkins";
import { CoExamPage } from "@/pages/CoExam";
import { CopyPage } from "@/pages/Copy";
import { DashboardPage } from "@/pages/Dashboard";
import { ExamManagerPage } from "@/pages/ExamManager";
import { ExternalPage } from "@/pages/External";
import { ImportPage } from "@/pages/Import";
import { LoginPage } from "@/pages/Login";
import { MyExamPage } from "@/pages/MyExam";
import { OptimizerPage } from "@/pages/Optimizer";
import { PeriodPage } from "@/pages/Period";
import { PrintQueuePage } from "@/pages/PrintQueue";
import { PrintReviewPage } from "@/pages/PrintReview";
import { RoleSelectionPage } from "@/pages/RoleSelection";
import { RoomAttendancePage } from "@/pages/RoomAttendance";
import { RoomManagementV2Page } from "@/pages/RoomManagementV2";
import { SchedulePage } from "@/pages/Schedule";
import { SectionsPage } from "@/pages/Sections";
import { SettingsPage } from "@/pages/Settings";
import { SettingsV2Page } from "@/pages/SettingsV2";
import { StudentsV2Page } from "@/pages/StudentsV2";
import { StudentSearchPage } from "@/pages/StudentSearch";
import { SubmissionsPage } from "@/pages/Submissions";
import { SwapsPage } from "@/pages/Swaps";
import { SwapsV2Page } from "@/pages/SwapsV2";
import { UsersPage } from "@/pages/Users";
import { UsersV2Page } from "@/pages/UsersV2";
import { WorkflowPage } from "@/pages/Workflow";
import { WorkflowV2Page } from "@/pages/WorkflowV2";
import { VenueManagementV2Page } from "@/pages/VenueManagementV2";

interface GuardedPageProps {
  roles?: UserRole[];
  allowBaseAdminPreview?: boolean;
  children: ReactNode;
}

function GuardedPage({ children, roles, allowBaseAdminPreview }: GuardedPageProps) {
  const { user } = useAuth();

  if (!hasRole(user, roles, { allowBaseAdminPreview })) {
    return <EmptyState icon={<Icon name="shield" />} title="You do not have access to this page." />;
  }

  return <>{children}</>;
}

function ProtectedAppLayout() {
  const location = useLocation();
  const page = getPageConfig(location.pathname);

  return (
    <PeriodProvider>
      <AppShell page={page} title={page?.title ?? "EMS Control Center"}>
        <ErrorBoundary>
          <Outlet />
        </ErrorBoundary>
      </AppShell>
    </PeriodProvider>
  );
}

function StudentSearchRoute() {
  const { initialized, loading, user } = useAuth();

  if (loading || !initialized) {
    return null;
  }

  if (!user) {
    return <StudentSearchPage />;
  }

  return (
    <PeriodProvider>
      <AppShell title="Student Search">
        <StudentSearchPage />
      </AppShell>
    </PeriodProvider>
  );
}

function HomeRedirect() {
  const { initialized, loading, user } = useAuth();

  if (loading || !initialized) {
    return null;
  }

  return <Navigate replace to={user ? getDefaultRoute(user) : getPublicEntryRoute()} />;
}

function NotFoundPage() {
  const { user } = useAuth();

  if (!user) {
    return <Navigate replace to={getPublicEntryRoute()} />;
  }

  return (
    <PeriodProvider>
      <AppShell title="Page not found">
        <EmptyState
          icon={<Icon name="search_off" />}
          title="We could not find that page."
          description="Try the main navigation or go back to the dashboard."
        />
      </AppShell>
    </PeriodProvider>
  );
}

export function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<HomeRedirect />} />
        <Route path="/role-selection" element={<RoleSelectionPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/student-search" element={<StudentSearchRoute />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<ProtectedAppLayout />}>
            <Route path="/dashboard" element={<GuardedPage roles={["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher"]}><DashboardPage /></GuardedPage>} />
            <Route path="/schedule" element={<GuardedPage roles={["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher"]}><SchedulePage /></GuardedPage>} />
            <Route path="/submissions" element={<GuardedPage roles={["admin", "esq_head", "secretary", "dept_supervisor", "teacher"]}><SubmissionsPage /></GuardedPage>} />
            <Route path="/attendance" element={<GuardedPage roles={["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher"]}><RoomAttendancePage /></GuardedPage>} />
            <Route path="/checkins" element={<GuardedPage roles={["admin", "dept_supervisor", "staff", "teacher"]}><CheckinsPage /></GuardedPage>} />
            <Route path="/swaps" element={<GuardedPage roles={["admin", "dept_supervisor", "staff", "teacher"]}><SwapsPage /></GuardedPage>} />
            <Route path="/swaps-v2" element={<GuardedPage roles={["admin"]}><SwapsV2Page /></GuardedPage>} />
            <Route path="/sections" element={<GuardedPage roles={["admin", "esq_head", "secretary", "staff", "teacher"]}><SectionsPage /></GuardedPage>} />
            <Route path="/copy" element={<GuardedPage roles={["admin", "staff"]}><CopyPage /></GuardedPage>} />
            <Route path="/print-queue" element={<GuardedPage roles={["print_shop"]}><PrintQueuePage /></GuardedPage>} />
            <Route path="/workflow" element={<GuardedPage roles={["admin", "esq_head", "secretary"]}><WorkflowPage /></GuardedPage>} />
            <Route path="/workflow-v2" element={<GuardedPage roles={["admin"]}><WorkflowV2Page /></GuardedPage>} />
            <Route path="/coexam" element={<GuardedPage roles={["admin"]}><CoExamPage /></GuardedPage>} />
            <Route path="/optimizer" element={<GuardedPage roles={["admin"]}><OptimizerPage /></GuardedPage>} />
            <Route path="/printreview" element={<GuardedPage roles={["admin"]}><PrintReviewPage /></GuardedPage>} />
            <Route path="/external" element={<GuardedPage roles={["admin"]}><ExternalPage /></GuardedPage>} />
            <Route path="/import" element={<GuardedPage roles={["admin"]}><ImportPage /></GuardedPage>} />
            <Route path="/period" element={<GuardedPage roles={["admin"]}><PeriodPage /></GuardedPage>} />
            <Route path="/settings" element={<GuardedPage roles={["admin"]} allowBaseAdminPreview><SettingsPage /></GuardedPage>} />
            <Route path="/settings-v2" element={<GuardedPage roles={["admin"]} allowBaseAdminPreview><SettingsV2Page /></GuardedPage>} />
            <Route path="/rooms-v2" element={<GuardedPage roles={["admin"]}><RoomManagementV2Page /></GuardedPage>} />
            <Route path="/venues-v2" element={<GuardedPage roles={["admin"]}><VenueManagementV2Page /></GuardedPage>} />
            <Route path="/students-v2" element={<GuardedPage roles={["admin"]}><StudentsV2Page /></GuardedPage>} />
            <Route path="/users" element={<GuardedPage roles={["admin"]}><UsersPage /></GuardedPage>} />
            <Route path="/users-v2" element={<GuardedPage roles={["admin"]}><UsersV2Page /></GuardedPage>} />
            <Route path="/myexam" element={<GuardedPage roles={["teacher"]}><MyExamPage /></GuardedPage>} />
            <Route path="/exammanager" element={<GuardedPage roles={["admin"]}><ExamManagerPage /></GuardedPage>} />
          </Route>
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
      <ToastViewport />
    </>
  );
}
