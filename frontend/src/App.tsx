import type { ReactNode } from "react";
import { Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { EmptyState } from "@/components/ui/EmptyState";
import { ToastViewport } from "@/components/ui/Toast";
import { getPageConfig } from "@/config/navigation";
import { PeriodProvider } from "@/store/period.store";
import { useAuth } from "@/store/auth.store";
import type { UserRole } from "@/types/api";
import { getDefaultRoute, hasRole } from "@/utils/roles";

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
import { PrintReviewPage } from "@/pages/PrintReview";
import { SchedulePage } from "@/pages/Schedule";
import { SectionsPage } from "@/pages/Sections";
import { SettingsPage } from "@/pages/Settings";
import { StudentSearchPage } from "@/pages/StudentSearch";
import { SubmissionsPage } from "@/pages/Submissions";
import { SwapsPage } from "@/pages/Swaps";
import { UsersPage } from "@/pages/Users";
import { WorkflowPage } from "@/pages/Workflow";

interface GuardedPageProps {
  roles?: UserRole[];
  children: ReactNode;
}

function GuardedPage({ children, roles }: GuardedPageProps) {
  const { user } = useAuth();

  if (!hasRole(user, roles)) {
    return <EmptyState icon="🔒" title="คุณไม่มีสิทธิ์เข้าถึงหน้านี้" />;
  }

  return <>{children}</>;
}

function ProtectedAppLayout() {
  const location = useLocation();
  const page = getPageConfig(location.pathname);

  return (
    <PeriodProvider>
      <AppShell title={page?.title ?? "EMS"}>
        <Outlet />
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
      <AppShell title="ค้นหาตารางสอบ">
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

  return <Navigate replace to={getDefaultRoute(user)} />;
}

function NotFoundPage() {
  const { user } = useAuth();

  if (!user) {
    return <Navigate replace to="/login" />;
  }

  return (
    <PeriodProvider>
      <AppShell title="ไม่พบหน้า">
        <EmptyState icon="🧭" title="ไม่พบหน้าที่ต้องการ" description="ลองตรวจสอบ URL หรือกลับไปยังเมนูหลัก" />
      </AppShell>
    </PeriodProvider>
  );
}

export function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<HomeRedirect />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/student-search" element={<StudentSearchRoute />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<ProtectedAppLayout />}>
            <Route path="/dashboard" element={<GuardedPage roles={["admin", "esq_head", "secretary", "dept_supervisor", "staff"]}><DashboardPage /></GuardedPage>} />
            <Route path="/schedule" element={<GuardedPage roles={["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher"]}><SchedulePage /></GuardedPage>} />
            <Route path="/submissions" element={<GuardedPage roles={["admin", "esq_head", "secretary", "dept_supervisor", "teacher"]}><SubmissionsPage /></GuardedPage>} />
            <Route path="/swaps" element={<GuardedPage roles={["admin", "dept_supervisor", "staff", "teacher"]}><SwapsPage /></GuardedPage>} />
            <Route path="/checkins" element={<GuardedPage roles={["admin", "dept_supervisor", "staff", "teacher"]}><CheckinsPage /></GuardedPage>} />
            <Route path="/sections" element={<GuardedPage roles={["admin", "esq_head", "secretary", "staff", "teacher"]}><SectionsPage /></GuardedPage>} />
            <Route path="/copy" element={<GuardedPage roles={["admin", "staff"]}><CopyPage /></GuardedPage>} />
            <Route path="/workflow" element={<GuardedPage roles={["admin", "esq_head", "secretary"]}><WorkflowPage /></GuardedPage>} />
            <Route path="/coexam" element={<GuardedPage roles={["admin"]}><CoExamPage /></GuardedPage>} />
            <Route path="/optimizer" element={<GuardedPage roles={["admin"]}><OptimizerPage /></GuardedPage>} />
            <Route path="/printreview" element={<GuardedPage roles={["admin"]}><PrintReviewPage /></GuardedPage>} />
            <Route path="/external" element={<GuardedPage roles={["admin"]}><ExternalPage /></GuardedPage>} />
            <Route path="/import" element={<GuardedPage roles={["admin"]}><ImportPage /></GuardedPage>} />
            <Route path="/period" element={<GuardedPage roles={["admin"]}><PeriodPage /></GuardedPage>} />
            <Route path="/settings" element={<GuardedPage roles={["admin"]}><SettingsPage /></GuardedPage>} />
            <Route path="/users" element={<GuardedPage roles={["admin"]}><UsersPage /></GuardedPage>} />
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
