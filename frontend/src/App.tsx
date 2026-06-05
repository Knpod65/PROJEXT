import type { ReactNode } from "react";
import { lazy, Suspense } from "react";
import { Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { ErrorBoundary } from "@/components/layout/ErrorBoundary";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { ToastViewport } from "@/components/ui/Toast";
import { getPageConfig } from "@/config/navigation";
import { useI18n } from "@/i18n";
import { CheckinsPage } from "@/pages/Checkins";
import { CoExamPage } from "@/pages/CoExam";
import { CopyPage } from "@/pages/Copy";
import { DashboardPage } from "@/pages/Dashboard";
import { ExamManagerPage } from "@/pages/ExamManager";
import { ExportCenterPage } from "@/pages/ExportCenter";
import { ExternalPage } from "@/pages/External";
import { HistoricalSchedulesPage } from "@/pages/HistoricalSchedules";
import { ImportAuditPage } from "@/pages/ImportAudit";
import { ImportV2Page } from "@/pages/ImportV2";
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
import { SettingsV2Page } from "@/pages/SettingsV2";
import { StaffAvailabilityPage } from "@/pages/StaffAvailability";
import { StudentSearchPage } from "@/pages/StudentSearch";
import { StudentsV2Page } from "@/pages/StudentsV2";
import { SubmissionsPage } from "@/pages/Submissions";
import { SwapsV2Page } from "@/pages/SwapsV2";
import { UsersV2Page } from "@/pages/UsersV2";
import { VenueManagementV2Page } from "@/pages/VenueManagementV2";
import { WorkflowV2Page } from "@/pages/WorkflowV2";
import { useAuth } from "@/store/auth.store";
import { PeriodProvider } from "@/store/period.store";
import type { UserRole } from "@/types/api";
import { getDefaultRoute, getPublicEntryRoute, hasRole } from "@/utils/roles";

const AdminIntelligenceDashboard = lazy(() => import("@/pages/AdminIntelligenceDashboard"));
const ExecutiveAnalytics = lazy(() => import("@/pages/ExecutiveAnalytics"));
const GovernanceCockpitPage = lazy(() =>
  import("@/pages/GovernanceCockpit").then((module) => ({ default: module.GovernanceCockpitPage })),
);
const OptimizerTraceExplorerPage = lazy(() => import("@/pages/OptimizationTraceExplorer"));
const PlatformConfigurationPage = lazy(() => import("@/pages/PlatformConfiguration"));
const OperationalHealthPage = lazy(() => import("@/pages/OperationalHealth"));
const AuditExplorerPage = lazy(() => import("@/pages/AuditExplorer"));
const WorkloadDutyAnalytics = lazy(() => import("@/pages/WorkloadDutyAnalytics"));
const AdvanceInvigilationBatchPreview = lazy(() => import("@/pages/AdvanceInvigilationBatchPreview"));
const InvigilationRateRules = lazy(() => import("@/pages/InvigilationRateRules"));
const OfficialPaymentDocumentDraft = lazy(() => import("@/pages/OfficialPaymentDocumentDraft"));

interface GuardedPageProps {
  roles?: UserRole[];
  allowBaseAdminPreview?: boolean;
  children: ReactNode;
}

function GuardedPage({ children, roles, allowBaseAdminPreview }: GuardedPageProps) {
  const { t } = useI18n();
  const { user } = useAuth();

  if (!hasRole(user, roles, { allowBaseAdminPreview })) {
    return <EmptyState icon={<Icon name="shield" />} title={t("app.unauthorized.title")} />;
  }

  return <>{children}</>;
}

function ProtectedAppLayout() {
  const { t } = useI18n();
  const location = useLocation();
  const page = getPageConfig(location.pathname);

  return (
    <PeriodProvider>
      <AppShell page={page} title={page?.title ?? t("app.shell.controlCenter")}>
        <ErrorBoundary>
          <Suspense fallback={<div className="p-8 text-center text-sm text-gray-500">Loading dashboard...</div>}>
            <Outlet />
          </Suspense>
        </ErrorBoundary>
      </AppShell>
    </PeriodProvider>
  );
}

function StudentSearchRoute() {
  const { t } = useI18n();
  const { initialized, loading, user } = useAuth();

  if (loading || !initialized) {
    return null;
  }

  if (!user) {
    return <StudentSearchPage />;
  }

  return (
    <PeriodProvider>
      <AppShell title={t("app.studentSearchTitle")}>
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
  const { t } = useI18n();
  const { user } = useAuth();

  if (!user) {
    return <Navigate replace to={getPublicEntryRoute()} />;
  }

  return (
    <PeriodProvider>
      <AppShell title={t("app.notFound.title")}>
        <EmptyState
          icon={<Icon name="search_off" />}
          title={t("app.notFound.heading")}
          description={t("app.notFound.description")}
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
            <Route
              path="/dashboard"
              element={
                <GuardedPage roles={["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher"]}>
                  <DashboardPage />
                </GuardedPage>
              }
            />
            <Route
              path="/admin-intelligence-dashboard"
              element={
                <GuardedPage roles={["admin"]}>
                  <AdminIntelligenceDashboard />
                </GuardedPage>
              }
            />
            <Route
              path="/schedule"
              element={
                <GuardedPage roles={["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher"]}>
                  <SchedulePage />
                </GuardedPage>
              }
            />
            <Route
              path="/analytics"
              element={
                <GuardedPage roles={["admin", "esq_head", "secretary"]}>
                  <ExecutiveAnalytics />
                </GuardedPage>
              }
            />
            <Route
              path="/workload-duty-analytics"
              element={
                <GuardedPage roles={["admin"]}>
                  <WorkloadDutyAnalytics />
                </GuardedPage>
              }
            />
            <Route
              path="/duty-workload"
              element={
                <GuardedPage roles={["staff", "dept_supervisor", "esq_head", "secretary"]}>
                  <WorkloadDutyAnalytics />
                </GuardedPage>
              }
            />
            <Route
              path="/my-workload"
              element={
                <GuardedPage roles={["teacher"]}>
                  <WorkloadDutyAnalytics />
                </GuardedPage>
              }
            />
            <Route
              path="/governance"
              element={
                <GuardedPage roles={["admin", "esq_head", "secretary"]}>
                  <GovernanceCockpitPage />
                </GuardedPage>
              }
            />
            <Route
              path="/submissions"
              element={
                <GuardedPage roles={["admin", "esq_head", "secretary", "dept_supervisor", "teacher"]}>
                  <SubmissionsPage />
                </GuardedPage>
              }
            />
            <Route
              path="/attendance"
              element={
                <GuardedPage roles={["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher"]}>
                  <RoomAttendancePage />
                </GuardedPage>
              }
            />
            <Route
              path="/checkins"
              element={
                <GuardedPage roles={["admin", "dept_supervisor", "staff", "teacher"]}>
                  <CheckinsPage />
                </GuardedPage>
              }
            />
            <Route
              path="/swaps"
              element={
                <GuardedPage roles={["admin", "dept_supervisor", "staff", "teacher"]}>
                  <SwapsV2Page />
                </GuardedPage>
              }
            />
            <Route path="/swaps-v2" element={<Navigate replace to="/swaps" />} />
            <Route
              path="/sections"
              element={
                <GuardedPage roles={["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher"]}>
                  <SectionsPage />
                </GuardedPage>
              }
            />
            <Route
              path="/copy"
              element={
                <GuardedPage roles={["admin", "staff"]}>
                  <CopyPage />
                </GuardedPage>
              }
            />
            <Route
              path="/print-queue"
              element={
                <GuardedPage roles={["print_shop"]}>
                  <PrintQueuePage />
                </GuardedPage>
              }
            />
            <Route
              path="/workflow"
              element={
                <GuardedPage roles={["admin", "esq_head", "secretary"]}>
                  <WorkflowV2Page />
                </GuardedPage>
              }
            />
            <Route path="/workflow-v2" element={<Navigate replace to="/workflow" />} />
            <Route
              path="/coexam"
              element={
                <GuardedPage roles={["admin"]}>
                  <CoExamPage />
                </GuardedPage>
              }
            />
            <Route
              path="/optimizer"
              element={
                <GuardedPage roles={["admin"]}>
                  <OptimizerPage />
                </GuardedPage>
              }
            />
            <Route
              path="/optimizer-trace"
              element={
                <GuardedPage roles={["admin"]}>
                  <OptimizerTraceExplorerPage />
                </GuardedPage>
              }
            />
            <Route
              path="/staff-availability"
              element={
                <GuardedPage roles={["admin"]}>
                  <StaffAvailabilityPage />
                </GuardedPage>
              }
            />
            <Route
              path="/printreview"
              element={
                <GuardedPage roles={["admin", "esq_head", "secretary"]}>
                  <PrintReviewPage />
                </GuardedPage>
              }
            />
            <Route
              path="/external"
              element={
                <GuardedPage roles={["admin", "staff"]}>
                  <ExternalPage />
                </GuardedPage>
              }
            />
            <Route
              path="/exports-center"
              element={
                <GuardedPage roles={["admin", "staff"]}>
                  <ExportCenterPage />
                </GuardedPage>
              }
            />
            <Route
              path="/invigilation-advance-batch-preview"
              element={
                <GuardedPage roles={["admin", "staff"]}>
                  <AdvanceInvigilationBatchPreview />
                </GuardedPage>
              }
            />
            <Route
              path="/invigilation-rate-rules"
              element={
                <GuardedPage roles={["admin", "staff"]}>
                  <InvigilationRateRules />
                </GuardedPage>
              }
            />
            <Route
              path="/invigilation-payment-document-draft"
              element={
                <GuardedPage roles={["admin", "staff"]}>
                  <OfficialPaymentDocumentDraft />
                </GuardedPage>
              }
            />
            <Route
              path="/historical-schedules"
              element={
                <GuardedPage roles={["admin"]}>
                  <HistoricalSchedulesPage />
                </GuardedPage>
              }
            />
            <Route
              path="/import"
              element={
                <GuardedPage roles={["admin"]}>
                  <ImportV2Page />
                </GuardedPage>
              }
            />
            <Route
              path="/import-audit"
              element={
                <GuardedPage roles={["admin"]}>
                  <ImportAuditPage />
                </GuardedPage>
              }
            />
            <Route
              path="/period"
              element={
                <GuardedPage roles={["admin"]}>
                  <PeriodPage />
                </GuardedPage>
              }
            />
            <Route
              path="/settings"
              element={
                <GuardedPage roles={["admin"]} allowBaseAdminPreview>
                  <SettingsV2Page />
                </GuardedPage>
              }
            />
            <Route path="/settings-v2" element={<Navigate replace to="/settings" />} />
            <Route
              path="/platform-config"
              element={
                <GuardedPage roles={["admin"]}>
                  <PlatformConfigurationPage />
                </GuardedPage>
              }
            />
            <Route
              path="/operational-health"
              element={
                <GuardedPage roles={["admin", "esq_head"]}>
                  <OperationalHealthPage />
                </GuardedPage>
              }
            />
            <Route
              path="/audit-explorer"
              element={
                <GuardedPage roles={["admin", "esq_head"]}>
                  <AuditExplorerPage />
                </GuardedPage>
              }
            />
            <Route
              path="/rooms-v2"
              element={
                <GuardedPage roles={["admin"]}>
                  <RoomManagementV2Page />
                </GuardedPage>
              }
            />
            <Route
              path="/venues-v2"
              element={
                <GuardedPage roles={["admin"]}>
                  <VenueManagementV2Page />
                </GuardedPage>
              }
            />
            <Route
              path="/students-v2"
              element={
                <GuardedPage roles={["admin"]}>
                  <StudentsV2Page />
                </GuardedPage>
              }
            />
            <Route
              path="/users"
              element={
                <GuardedPage roles={["admin"]}>
                  <UsersV2Page />
                </GuardedPage>
              }
            />
            <Route path="/users-v2" element={<Navigate replace to="/users" />} />
            <Route
              path="/myexam"
              element={
                <GuardedPage roles={["teacher"]}>
                  <MyExamPage />
                </GuardedPage>
              }
            />
            <Route
              path="/exammanager"
              element={
                <GuardedPage roles={["admin", "dept_supervisor"]}>
                  <ExamManagerPage />
                </GuardedPage>
              }
            />
          </Route>
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
      <ToastViewport />
    </>
  );
}
